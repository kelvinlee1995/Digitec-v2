# DigitecScript

## Goal
The goal of the script is to update the target stock of a product in the ERP system.
The script reads the target stock from an excel file and updates the target stock in the ERP system online.

## Requirement
To run the script you need to install the following packages:
- selenium == 4.9.1
- pandas == 2.0.1
- bs4 == 0.0.1
- requests == 2.30.0

You can install them with the following command:
```
pip install -r requirement/requirements.txt
```
## Usage
To run the script you need to run the following command :

- First you, you need to give your access (cookies) to the script
```
python erp/cookieGrab.py
```

- When your access is stored in your session, then you run the script

```
python erp/cookieGrab.py
```