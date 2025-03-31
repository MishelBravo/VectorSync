import firebase_admin
from firebase_admin import credentials, firestore

def connect_to_dbB():
    try:
        cred = credentials.Certificate("key.json")  # Reemplaza con tu archivo de credenciales de Firebase
        firebase_admin.initialize_app(cred)
        db_firestore = firestore.client()
        print("🔌 Conectado a dbaeropuerto_b en Firebase (Europa) Scrip")
        return db_firestore
    except Exception as e:
        print(f"❌ Error al conectar con dbaeropuerto_b: {e}")
        return None
