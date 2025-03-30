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
conn_mysql_a = connect_to_mysql("dbaeropuerto_a")  # Base de datos en Norteamérica (asumido)
conn_mysql_c = connect_to_mysql("dbaeropuerto_c")  # Base de datos en Sudamérica
# Firebase debe estar en Europa
firebase_db = None  # Firebase no necesita conexión en este caso.

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

# 🔹 Diccionario actualizado de países por continente
countries = {
    "África": [
        "Argelia", "Angola", "Benín", "Botsuana", "Burkina Faso", "Burundi", "Cabo Verde", 
        "Camerún", "República Centroafricana", "Chad", "Comoras", "Congo", "República Democrática del Congo", 
        "Costa de Marfil", "Djibouti", "Egipto", "Guinea Ecuatorial", "Eritrea", "Esuatini", "Etiopía", 
        "Gabón", "Gambia", "Ghana", "Guinea", "Guinea-Bisáu", "Kenia", "Lesoto", "Liberia", "Libia", 
        "Madagascar", "Malawi", "Malí", "Mauricio", "Mauritania", "Mozambique", "Namibia", "Níger", "Nigeria", 
        "Ruanda", "Santo Tomé y Príncipe", "Senegal", "Seychelles", "Sierra Leona", "Somalia", "Sudáfrica", 
        "Sudán", "Tanzania", "Togo", "Túnez", "Uganda", "Zambia", "Zimbabue"
    ],
    "Asia": [
        "Afganistán", "Armenia", "Azerbaiyán", "Bahrein", "Bangladés", "Birmania (Myanmar)", "Bután", "Brunéi", 
        "Camboya", "China", "Chipre", "Corea del Norte", "Corea del Sur", "Emiratos Árabes Unidos", 
        "Georgia", "India", "Indonesia", "Irak", "Irán", "Israel", "Japón", "Jordania", "Kazajistán", 
        "Kenia", "Kuwait", "Kirgistán", "Laos", "Líbano", "Malasia", "Maldivas", "Mongolia", "Nepal", "Omán", 
        "Pakistán", "Palestina", "Filipinas", "Qatar", "Rusia", "Arabia Saudita", "Singapur", "Sri Lanka", 
        "Siria", "Tayikistán", "Tailandia", "Timor Oriental", "Turkmenistán", "Emiratos Árabes Unidos", 
        "Uzbekistán", "Vietnam", "Yemen"
    ],
    "Europa": [
        "Albania", "Alemania", "Andorra", "Armenia", "Austria", "Bélgica", "Bielorrusia", "Bosnia y Herzegovina", 
        "Bulgaria", "Chipre", "Croacia", "Dinamarca", "Eslovaquia", "Eslovenia", "España", "Estonia", "Finlandia", 
        "Francia", "Georgia", "Grecia", "Hungría", "Irlanda", "Islandia", "Italia", "Kazajistán", "Kosovo", 
        "Letonia", "Liechtenstein", "Lituania", "Luxemburgo", "Malta", "Moldavia", "Mónaco", "Montenegro", "Noruega", 
        "Países Bajos", "Polonia", "Portugal", "Reino Unido", "República Checa", "Rumanía", "San Marino", "Serbia", 
        "Suecia", "Suiza", "Ucrania"
    ],
    "América del Sur": [
        "Argentina", "Bolivia", "Brasil", "Chile", "Colombia", "Ecuador", "Guyana", "Paraguay", "Perú", "Surinam", 
        "Uruguay", "Venezuela"
    ],
    "América del Norte": [
        "Canadá", "Estados Unidos", "México"
    ],
    "Oceanía": [
        "Australia", "Fiyi", "Islas Marshall", "Micronesia", "Nauru", "Nueva Zelanda", "Palau", "Papúa Nueva Guinea", 
        "Samoa", "Islas Salomón", "Tonga", "Tuvalu", "Vanuatu"
    ],
    "Antártida": [
        "Antártida"
    ]
}

# Función que determina el servidor más cercano según el país
def get_server_for_country(country):
    # Recorremos el diccionario de países por continente
    for continent, countries_list in countries.items():
        if country in countries_list:
            # Si el país está en América del Norte, usa dbaeropuerto_a
            if continent == "América del Norte":
                return "Conectando a dbaeropuerto_a (MySQL) en América del Norte"
            # Si el país está en América del Sur, usa dbaeropuerto_c
            elif continent == "América del Sur":
                return "Conectando a dbaeropuerto_c (MySQL) en América del Sur"
            # Si el país está en Europa, usa dbaeropuerto_b
            elif continent == "Europa":
                return "Conectando a dbaeropuerto_b (Firebase) en Europa"
            # Si el país no está en los continentes definidos
            else:
                return "No hay servidor disponible para este continente"
    
    # Si el país no se encuentra en ninguna lista de continentes
    return "País no reconocido"

# Ejemplo de uso
country_input = "España"  # Ejemplo de país
server_connection = get_server_for_country(country_input)
print(server_connection)

# 🔹 Ruta para determinar la base de datos a utilizar
@app.route('/connect', methods=['POST'])
def connect():
    country = request.json.get('country')
    continent = None

    # Identificar continente
    for cont, country_list in countries.items():
        if country in country_list:
            continent = cont
            break

    response = {"message": ""}

    # Determinar a qué servidor conectar
    if continent == "Europa":
        response["message"] = f"Conectado a Firebase dbaeropuerto_b (Europa)."
    elif continent == "Asia":
        response["message"] = f"Conectado a Firebase dbaeropuerto_b (Asia)."
    elif continent == "América del Sur":
        if conn_mysql_c:
            response["message"] = f"Conectado a la base de datos dbaeropuerto_c (Sudamérica) (MySQL)."
    elif continent == "América del Norte":
        if conn_mysql_a:
            response["message"] = f"Conectado a la base de datos dbaeropuerto_a (Norteamérica) (MySQL)."
    elif continent == "África":
        response["message"] = f"Conectado a la base de datos dbaeropuerto_a (África)Norteamérica(MySQL)."
    elif continent == "Antártida":
        response["message"] = f"No hay servidores disponibles para la Antártida."
    else:
        return jsonify({"message": "País no encontrado. Verifica el nombre."}), 400


    return jsonify(response)

# Ruta principal para mostrar la página
@app.route('/')
def home():
    return render_template('index.html')  # 🟢 Retorna el archivo index.html

if __name__ == '__main__':
    app.run(debug=True)
