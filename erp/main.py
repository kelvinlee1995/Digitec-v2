import requests
import pickle
import os
from bs4 import BeautifulSoup
import pandas as pd

from typing import List, Dict, Union

# Gets the cookies from a specified path and returns a session with them
def get_cookies(cookiesFilePath: str = "data/cookies.pkl", validate: bool = True) -> requests.Session:
    session = requests.Session()

    # Get the cookies 
    if os.path.exists(cookiesFilePath):
        with open(cookiesFilePath, 'rb') as file:
            cookies = pickle.load(file) # Could not figure out how to authenticate with the ERP (especially because of 2FA), so I just copy the cookies from my browser and keep track of the Auth2.0 behaviour. Defeneteley something to change in the future.
    else:
        print("No cookies found in path: " + cookiesFilePath)
        return None
    
    # Store the cookies in the session
    try:
        session.cookies.update(cookies)
    except Exception as e:
        print("An unknown error occured. Please try again. The cookies are probably not in the right format.")
        print(e)
        return None

    # Check if the cookies are valid
    if validate:
        response = session.get("https://erp.digitecgalaxus.ch/de/Welcome")
        if response.url.startswith("https://erp.digitecgalaxus.ch/de/Login"): # If im redirected to the login page, the cookies are not valid
            print("Cookies are not valid. Please run the cookiesGrab.py.")
            return None
        
    return session

# Function to change the key name of a dictionary. Python should have a built in function for this
def change_key_name(dictionary: dict, old_key: str, new_key: str) -> dict:
    if old_key in dictionary:
        value = dictionary.pop(old_key)
        dictionary[new_key] = value
    return dictionary

# Function to get the Lafgerstand of a given product, if no soup is given, the soup will be requested
def getLagerStand(session: requests.Session, productID: str, soup=None) -> Union[Dict[str, int], BeautifulSoup]:
    if soup == None:
        find_product_url = "https://erp.digitecgalaxus.ch/de/Product/Availability/"

        r = session.get(find_product_url + productID)
        soup = BeautifulSoup(r.text, 'html.parser')
    else:
        print("Soup given")

    # Find the table
    #table = soup.select_one("#ProductProductWarehouseCompartment2 > div.content.erpBoxContent > div > div > div > table")
    table = soup.select_one("#ProductSiteTargetInventoryOverrideTable5 > form > table")

    # Parse the table
    tr_elements = table.find_all("tr")[1:]

    td_elements = [tr_element.find_all("td") for tr_element in tr_elements]
    td_elements = [[td_element.text.strip() for td_element in td_element] for td_element in td_elements]

    # Store the Lagerstand in a dictionary
    lagerstand = {}

    for td_element in td_elements:
        if td_element[0] not in lagerstand:
            lagerstand[td_element[0]] = int(td_element[1])
        else:
            lagerstand[td_element[0]] += int(td_element[1])
    
    # Some of the filialen have different names in the Lagerstand than in the Zielbestand
    if "StGallen" in lagerstand:
        lagerstand = change_key_name(lagerstand, "StGallen", "St. Gallen")
    if "ZÃ¼rich" in lagerstand:
        lagerstand = change_key_name(lagerstand, "ZÃ¼rich", "Zürich")

    return lagerstand, soup

# Function to deleate all the current Zielbestand rules, if no soup is given, the soup will be requested
def deleateZielbestand(session: requests.Session, productID: str, soup=None) -> BeautifulSoup:
    if soup == None:
        find_product_url = "https://erp.digitecgalaxus.ch/de/Product/Availability/"
        
        r = session.get(find_product_url + productID)
        soup = BeautifulSoup(r.text, 'html.parser')

    # Find out how many rules there are
    rule_table = soup.select_one("#ProductSiteTargetInventoryOverrideTable5 > form > table")

    # Parse the table
    tbody_elements = rule_table.find_all("tbody")[0]
    tr_elements = tbody_elements.find_all("tr")
    hrefs = [tr_element.find_all("a")[0]["href"] for tr_element in tr_elements]

    currentURL = "https://erp.digitecgalaxus.ch/de/Product/Availability/" + productID

    # Traverse the hrefs and deleate the rules
    num_requests = 0
    for href in hrefs:
        deleate_url = "https://erp.digitecgalaxus.ch" + href

        params = {
            'ajaxerplist': '2'
        }

        data = {
            'crud': 'delete'
        }

        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,de-CH;q=0.8,de;q=0.7',
            'Content-Length': '11',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://erp.digitecgalaxus.ch',
            'Referer': currentURL,
            'Sec-Ch-Ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }

        r = session.post(deleate_url, params=params, data=data, headers=headers)

        if r.status_code == 200:
            num_requests += 1
        else:
            print(f"Error: {r.status_code}")
    
    print(f"Deleated {num_requests} rules")

    return soup

# Takes in a session, productID and information about the new Zielbestand and adds it to the product for every filiale in the filialen list
def addZielbestand(session: requests.Session, productID: str, from_date: str, to_date: str, product_quantity: int, filialen: List[str], soup=None) -> BeautifulSoup:
    if soup == None:
        find_product_url = "https://erp.digitecgalaxus.ch/de/Product/Availability/"
        
        r = session.get(find_product_url + productID)
        soup = BeautifulSoup(r.text, 'html.parser')

    # Values encoded
    values_encoded ={
        'Basel': 246967,
        'Bern': 246970,
        'Dietikon': 246971,
        'Genf': 246975,
        'Kriens': 246968,
        'Lausanne': 246965,
        'St. Gallen': 246974,
        'Winterthur': 246969,
        'Wohlen': 246977,
        'Zürich': 246938
    }

    # Find out the product mandant, necessary for the request
    #mandant = soup.select_one("#ProductBox1 > div.content.erpBoxContent > div:nth-child(3) > div:nth-child(8) > div:nth-child(2)").text.strip()

    mandant = soup.select_one("#ProductSiteTargetInventoryOverrideTable5 > div > ul > li:nth-child(2) > a")["href"].split("/")[-1]

    # The url on which the post request is made
    create_url = "https://erp.digitecgalaxus.ch/ProductSiteTargetInventoryOverride/TableNew/" + mandant
    currentURL = "https://erp.digitecgalaxus.ch/de/Product/Availability/" + productID

    # Make a post request for every filiale
    num_requests = 0
    for filiale in filialen:

        params = {
                'ajaxerplist': '2'
        }

        data = {
            "ProductSiteTargetInventoryOverride.SiteId": values_encoded[filiale],
            "ProductSiteTargetInventoryOverride.Quantity": product_quantity,
            "ProductSiteTargetInventoryOverride.ValidFrom": from_date,
            "ProductSiteTargetInventoryOverride.ValidTo" : to_date,
            "save" : "",
        }

        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": currentURL,
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }

        r = session.post(create_url, params=params, data=data, headers=headers)

        if r.status_code == 200:
            num_requests += 1
        else:
            print(f"Error: {r.status_code}")
    
    print(f"Added {num_requests} rules")

    return soup

# Higher level function to update the Zielbestand of a product, returns a dictionary of how many products will be transfered to each filiale in the filialen
def updateZielbestand(session: requests.Session, productID: str, date_start: str, date_end:str, quantity: int, filialen: List[str] = ["Basel", "Bern", "Dietikon", "Genf", "Kriens", "Lausanne", "St. Gallen", "Winterthur", "Zürich"]) -> Dict[str, int]:
    # Get the Lagerstand
    lagerstand, soup = getLagerStand(session, productID)

    # Deleate the current Zielbestand
    deleateZielbestand(session, productID, soup=soup)

    # Add the new Zielbestand
    addZielbestand(session, productID, date_start, date_end, quantity, filialen, soup=soup)

    # Calculate how many products need to be transfered per filiale with the new Zielbestand
    productsForTransfer = {}
    for filiale in filialen:
        if filiale not in lagerstand:
            productsForTransfer[filiale] = quantity
        else:
            productsForTransfer[filiale] = max(0, quantity - lagerstand[filiale])
    return productsForTransfer

def main():
    # Load the cookies pkl file and store them in a session object
    session = get_cookies(validate=True)

    assert session != None, "The cookies are not valid. Please run the cookiesGrab.py."

    date_start = "16.05.2023"
    date_end = "09.05.2024"

    #load excel
    df = pd.read_csv("data.csv", skiprows=2)

    bestand = {'Basel': 0, 'Bern': 0, 'Dietikon': 0, 'Genf': 0, 'Kriens': 0, 'Lausanne': 0, 'St. Gallen': 0, 'Winterthur': 0, 'Zürich': 0}

    stop_at = 200

    for index, row in df.iterrows():
        product = str(int(row["Product Id"]))
        zielbestand = int(row["Stück pro Filiale"])
        bemerkungen = row['Bemerkungen']

        update = updateZielbestand(session, product, date_start, date_end, zielbestand)

        for city, value in update.items():
            if city in bestand:
                bestand[city] += value

        if index % 10 == 0:
            print(bestand)

        max_stock = max(bestand.values())

        print(f"{round(max_stock/stop_at*100)} %")

if __name__ == "__main__":
    main()