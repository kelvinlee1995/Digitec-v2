from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
import os
import pickle

# Create a Service object
s=Service("requirement/chromedriver.exe")

# Pass the Service object instead of executable_path
browser = webdriver.Chrome(service=s)

# Go to the URL
browser.get("https://test-erp.digitecgalaxus.ch/")

# Wait 10s for the page to load
WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="activedirectoryotheruser"]')))

# Wait untill the user authentificates
print("Waiting 120s for user to authentificate...")
try:
    WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.XPATH, '//*[@id="controllertitle"]')))
except TimeoutException:
    print("User did not authentificate in time!")


print("User authentificated!")

print("Downloading the cookies...")

# Store the cookies in a dictionary
cookies = {cookie['name']: cookie['value'] for cookie in browser.get_cookies()}

# make sure the data folder exists
if not os.path.exists('data'):
    os.makedirs('data')

# Store the cookie as a pickle file

file_name = 'cookies_aleks.pkl'
with open(f"../data/{file_name}", 'wb') as file:
    pickle.dump(cookies, file)

# Close the browser after the cookies are stored
browser.quit()