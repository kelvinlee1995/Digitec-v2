#convert xlsx to csv
import pandas as pd
import os

# make sure the data folder exists
if not os.path.exists('data'):
    os.makedirs('data')

# import the xlsx file
df = pd.read_excel('data/20220405_Filialzielbestand Pilotversuch.xlsx')
df = df.drop([0,1]) # remove the first two lines

# store the csv file
df.to_csv('data/20220405_Filialzielbestand Pilotversuch.csv', index=False)

#remove line 1 and 2
df = pd.read_csv('data/20220405_Filialzielbestand Pilotversuch.csv')

print("File converted successfully!")