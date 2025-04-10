# import necessary libraries
import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import regex as re
import datetime as dt
import requests
import json
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

# variables and API's
load_dotenv()
api_key = os.getenv('CURRENCY_API_KEY')

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
                return 'MXN' # set default currency as mexican pesos

        # check if the Pandas series given contains only string values and if not, convert to it
        df['price'] = df['price'].astype(str)

        # apply the function to create the 'listed_in' column
        df['listed_in'] = df['price'].apply(extract_currency)

        # remove non-numeric characters from in price
        df['price'] = df['price'].str.replace(r'[^\d.]', '', regex=True).str.strip()

        # convert the clean column to float values, handle errors giving None
        df['price'] = pd.to_numeric(df['price'], errors='coerce')

        return df

class PriceCurrencyUpdater(Cleaner):
    def clean(self, df:pd.DataFrame) -> pd.DataFrame:
        
        def get_real_time_exchange_rate():
            url = f'https://v6.exchangerate-api.com/v6/{api_key}/latest/USD'
            response = requests.get(url)
                
            if response.status_code == 200:
                data = response.json()
                mxn_rate = data['conversion_rates'].get('MXN')
                if mxn_rate:
                    return mxn_rate
                else:
                    raise ValueError('MXN rate not found')
            else:
                raise Exception(f'API failed. Status code: {response.status_code}')

        mxn_exchange_rate = get_real_time_exchange_rate()
        df['price_in_mxn'] = df[df['listed_in']=='USD']['price'].apply(lambda x: round(x * mxn_exchange_rate, 2))
              
        return df


class LocationCleaner(Cleaner):
    def clean(self, df:pd.DataFrame) -> pd.DataFrame:

        def extract_property_type(value:str) -> str:
            posible_house_denominations = ['Casa en', 'Casa', 'casa en', 'casa']
            posible_condo_denominations = ['condominio', 'Condominio', 'Casa condominio', 'casa condominio', 'Condominio', 'condominio']
            posible_apartments_denominations = ['Departamento en', 'departamento en', 'Departamento', 'departamento', 'Dpto.', 'dpto.', 'Dpto', 'dpto']
            if any(x in value for x in posible_condo_denominations):
                return 'Casa condominio'
            elif any(x in value for x in posible_house_denominations):
                return 'Casa'
            elif any(x in value for x in posible_apartments_denominations):
                return 'Departamento'
            else:
                return 'Casa'

        def drop_property_type(value:str) -> str:
            new_value = re.sub(r'(?:Casa en(?: condominio)?|Departamento en)?', '', value)
            return new_value

        def drop_postal_codes_and_street_numbers(value:str) -> str:
            new_value = re.sub(r'\d', '', value).strip()
            renew_value = re.sub(r'Calle', '', new_value)
            return renew_value.strip()

        def extract_neighborhood(value:str) -> str:
            match = re.search(r'\s*(?:en\s)?([\w\sáéíóúÁÉÍÓÚñÑüÜ]+?)(?=,|$)', value)
            if match:
                    neighborhood = match.group(1).strip()
                    if len(neighborhood) > 1:
                            return f'{neighborhood}, La Paz, Baja California Sur, Mexico'
            return 'Unknown, La Paz, Baja California Sur'


        # make sure location column contains only strings
        df['location'] = df['location'].astype(str)

        # divide location column in two to conserve original listing location
        df['full_location'] = df['location']

        # create a column with the property type exctracted from listed location
        df['property_type'] = df['location'].apply(extract_property_type)

        # apply extracting and cleaning functions to location column
        df['location'] = df['location'].apply(drop_property_type)
        df['location'] = df['location'].apply(drop_postal_codes_and_street_numbers)
        df['location'] = df['location'].apply(extract_neighborhood)

        return df


class BedroomsCleaner(Cleaner):
    def clean(self, df:pd.DataFrame) -> pd.DataFrame:
        df['bedrooms'] = df['bedrooms'].str.replace(r'[^\d.]', '', regex=True).str.strip()
        df['bedrooms'] = df['bedrooms'].astype(float)

        return df

class BathroomsCleaner(Cleaner):
    def clean(self, df:pd.DataFrame) -> pd.DataFrame:
        df['bathrooms'] = df['bathrooms'].str.replace(r'[^\d.]', '', regex=True).str.strip()
        df['bathrooms'] = df['bathrooms'].astype(float)

        return df


class AreaCleaner(Cleaner):
    def clean(self, df:pd.DataFrame) -> pd.DataFrame:
        df['area'] = df['area'].str.strip().str.slice(0, -2)
        df['area'] = df['area'].str.replace(r'[^\d.]', '', regex=True).astype(float)

        return df


class ParkingsCleaner(Cleaner):
    def clean(self, df:pd.DataFrame) -> pd.DataFrame:
        
        def normalize_parkings(value:str) -> str:
            if not isinstance(value,str):
                return '1'
            
            new_value = re.sub(r'(?:Estacionamiento|Parking|estacionamiento|parqueadero|car\s+park)', '1', value, flags=re.IGNORECASE)
            return new_value

        df['parkings'] = df['parkings'].astype(str)

        # replace all non-numeric characters using regex
        df['parkings'] = df['parkings'].apply(normalize_parkings)
        df['parkings'] = df['parkings'].str.replace(r'\D', '', regex=True).str.strip()

        # convert results in numeric values
        df['parkings'] = pd.to_numeric(df['parkings'], errors='coerce')

        return df


# ------ ADA, THE MAIN CLEANER ------ #
class Ada:
    def __init__(self, columns_to_clean:List[str]):
        cleaners_ = {
            'price':PriceCleaner,
            'price_pesos':PriceCurrencyUpdater,
            'location':LocationCleaner,
            'bedrooms':BedroomsCleaner,
            'bathrooms':BathroomsCleaner,
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

        return df
    
    def set_register_date(self, df:pd.DataFrame) -> pd.DataFrame:
        df['register_date'] = dt.datetime.now().strftime('%Y-%m-%d %H:%M')
        return df

    def reorganize(self, df:pd.DataFrame) -> pd.DataFrame:
        df = df[['price', 'listed_in', 'price_in_mxn', 'location', 'full_location', 'property_type', 'bedrooms', 'bathrooms', 'area', 'parkings', 'source', 'url', 'register_date']]
        return df
