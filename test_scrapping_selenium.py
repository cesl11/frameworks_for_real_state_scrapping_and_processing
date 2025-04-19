from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import pandas as pd
import numpy as np

# defining user agent
opts = Options()
opts.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36')

# starts a webdriver and initialize Chrome
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=opts
)

# entering to the page
url_base = 'https://www.real_state_example.com/listings#?cityIds=dc18cc8c-540b-e611-80c9-000d3a12a9c9&searchText=%20La%20Paz,%20Baja%20California%20Sur&transactionType=1&lan=es-MX&currency=MXN&filterVal=1026&refineSearch=1&propertyType=1013&pageNumber=2'
driver.get(url_base)

# wait page load
sleep(13)

# create a list to storage all listings info
all_listings = []

# get all listings on the page
listings = driver.find_elements(By.CSS_SELECTOR, 'div.gallery-item')

for listing in listings:
    # getting each individual listing
    element_href = listing.find_element(By.CSS_SELECTOR, 'a.LinkImage')
    url_listing = element_href.get_attribute('href')
    
    driver.execute_script('window.open(arguments[0]);', url_listing)
    driver.switch_to.window(driver.window_handles[1])
    sleep(20)
    
    # scrap with exceptions handling

    price = driver.find_element(By.XPATH, '//span[contains(text(), "MXN $")]').text.strip() if driver.find_elements(By.XPATH, '//span[contains(text(), "MXN $")]') else None
    location = driver.find_element(By.CSS_SELECTOR, 'p.ng-binding').text.strip() if driver.find_elements(By.CSS_SELECTOR, 'p.ng-binding') else None
    bedrooms = driver.find_element(By.XPATH, '//p[text()="Recámaras:"]/following-sibling::p').text.strip() if driver.find_elements(By.XPATH, '//p[text()="Recámaras:"]/following-sibling::p') else None
    bathrooms = driver.find_element(By.XPATH, '//p[text()="Baños:"]/following-sibling::p').text.strip() if driver.find_elements(By.XPATH, '//p[text()="Baños:"]/following-sibling::p') else None
    area = driver.find_element(By.XPATH, '//p[text()="Área construida:"]/following-sibling::p').text.strip() if driver.find_elements(By.XPATH, '//p[text()="Área construida:"]/following-sibling::p') else None
    parkings = driver.find_element(By.XPATH, '//p[text()="Estacionamientos:"]/following-sibling::p').text.strip() if driver.find_elements(By.XPATH, '//p[text()="Estacionamientos:"]/following-sibling::p') else None

    dataListing = {
        'price':price,
        'location':location,
        'bedrooms':bedrooms,
        'bathrooms':bathrooms,
        'area':area,
        'parkings':parkings,
        'url':url_listing
    }
        
    all_listings.append(dataListing)
        
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    sleep(15)

# check if the data is saved successfully
for listing in all_listings:
    print(listing)

# saving data in a .csv file     
df = pd.DataFrame(all_listings)
df.to_csv(f'data{4}_.csv', index=False, encoding='utf-8')

# close driver
driver.quit()