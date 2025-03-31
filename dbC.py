import mysql.connector

def connect_to_dbC():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="admin",
            database="db_aeropuerto_c"
        )
        if conn.is_connected():
            print("🔌 Conectado a db_aeropuerto_c en MySQL (Sudamérica) Scrip")
        return conn
    except mysql.connector.Error as err:
        print(f"❌ Error al conectar con db_aeropuerto_c: {err}")
        return None
