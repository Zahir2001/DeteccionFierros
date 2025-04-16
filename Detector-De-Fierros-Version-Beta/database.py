import mysql.connector

def conectar_bd():
    conn = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="",
        database="semoviente"
    )
    return conn
