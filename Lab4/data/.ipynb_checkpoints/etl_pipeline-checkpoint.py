import pyodbc as odbc
import pandas as pd
import sys
from sqlalchemy import create_engine
import time

#Create connection to SQL Database on Azure Cloud


      
def extract(message_filepath, categories_filepath):
    #Load data from two file csv and merge them.
    messages = pd.read_csv(message_filepath)
    categories = pd.read_csv(categories_filepath)
    return pd.merge(messages, categories, on='id')
    
def transform(df):
    categories = df['categories'].str.split(pat=';', n=None, expand=True)
    category_colnames = categories.iloc[0].str[:-2]
    categories.columns = category_colnames

    for column in categories:
        categories[column] = categories[column].str[-1].astype(int)

    df = df.drop(columns='categories')
    df = pd.concat([df, categories], axis=1)
    df = df.drop(columns=['child_alone'])
    filtered_df = df[df['related'] <= 1]
    df = filtered_df.copy()
    df.drop_duplicates(subset=['id'], keep='first', inplace=True)
    df = df.drop_duplicates(keep='first')
    # print(df.columns.unique)
    return df

def save_data_azure(df):
    
    connection_string = "Driver={ODBC Driver 18 for SQL Server};Server=tcp:chunporo.database.windows.net,1433;Database=Disaster;Uid=chunporo;Pwd=Pass@123;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    insert_statement = f"""
    INSERT INTO tbl_disaster (
        [id], [message], [original], [genre], [related], [request], [offer],
        [aid_related], [medical_help], [medical_products], [search_and_rescue],
        [security], [military], [water], [food], [shelter],
        [clothing], [money], [missing_people], [refugees], [death], [other_aid],
        [infrastructure_related], [transport], [buildings], [electricity],
        [tools], [hospitals], [shops], [aid_centers], [other_infrastructure],
        [weather_related], [floods], [storm], [fire], [earthquake], [cold],
        [other_weather], [direct_report]
    ) VALUES (
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
    );
    """
 
        
    conn = odbc.connect(connection_string)
    cursor = conn.cursor()
    for index, row in df.iterrows():
    # Execute the INSERT statement with parameterized query
        cursor.execute("INSERT INTO tbl_disaster "
                    "(id, message, original, genre, related, request, offer, aid_related, "
                    "medical_help, medical_products, search_and_rescue, security, military, "
                    "water, food, shelter, clothing, money, missing_people, refugees, death, "
                    "other_aid, infrastructure_related, transport, buildings, electricity, "
                    "tools, hospitals, shops, aid_centers, other_infrastructure, weather_related, "
                    "floods, storm, fire, earthquake, cold, other_weather, direct_report) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
                    "?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (row['id'], row['message'], row['original'], row['genre'], row['related'],
                        row['request'], row['offer'], row['aid_related'], row['medical_help'],
                        row['medical_products'], row['search_and_rescue'], row['security'],
                        row['military'], row['water'], row['food'], row['shelter'], row['clothing'],
                        row['money'], row['missing_people'], row['refugees'], row['death'],
                        row['other_aid'], row['infrastructure_related'], row['transport'],
                        row['buildings'], row['electricity'], row['tools'], row['hospitals'],
                        row['shops'], row['aid_centers'], row['other_infrastructure'],
                        row['weather_related'], row['floods'], row['storm'], row['fire'],
                        row['earthquake'], row['cold'], row['other_weather'], row['direct_report']))
    
    cursor.commit()        #Close the cursor and connection


def save_data_to_db(df, database_filename):
    engine = create_engine('sqlite:///'+ database_filename)
    table_name = database_filename.replace(".db","") + "_table"
    df.to_sql(table_name, engine, index=False, if_exists='replace')

def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:] # Extract the parameters in relevant variable
       
        df = extract(messages_filepath, categories_filepath)
        df = transform(df)
        
        print('Saving data to SQLite DB : {}'.format(database_filepath))
        save_data_to_db(df, database_filepath)
        
        print('Cleaned data has been saved to database!')
    
    else: # Print the help message so that user can execute the script with correct parameters
        print("ERROR")
    
if __name__ == '__main__':
    main()