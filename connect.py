import mysql.connector

cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="bdbazar"
)

cursor = cnx.cursor()

query = "SELECT * FROM producto"
cursor.execute(query)

results = cursor.fetchall()

cursor.close()
cnx.close()

