# import necessary libraries
import pandas as pd
import numpy as np
import regex as re
import datetime as dt
from abc import (
    ABC,
    abstractmethod
) 
from typing import List

"""
This code belongs to César Loubet (GitHub user: cesl11) and the only person or company allowed to use it and modify it is AiMexa (https://aimexa.tech/).
    - If you want to use this code as inspiration, or you find it useful and want to implement it in your own projects, please contact me:
        MAIL: cesarloubet2003@gmail.com
        LINKEDIN: César Loubet
    Cheers :)
"""


# abstract Cleaner class -- base of all further cleaners 
class Cleaner(ABC):
    @abstractmethod
    def clean(self, df:pd.DataFrame) -> pd.DataFrame:
        pass

# ------ Cleaners ------ #
class PriceCleaner(Cleaner):
    def clean(self, df:pd.DataFrame) -> pd.DataFrame:
        
        # a function to extract from price column the type exchange of the listing
        def extract_currency(value:str) -> str:
            if any(x in value for x in ['MXN', 'MX', 'MX$', 'mx']):
                return 'MXN'
            elif any(x in value for x in ['USD', 'US', 'US$', 'us']):
                return 'USD'
            else:
                return None
        
        # check if the Pandas series given contains only string values and if not, convert to it
        df['price'] = df['price'].astype(str)
        
        # apply the function to create the 'listed_in' column
        df['listed_in'] = df['price'].apply(extract_currency)
        
        # remove non-numeric characters from in price
        df['price'] = df['price'].str.replace(r'[^\d.]', '', regex=True).str.strip()
        
        # convert the clean column to float values, handle errors giving None
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        
        return df


class LocationCleaner(Cleaner):
    def clean(self, df:pd.DataFrame) -> pd.DataFrame:
        
        # a function to extract neighborhood from location values
        def extract_neighborhood(value:str) -> str:
            match = re.search(r'(?:Casa en(?: condominio)?|Departamento en)?\s*(?:en\s)?([A-Za-z\s]+?)(?=,|$)', value)
            return f'{match.group(1).strip()}, La Paz, Baja California Sur, Mexico' if match else 'Unknown, La Paz, Baja California Sur, Mexico'
        
        # divide location column in two
        df['full_location'] = df['location']
        
        # apply extracting function to location column
        df['location'] = df['location'].apply(extract_neighborhood)
        
        return df
    

class AreaCleaner(Cleaner):
    def clean(self, df:pd.DataFrame) -> pd.DataFrame:
        df['area'] = df['area'].str.strip().str.slice(0, -2)
        df['area'] = df['area'].str.replace(r'[^\d.]', '', regex=True).astype(float)
        
        return df


class ParkingsCleaner(Cleaner):
    def clean(self, df:pd.DataFrame) -> pd.DataFrame:
        
        # define a function to purge wrong-extracted parkings info
        def purge_parkings(value:str):
            possible_parkings_identifiers = ['Estacionamiento', 'estacionamiento', 'Parking', 'Parkings', 'parkings', 'parking']
            if any(x in value for x in possible_parkings_identifiers):
                return '1 Estacionamiento' # set 1 parking as default
            else:
                return value

        # apply the function to the column
        df['parkings'] = df['parkings'].apply(purge_parkings)
        
        # replace all non-numeric characters using regex
        df['parkings'] = df['parkings'].str.replace(r'\D', '', regex=True).str.strip()
        
        # convert results in numeric values
        df['parkings'] = pd.to_numeric(df['parkings'], errors='coerce')

        return df        
        

# ------ ADA, THE MAIN CLEANER ------ #
class Ada:
    def __init__(self, columns_to_clean:List[str]):
        cleaners_ = {
            'price':PriceCleaner,
            'location':LocationCleaner,
            'area':AreaCleaner,
            'parkings':ParkingsCleaner
        }
        self.cleaners = [cleaners_[col]() for col in columns_to_clean if col in cleaners_]   
    
    def clean(self, df:pd.DataFrame) -> pd.DataFrame:
        
        # drop duplicated rows if exists
        if df.duplicated().sum() != 0:
            df = df.drop_duplicates()
        
        # implement the 'clean' method of all   
        for cleaner in self.cleaners:
            df = cleaner.clean(df)
            
        df['register_date'] = dt.datetime.now().strftime('%Y-%m-%d %H:%M')
        
        return df
    
    def reorganize(self, df:pd.DataFrame) -> pd.DataFrame:
        df = df[['price', 'listed_in', 'location', 'full_location', 'property_type', 'bedrooms', 'bathrooms', 'area', 'parkings', 'source', 'url', 'register_date']]
        return df
