from flask import Flask, request, jsonify, render_template
import mysql.connector
import firebase_admin
from firebase_admin import credentials, firestore
import time
import threading

app = Flask(__name__, template_folder="templates")  # 🟢 Define la carpeta de templates

# 🔹 Inicializar Firebase.
try:
    cred = credentials.Certificate("key.json")  # Asegúrate de tener el archivo key.json
    firebase_admin.initialize_app(cred)
    db_firestore = firestore.client()
    print("✅ Conectado a Firebase correctamente.")
except Exception as e:
    print(f"❌ Error al conectar con Firebase: {e}")

# 🔹 Conectar a ambas bases de datos MySQL
def connect_to_mysql(database_name):
    try:
        conn = mysql.connector.connect(
            host="localhost",   # Dirección del servidor MySQL
            user="root",        # Usuario de MySQL
            password="admin",   # Contraseña de MySQL
            database=database_name  # Nombre de la base de datos (dbaeropuerto_a o dbaeropuerto_c)
        )
        return conn
    except mysql.connector.Error as err:
        print(f"❌ Error al conectar con MySQL ({database_name}): {err}")
        return None

# Crear conexiones simultáneas
conn_mysql_a = connect_to_mysql("dbaeropuerto_a")  # Base de datos en Europa
conn_mysql_c = connect_to_mysql("dbaeropuerto_c")  # Base de datos en América

# 🔹 Implementación de Relojes Vectoriales para sincronización
vector_clock = {"dbaeropuerto_a": 0, "dbaeropuerto_b": 0, "dbaeropuerto_c": 0}

# 🔹 Función para sincronizar datos entre servidores
def sync_data():
    while True:
        # Simulación de sincronización cada 5 segundos
        time.sleep(5)
        print("🔄 Sincronizando datos entre servidores...")

        # Incrementar el reloj vectorial
        vector_clock["dbaeropuerto_a"] += 1
        vector_clock["dbaeropuerto_b"] += 1
        vector_clock["dbaeropuerto_c"] += 1

        print(f"🕒 Estado del Reloj Vectorial: {vector_clock}")

# Ejecutar sincronización en un hilo aparte
sync_thread = threading.Thread(target=sync_data)
sync_thread.daemon = True
sync_thread.start()

# 🔹 Ruta para determinar la base de datos a utilizar
@app.route('/connect', methods=['POST'])
def connect():
    country = request.json.get('country')
    continent = None

    # Definir los países por continente
    countries = {
        "Europa": ["España", "Francia", "Alemania", "Italia", "Polonia"],
        "Asia": ["China", "India", "Japón", "Corea del Sur", "Vietnam"],
        "América del Sur": ["Argentina", "Brasil", "Chile", "Bolivia", "Perú"],
        "América del Norte": ["Estados Unidos", "Canadá", "México"],
    }

    # Identificar continente
    for cont, country_list in countries.items():
        if country in country_list:
            continent = cont
            break

    response = {"message": ""}

    # Conectar a la base de datos según la ubicación del usuario
    if continent == "Europa":
        if conn_mysql_a:
            response["message"] = f"Conectado a la base de datos dbaeropuerto_a (Europa)."
    elif continent == "Asia":
        response["message"] = f"Conectado a Firebase dbaeropuerto_b (Asia)."
    elif continent in ["América del Sur", "América del Norte"]:
        if conn_mysql_c:
            response["message"] = f"Conectado a la base de datos dbaeropuerto_c (América)."
    else:
        return jsonify({"message": "País no encontrado. Verifica el nombre."}), 400

    return jsonify(response)

# Ruta principal para mostrar la página
@app.route('/')
def home():
    return render_template('index.html')  # 🟢 Retorna el archivo index.html

if __name__ == '__main__':
    app.run(debug=True)
