from flask import Flask, request, jsonify, render_template
import mysql.connector
from mysql.connector import Error
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# Conexión global a la base de datos
db_connection = None
query_executed = False

def connect_to_dbA():
    global db_connection
    try:
        # Solo conectar si no hay una conexión activa
        if db_connection is None or not db_connection.is_connected():
            db_connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="admin",
                database="db_aeropuerto_a"
            )
            if db_connection.is_connected():
                print("🔌 Conectado a db_aeropuerto_a en MySQL")
        return db_connection
    except Error as err:
        print(f"❌ Error al conectar con db_aeropuerto_a: {err}")
        return None


# Diccionario actualizado de países por continente
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
    "Sudamérica": [
        "Argentina", "Bolivia", "Brasil", "Chile", "Colombia", "Ecuador", "Guyana", "Paraguay", "Perú", "Surinam", 
        "Uruguay", "Venezuela"
    ],
    "Norteamérica": [
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


# Ruta principal para mostrar la página
@app.route('/')
def home():
    results = execute_query_and_print()  # Solo contiene aeropuertos
    descriptions = [airport['descripcion'] for airport in results]

    airports = {
        "origen": descriptions,
        "destino": descriptions
    }

    return render_template('index.html', airports=airports)

#----------------------------------------------------------------------------------------------------------

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

    if continent in ["Europa", "Asia", "África"]:
        servidor = "dbaeropuerto_a"
        response["message"] = f"Conectado a {servidor} en (MYSQL-Europa) ({continent})."
        connect_to_dbA()
        guardar_servidor(servidor)

    elif continent == "Norteamérica":
        servidor = "dbaeropuerto_b"
        response["message"] = f"Conectado a {servidor} en Firebase (Norteamérica)."
        connect_to_dbA()
        guardar_servidor(servidor)

    elif continent == "Sudamérica":
        servidor = "dbaeropuerto_c"
        response["message"] = f"Conectado a {servidor} en MySQL (Sudamérica)."
        connect_to_dbA()
        guardar_servidor(servidor)

    else:
        response["message"] = "No hay servidores disponibles para este continente."

    return jsonify(response)

#----------------------------------------------------------------------------------------------------------
def guardar_servidor(nombre_servidor):
    try:
        if db_connection is None or not db_connection.is_connected():
            connect_to_dbA()

        cursor = db_connection.cursor()
        query = "INSERT INTO servidores (nombreServidor) VALUES (%s)"
        cursor.execute(query, (nombre_servidor,))
        db_connection.commit()
        cursor.close()
        print(f"✅ Servidor '{nombre_servidor}' guardado en la base de datos.")
    except Error as e:
        print(f"❌ Error al guardar el servidor: {e}")



#----------------------------------------------------------------------------------------------------------
# Ejecutar la consulta
def execute_query_and_print():
    try:
        if db_connection is None or not db_connection.is_connected():
            print("🔌 Intentando conectar a la base de datos...")
            connect_to_dbA()  # Conectar si no está ya conectado

        cursor = db_connection.cursor(dictionary=True)

        # 🔄 Solo obtener las descripciones de los aeropuertos
        query = """
        SELECT idAeropuerto, descripcion 
        FROM Aeropuerto;
        """
        print(f"Ejecutando consulta: {query}")
        cursor.execute(query)
        results = cursor.fetchall()
        print(f"Resultados obtenidos: {results}")

        cursor.close()
        return results
    except Error as err:
        print(f"❌ Error al ejecutar la consulta: {err}")
        return []


#----------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/buscar_vuelos', methods=['POST'])
def buscar_vuelos():
    data = request.get_json()
    origen = data['origin']
    destino = data['destination']
    fecha = data['date']

    conn = connect_to_dbA()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT 
            v.idVuelo, 
            v.fechaSalida, 
            v.horaSalida, 
            v.estado, 
            a1.descripcion AS Origen, 
            a2.descripcion AS Destino,
            al.nombreAerolinea,
            av.nombreAvion,
            av.tipoAvion
        FROM Vuelo v
        JOIN RutaComercial r ON v.RutaComercial_idRutaComercial = r.idRutaComercial
        JOIN Aeropuerto a1 ON r.fk_idAeropuertoOrigen = a1.idAeropuerto
        JOIN Aeropuerto a2 ON r.fk_idAeropuertoDestino = a2.idAeropuerto
        JOIN Aerolinea al ON v.Aerolinea_idAerolinea = al.idAerolinea
        JOIN Avion av ON v.Avion_idAvion = av.idAvion
        WHERE 
            a1.descripcion = %s
            AND a2.descripcion = %s
            AND v.fechaSalida = %s;
    """

    cursor.execute(query, (origen, destino, fecha))
    vuelos = cursor.fetchall()

    conn.close()

    # Convertir los datos a texto o formato adecuado para pasar al frontend
    vuelos_texto = []
    for vuelo in vuelos:
        vuelo_data = {
            'idVuelo': vuelo['idVuelo'],
            'fechaSalida': str(vuelo['fechaSalida']),
            'horaSalida': str(vuelo['horaSalida']),
            'estado': vuelo['estado'],
            'origen': vuelo['Origen'],
            'destino': vuelo['Destino'],
            'nombreAerolinea': vuelo['nombreAerolinea'],
            'nombreAvion': vuelo['nombreAvion'],
            'tipoAvion': vuelo['tipoAvion']
        }
        vuelos_texto.append(vuelo_data)

    # Enviar los datos como texto (JSON) o en formato plano si prefieres
    return jsonify(vuelos_texto)


#----------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/info')
def info_vuelo():
    id_vuelo = request.args.get('id')  # Obtén el id del vuelo desde la URL

    # Conexión a la base de datos
    connection = connect_to_dbA()
    cursor = connection.cursor()

    # Consulta SQL
    query = """
    SELECT 
        v.idVuelo, 
        v.fechaSalida, 
        v.horaSalida, 
        v.fechaActulizacion, 
        v.estado AS estadoVuelo,
        
        -- Información de la ruta comercial (Aeropuerto Origen y Destino)
        ao.descripcion AS aeropuertoOrigen,
        ad.descripcion AS aeropuertoDestino,
        
        -- Nombre de la aerolínea
        a.nombreAerolinea,
        
        -- Información del avión
        av.nombreAvion,

        -- Información de los asientos
        asi.idAsiento,
        asi.numeroAsiento,
        asi.estado AS estadoAsiento,
        asi.fechaActulizacion AS fechaActualizacionAsiento,

        -- Información de la categoría del asiento
        cat.nombreCategoria,           -- Nombre de la categoría
        cat.precioAsiento,             -- Precio del asiento

        -- Agregar el id del asiento junto con la categoría y el estado
        asi.fk_idCategoria AS idCategoriaAsiento,
        asi.fk_idAvion AS idAvionAsiento

    FROM Vuelo v
    -- Relación con RutaComercial
    JOIN RutaComercial rc ON v.RutaComercial_idRutaComercial = rc.idRutaComercial
    JOIN Aeropuerto ao ON rc.fk_idAeropuertoOrigen = ao.idAeropuerto
    JOIN Aeropuerto ad ON rc.fk_idAeropuertoDestino = ad.idAeropuerto

    -- Relación con Aerolínea y Avión
    JOIN Aerolinea a ON v.Aerolinea_idAerolinea = a.idAerolinea
    JOIN Avion av ON v.Avion_idAvion = av.idAvion

    -- Relación con los asientos y su categoría
    JOIN Asiento asi ON av.idAvion = asi.fk_idAvion
    JOIN Categoria cat ON asi.fk_idCategoria = cat.idCategoria

    WHERE v.idVuelo = %s;
    """
    cursor.execute(query, (id_vuelo,))

    vuelo_info = cursor.fetchall()

    connection.close()

    # Pasar los resultados a la plantilla HTML
    return render_template('info.html', vuelo_info=vuelo_info)

#----------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/reservar_asiento', methods=['POST'])
def reservar_asiento():
    try:
        # Obtener los datos del JSON enviado desde el frontend
        data = request.get_json()

        # Extraer los datos del JSON
        id_vuelo = data.get('idVuelo')
        id_asiento = data.get('idAsiento')
        nombre = data.get('nombrePasajero')
        primer_apellido = data.get('primerApellido')
        segundo_apellido = data.get('segundoApellido')
        pasaporte = data.get('pasaporte')
        estado = data.get('estadoAsiento')

        # Conectar a la base de datos
        connection = connect_to_dbA()
        if connection is None:
            return jsonify({"mensaje": "❌ Error al conectar con la base de datos"}), 500

        cursor = connection.cursor()

        # Verificar si el pasajero ya existe en la base de datos
        query_verificar_pasajero = "SELECT idPasajero FROM Pasajero WHERE pasaporte = %s"
        cursor.execute(query_verificar_pasajero, (pasaporte,))
        pasajero_existente = cursor.fetchone()  # Obtiene el primer resultado si existe

        if pasajero_existente:
            mensaje = "✅ El pasajero ya existe. Se actualizó su asiento."
        else:
            # Insertar el pasajero en la tabla Pasajero si no existe
            query_insert_pasajero = """
            INSERT INTO Pasajero (pasaporte, nombre, primerApellido, segundoApellido, fk_idVuelo)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query_insert_pasajero, (pasaporte, nombre, primer_apellido, segundo_apellido, id_vuelo))
            mensaje = "✅ Nuevo pasajero registrado y asiento actualizado."

        # Actualizar el estado del asiento en la tabla Asiento
        query_actualizar_asiento = """
        UPDATE Asiento
        SET estado = %s
        WHERE idAsiento = %s
        """
        cursor.execute(query_actualizar_asiento, (estado, id_asiento))


        # Actualizar la fechaActualizacion en la tabla Vuelo
        query_actualizar_fecha = """
        UPDATE Vuelo
        SET fechaActulizacion = UNIX_TIMESTAMP()
        WHERE idVuelo = %s
        """
        cursor.execute(query_actualizar_fecha, (id_vuelo,))

        # Confirmar los cambios
        connection.commit()
        connection.close()

        # Retornar la respuesta JSON al frontend
        return jsonify({"mensaje": mensaje})

    except Exception as e:
        return jsonify({"mensaje": f"❌ Error en el servidor: {e}"}), 500


#----------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/obtener_pasajero', methods=['POST'])
def obtener_pasajero():
    data = request.get_json()
    id_asiento = data.get('idAsiento')

    conn = connect_to_dbA()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT p.nombre, p.primerApellido, p.segundoApellido, p.pasaporte
        FROM Pasajero p
        JOIN Vuelo v ON p.fk_idVuelo = v.idVuelo
        JOIN Avion av ON v.Avion_idAvion = av.idAvion
        JOIN Asiento a ON a.fk_idAvion = av.idAvion
        WHERE a.idAsiento = %s
        ORDER BY p.idPasajero DESC
        LIMIT 1;
    """

    cursor.execute(query, (id_asiento,))
    pasajero = cursor.fetchone()
    conn.close()

    return jsonify(pasajero if pasajero else {})

@app.route('/info')
def info():
    return render_template('info.html')

#--------------------------------------------------------------------------------------------------------------------------------
@app.route('/aviones')
def aviones():
    try:
        # Obtener los IDs de los aviones
        ids_aviones = obtener_ids_aviones()

        # Pasar los IDs al template HTML
        return render_template('Aviones.html', ids_aviones=ids_aviones)
    except Exception as e:
        print(f"Error al obtener los aviones: {e}")
        return "Error al obtener los aviones.", 500

def obtener_ids_aviones():
    try:
        if db_connection is None or not db_connection.is_connected():
            connect_to_dbA()

        cursor = db_connection.cursor(dictionary=True)
        query = "SELECT idAvion FROM avion;"
        cursor.execute(query)
        resultados = cursor.fetchall()
        cursor.close()

        # Extraer solo los IDs
        ids = [row['idAvion'] for row in resultados]
        return ids
    except Error as e:
        print(f"❌ Error al obtener los aviones: {e}")
        return []


#--------------------------------------------------------------------------------------------------------------------------------

@app.route('/detalle_avion/<int:id_avion>')
def detalle_avion(id_avion):
    try:
        # Verificar conexión a la base de datos
        if db_connection is None or not db_connection.is_connected():
            connect_to_dbA()

        cursor = db_connection.cursor(dictionary=True)

        # Consulta 1: Millas acumuladas
        query_millas = """
            SELECT 
                v.Avion_idAvion AS idAvion,
                SUM(rc.distancia_aproximada) AS total_distancia
            FROM vuelo v
            JOIN RutaComercial rc ON v.RutaComercial_idRutaComercial = rc.idRutaComercial
            WHERE 
                v.Avion_idAvion = %s
                AND v.fechaSalida BETWEEN '2025-01-01' AND '2025-12-31'
            GROUP BY v.Avion_idAvion;
        """
        cursor.execute(query_millas, (id_avion,))
        millas_result = cursor.fetchone()

        # Consulta 2: Estado actual
        query_estado = """
            SELECT 
              v.idVuelo,
              a.nombreAvion,
              ac.nombreAerolinea,
              rc.idRutaComercial,
              ao.descripcion AS origen,
              ad.descripcion AS destino,
              v.fechaSalida,
              v.horaSalida,
              v.fechaLlegada,
              v.horaLlegada,
              CONCAT(v.fechaSalida, ' ', v.horaSalida) AS fechaHoraSalida,
              CONCAT(v.fechaLlegada, ' ', v.horaLlegada) AS fechaHoraLlegada,
              NOW() AS fechaHoraActual,
              CASE 
                WHEN NOW() < CONCAT(v.fechaSalida, ' ', v.horaSalida) THEN 'En tierra (esperando vuelo)'
                WHEN NOW() BETWEEN CONCAT(v.fechaSalida, ' ', v.horaSalida) AND CONCAT(v.fechaLlegada, ' ', v.horaLlegada) THEN 'En vuelo'
                ELSE CONCAT('En destino: ', ad.descripcion)
              END AS estadoAvion
            FROM Vuelo v
            JOIN Avion a ON v.Avion_idAvion = a.idAvion
            JOIN Aerolinea ac ON v.Aerolinea_idAerolinea = ac.idAerolinea
            JOIN RutaComercial rc ON v.RutaComercial_idRutaComercial = rc.idRutaComercial
            JOIN Aeropuerto ao ON rc.fk_idAeropuertoOrigen = ao.idAeropuerto
            JOIN Aeropuerto ad ON rc.fk_idAeropuertoDestino = ad.idAeropuerto
            WHERE a.idAvion = %s
              AND CONCAT(v.fechaSalida, ' ', v.horaSalida) <= NOW()
            ORDER BY CONCAT(v.fechaSalida, ' ', v.horaSalida) DESC
            LIMIT 1;
        """
        cursor.execute(query_estado, (id_avion,))
        estado_result = cursor.fetchone()

        cursor.close()

        return jsonify({
            "idAvion": id_avion,
            "millasTotales": millas_result["total_distancia"] if millas_result else 0,
            "nombreAvion": estado_result["nombreAvion"] if estado_result else "Desconocido",
            "estado": estado_result["estadoAvion"] if estado_result else "Sin información",
            "vuelo": f'{estado_result["origen"]} ➝ {estado_result["destino"]}' if estado_result else "N/A"
        })

    except Exception as e:
        print(f"❌ Error en detalle_avion: {e}")
        return jsonify({"error": "Error al obtener detalles del avión"}), 500


#--------------------------------------------------------------------------------------------------------------------------------


# Ejecutar la consulta al iniciar la aplicación y antes de cada solicitud
@app.before_request
def before_request():
    global db_connection, query_executed  # Declarar las variables globales dentro de la función
    # Asegurarse de que la base de datos esté conectada antes de cada solicitud
    if db_connection is None or not db_connection.is_connected():
        connect_to_dbA()

    # Ejecutar la consulta solo la primera vez
    if not query_executed:
        print("🚀 Ejecutando consulta al iniciar la aplicación...")
        execute_query_and_print()  # Llamar la función para ejecutar la consulta inmediatamente al inicio
        query_executed = True  # Marcar la bandera como True para evitar ejecutar la consulta nuevamente


if __name__ == '__main__':
    app.run(debug=True)