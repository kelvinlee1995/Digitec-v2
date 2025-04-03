from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, InvalidSessionIdException, NoSuchWindowException
from selenium.webdriver.chrome.service import Service
import os
import pickle
import platform
import psutil

# Function to kill leftover chromedriver processes
def kill_chromedriver_processes():
    killed_pids = []  # List to store the PIDs of killed processes
    for process in psutil.process_iter(['pid', 'name']):
        if 'chromedriver' in process.info['name']:
            try:
                os.kill(process.info['pid'], 9)  # Force kill the process
                killed_pids.append(process.info['pid'])
            except Exception as e:
                print(f"Error killing process {process.info['pid']}: {e}")
    
    if killed_pids:
        print("All chromedriver processes killed.")
    else:
        print("No leftover chromedriver processes found.")

# Detect the operating system and set the ChromeDriver path
if platform.system() == "Windows":
    chromedriver_path = "requirement/chromedriver.exe"
elif platform.system() == "Darwin":
    chromedriver_path = "requirement/chromedriver"
else:
    raise OSError("Unsupported operating system")

# Create a Service object
s = Service(chromedriver_path)

# Ensure leftover processes are killed before starting
kill_chromedriver_processes()

try:
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

    print("Downloading the cookies...")

    # Store the cookies in a dictionary
    cookies = {cookie['name']: cookie['value'] for cookie in browser.get_cookies()}

    # Make sure the data folder exists
    if not os.path.exists('data'):
        os.makedirs('data')

    # Store the cookie as a pickle file
    file_name = 'cookies_test.pkl'
    with open(f"data/{file_name}", 'wb') as file:
        pickle.dump(cookies, file)

except InvalidSessionIdException:
    print("The browser session is invalid or has been closed. Please restart the script.")
except NoSuchWindowException:
    print("The target window has already been closed. Please restart the script.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    # Ensure the browser and chromedriver are closed
    if 'browser' in locals():
        try:
            browser.quit()
        except (InvalidSessionIdException, NoSuchWindowException):
            print("Browser was already closed.")
    kill_chromedriver_processes()