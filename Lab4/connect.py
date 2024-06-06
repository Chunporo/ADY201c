import pyodbc as odbc


#Create connection to SQL Database on Azure Cloud
connection_string = "Driver={ODBC Driver 18 for SQL Server};Server=tcp:chunporo.database.windows.net,1433;Database=Disaster;Uid=chunporo;Pwd=Pass@123;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"

cnxh = odbc.connect(connection_string)
cursor = cnxh.cursor()
