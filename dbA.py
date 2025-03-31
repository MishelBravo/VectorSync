import mysql.connector

def connect_to_dbA():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="admin",
            database="db_aeropuerto_a"
        )
        if conn.is_connected():
            print("🔌 Conectado a db_aeropuerto_a en MySQL ")
        return conn
    except mysql.connector.Error as err:
        print(f"❌ Error al conectar con db_aeropuerto_a: {err}")
        return None


