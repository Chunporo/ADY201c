import pyodbc as odbc
import pandas as pd
import sys
from sqlalchemy import create_engine

#Create connection to SQL Database on Azure Cloud
connection_string = "Driver={ODBC Driver 18 for SQL Server};Server=tcp:chunporo.database.windows.net,1433;Database=Disaster;Uid=chunporo;Pwd=Pass@123;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"

cnxh = odbc.connect(connection_string)
cursor = cnxh.cursor()

def extract(message_filepath, categories_filepath):
    #Load data from two file csv and merge them.
    messages = pd.read_csv(message_filepath)
    categories = pd.read_csv(categories_filepath)
    
def transform(df):
    categories = df['categories'].str.split(pat=';', n=None, expand=True)
    category_colnames = categories.iloc[0].str[:-2]
    categories.columns = category_colnames

    for column in categories:
        categories[column] = categories[column].str[-1].astype(int)

    df = df.drop(columns='categories')
    df = pd.concat([df, categories], axis=1)
    df = df.drop_duplicates(keep='first')

    return df

def save_data(df, database_filename):
    
