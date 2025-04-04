# DigitecScript

## Goal
The goal of the script is to update the target stock of a product in the ERP system.
The script reads the target stock from an excel file and updates the target stock in the ERP system online.

## Requirement
Software needed :
- Visual Studio Code
- Python 3
- Google Chrome

To run the script you need to install the following packages:
- selenium == 4.9.1
- pandas == 2.0.1
- bs4 == 0.0.1
- requests == 2.30.0
- psutil==2023.4.0

You can install them with the following command in the terminal:
```
pip3 install -r requirement/requirements.txt
```

Use this commande if you have right issues
```
pip3 install --user -r requirement/requirements.txt
```
## Usage
To run the script you need to run the following command :

- First you, you need to give your access (cookies) to the script
```
python cookieGrab.py
```

- When your access are stored in your session, then you run the script

```
python main.py
```
---
To set the limit of product the script will update go to line 270 to update the value

![image](https://github.com/kelvinlee1995/Digitec-v2/assets/55844277/b04d7e2a-ef4d-463f-9917-1d3ce9f997fe)


## Convert XLSX to CSV
- Open your Excel file and export it in CSV

![image](https://github.com/kelvinlee1995/Digitec-v2/assets/55844277/b5d65301-0d3d-4e83-839f-8f9ccee75001)

- Save it in **CSV UTF-8 (Comma delimited)**
- Rename the file in **"data.csv"**
- Save it in data directory

![image](https://github.com/kelvinlee1995/Digitec-v2/assets/55844277/2d38a1a2-d0d5-4a49-abf9-a5aa29e41a19)

---
# Update chromedriver.exe

- Go to https://googlechromelabs.github.io/chrome-for-testing/#stable
- Download the latest (stable) version of the file
- Replace the old chromedriver.exe with the new one inside the **requirement** folder

![image](https://github.com/user-attachments/assets/b593b720-805a-47ef-a290-1879cfb18063)
