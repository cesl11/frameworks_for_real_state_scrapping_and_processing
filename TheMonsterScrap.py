# importing libraries
import numpy as np
import pandas as pd
import requests
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Any

"""
This code belongs to César Loubet (GitHub user: cesl11) and the only person or company allowed to use it and modify it is AiMexa (https://aimexa.tech/).
    - If you want to use this code as inspiration, or you find it useful and want to implement it in your own projects, please contact me:
        MAIL: cesarloubet2003@gmail.com
        LINKEDIN: César Loubet
    Cheers :)
"""


# ------- Handlers ------ #
class HttpClient:
    """A class to handle all HTTP with proper headers and excepcion handling."""
    def __init__(self, headers:Optional[Dict[str,str]] = None, timeout:int = 15):
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
        }
        self.timeout = timeout
    
    def get_html(self, url:str) -> Optional[str]:
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            if response.status_code == 200:
                return response.text
            else:
                print(f'An error ocurred : status code {response.status_code} of {url}')
                return None
        except requests.exceptions.RequestException as e:
            print(f'An error ocurred while fetching {url}: {e}')
            return None


class Listing:
    """Represents a real-state listing in a page."""
    def __init__(self):
        self.price = Optional[str]
        self.location = Optional[str]
        self.bedrooms = Optional[str]
        self.bathrooms = Optional[str]
        self.area = Optional[str]
        self.parkings = Optional[str]
        self.url = Optional[str]
        
    def convert_to_dict(self) -> Dict[str,Any]:
        """Convert info into a dict for better manipulation."""
        return dict({
            'price':self.price,
            'location':self.location,
            'bedrooms':self.bedrooms,
            'bathrooms':self.bathrooms,
            'area':self.area,
            'parkings':self.parkings,
            'url':self.url
        })



# ------ Parsing Interfaces ------ #
class AttributeParser(ABC):
    """An abstract class for managing further parsers."""
    
    @abstractmethod
    def parse(self, listing:BeautifulSoup) -> Optional[str]:
        pass


class PriceParser(AttributeParser):
    def __init__(self, label:str, attrs:Optional[Dict[str,str]]):
        self.label = label
        self.attrs = attrs
    
    def parse(self, listing:BeautifulSoup) -> Optional[str]:
        element = listing.find(self.label, attrs=self.attrs)
        return element.get_text(strip=True) if element else None
    

class LocationParser(AttributeParser):
    def __init__(self, label:str, attrs:Optional[Dict[str,str]]):
        self.label = label
        self.attrs = attrs
        
    def parse(self, listing:BeautifulSoup) -> Optional[str]:
        element = listing.find(self.label, attrs=self.attrs)
        return element.get_text(strip=True) if element else None


class BedroomsParser(AttributeParser):
    def __init__(self, label:str, attrs:Optional[Dict[str,str]]):
        self.label = label
        self.attrs = attrs
        
    def parse(self, listing:BeautifulSoup) -> Optional[str]:
        element = listing.find(self.label, attrs=self.attrs)
        return element.get_text(strip=True) if element else None
    

class BathroomsParser(AttributeParser):
    def __init__(self, label:str, attrs:Optional[Dict[str,str]]):
        self.label = label
        self.attrs = attrs
        
    def parse(self, listing:BeautifulSoup) -> Optional[str]:
        element = listing.find(self.label, attrs=self.attrs)
        return element.get_text(strip=True) if element else None


class AreaParser(AttributeParser):
    def __init__(self, label:str, attrs:Optional[Dict[str,str]]):
        self.label = label
        self.attrs = attrs
        
    def parse(self, listing:BeautifulSoup) -> Optional[str]:
        element = listing.find(self.label, attrs=self.attrs)
        return element.get_text(strip=True) if element else None


class ParkingsParser(AttributeParser):
    def __init__(self, label:str, attrs:Optional[Dict[str,str]]):
        self.label = label
        self.attrs = attrs
    
    def parse(self, listing:BeautifulSoup) -> Optional[str]:
        element = listing.find(self.label, attrs=self.attrs)
        return element.get_text(strip=True) if element else None
    

class UrlParser(AttributeParser):
    def __init__(self, label:str):
        self.label = label
    
    def parse(self, listing:BeautifulSoup) -> str:
        element = listing.find(self.label)
        return element.get('href') if element else None



# ------ MAIN SCRAPPER, THE BEAST ------ #
class ScrapperMonster:
    """This Monster manages all the scrapping process."""
    def __init__(self, html:str):
        self.soup = BeautifulSoup(html, 'html.parser')
        self.parsers:Dict[str,AttributeParser] = {}
    
    def add_parser(self, attribute_name:str, parser:AttributeParser):
        """Add and attribute parser to the monster."""
        self.parsers[attribute_name] = parser
        
    def get_listings(self, label_tag:str, attrs:Optional[Dict[str,str]]) -> List[BeautifulSoup]:
        """Get all listings from webpage."""
        return self.soup.find_all(
            label_tag,
            attrs=attrs
        )
    
    def unleash(self, listings:List[BeautifulSoup]) -> List[Listing]:
        """Scrap all the defined attributes and returns a list with all data."""
        results = []
        
        for listing in listings:
            current_listing = Listing()
            
            for attribute_name, parser in self.parsers.items():
                value = parser.parse(listing)
                setattr(current_listing, attribute_name.lower(), value)
                
            results.append(current_listing)
            
        return results



# ------ Exporter ------ #
class Exporter:
    """Manage the exporting process for .csv and Pandas DataFrame formats.
    Requires the return of the ScrapperMonster to work."""
    @staticmethod
    def to_csv(listings: List[Listing], filename: str):
        data = [listing.convert_to_dict() for listing in listings]
        df = pd.DataFrame(data)
        df.to_csv(f'{filename}.csv', index=False, encoding='latin1')

    @staticmethod
    def to_dataframe(listings: List[Dict[str, Any]]) -> pd.DataFrame:
        data = [listing.convert_to_dict() for listing in listings]
        return pd.DataFrame(data)
