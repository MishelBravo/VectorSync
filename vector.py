import mysql.connector
import firebase_admin
from firebase_admin import credentials, firestore
import time
import json

# Configuración de MySQL (db_aerolinea_a y db_aerolinea_c)
db_aerolinea_a = mysql.connector.connect(
    host="localhost",
    user="usuario_a",
    password="contraseña_a",
    database="db_aerolinea_a"
)

db_aerolinea_c = mysql.connector.connect(
    host="localhost",
    user="usuario_c",
    password="contraseña_c",
    database="db_aerolinea_c"
)

# Configuración de Firebase (db_aerolinea_b)
cred = credentials.Certificate('path/to/serviceAccountKey.json')
firebase_admin.initialize_app(cred)
db_firebase = firestore.client()

# Reloj Vectorial de las bases de datos (inicialización)
reloj_vectorial_a = [0, 0]  # Asumimos que hay 2 nodos (a y c)
reloj_vectorial_c = [0, 0]
reloj_vectorial_b = [0, 0]

# Función para obtener los datos desde db_aerolinea_a (MySQL)
def obtener_datos_desde_mysql_a():
    cursor = db_aerolinea_a.cursor(dictionary=True)
    cursor.execute("SELECT * FROM vuelos")  # Cambia la consulta según tu esquema
    resultados = cursor.fetchall()
    cursor.close()
    return resultados

# Función para sincronizar con db_aerolinea_c (MySQL)
def sincronizar_con_mysql_c(datos, reloj_a):
    cursor = db_aerolinea_c.cursor()
    sql = "INSERT INTO vuelos (id, nombre, fecha) VALUES (%s, %s, %s)"
    valores = [(d['id'], d['nombre'], d['fecha']) for d in datos]
    cursor.executemany(sql, valores)
    db_aerolinea_c.commit()
    cursor.close()
    
    # Actualizar reloj vectorial de db_aerolinea_c (incrementamos su índice correspondiente)
    reloj_vectorial_c[1] = max(reloj_vectorial_c[1], reloj_a[1]) + 1  # Incrementar el reloj de c
    print("Datos sincronizados con db_aerolinea_c (MySQL), Reloj actualizado:", reloj_vectorial_c)

# Función para sincronizar con Firebase (db_aerolinea_b)
def sincronizar_con_firebase(datos, reloj_a):
    batch = db_firebase.batch()
    for d in datos:
        doc_ref = db_firebase.collection('vuelos').document(str(d['id']))
        batch.set(doc_ref, {
            'nombre': d['nombre'],
            'fecha': d['fecha']
        })
    batch.commit()
    
    # Actualizar reloj vectorial de Firebase
    reloj_vectorial_b[0] = max(reloj_vectorial_b[0], reloj_a[0]) + 1  # Incrementar el reloj de b
    print("Datos sincronizados con db_aerolinea_b (Firebase), Reloj actualizado:", reloj_vectorial_b)

# Función principal para sincronizar las tres bases de datos
def sincronizar_bases_de_datos():
    try:
        # Obtener los datos desde db_aerolinea_a
        datos = obtener_datos_desde_mysql_a()

        # Sincronizar con db_aerolinea_c (MySQL)
        sincronizar_con_mysql_c(datos, reloj_vectorial_a)

        # Sincronizar con Firebase
        sincronizar_con_firebase(datos, reloj_vectorial_a)

        # Actualizar reloj de db_aerolinea_a
        reloj_vectorial_a[0] += 1  # Incrementar el reloj de a
        print("Datos sincronizados con db_aerolinea_a (MySQL), Reloj actualizado:", reloj_vectorial_a)

    except Exception as e:
        print(f"Error en la sincronización: {e}")

# Ejecutar la sincronización cada 5 segundos
while True:
    sincronizar_bases_de_datos()
    time.sleep(5)  # Esperar 5 segundos antes de volver a sincronizar
