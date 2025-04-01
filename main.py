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
    results = execute_query_and_print()  # Ejecuta la consulta para obtener los resultados
    airports = {  # Crear un diccionario de aeropuertos de origen y destino
        "origen": [],
        "destino": []
    }
    
    # Llenar los aeropuertos de origen y destino
    for result in results:
        airports["origen"].append(result['Descripcion_Aeropuerto_Origen'])
        airports["destino"].append(result['Descripcion_Aeropuerto_Destino'])

    return render_template('index.html', airports=airports)  # Pasar los datos a index.html


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
    if continent in ["Europa", "Asia", "África"]:
        # Conectar a MySQL (dbaeropuerto_a)
        response["message"] = f"Conectado a dbaeropuerto_a en (MYSQL-Europa) ({continent})."
        connect_to_dbA()  # Conectar a dbaeropuerto_a

    elif continent == "Norteamérica":
        # Conectar a Firebase (dbaeropuerto_b)
        response["message"] = "Conectado a dbaeropuerto_b en Firebase (Norteamérica)."
        connect_to_dbA()  # Conectar a dbaeropuerto_b

    elif continent == "Sudamérica":
        # Conectar a MySQL (dbaeropuerto_c)
        response["message"] = "Conectado a dbaeropuerto_c en MySQL (Sudamérica)."
        connect_to_dbA()  # Conectar a dbaeropuerto_c

    else:
        response["message"] = "No hay servidores disponibles para este continente."

    return jsonify(response)


# Ejecutar la consulta
def execute_query_and_print():
    try:
        if db_connection is None or not db_connection.is_connected():
            print("🔌 Intentando conectar a la base de datos...")
            connect_to_dbA()  # Conectar a la base de datos si no está conectado

        cursor = db_connection.cursor(dictionary=True)
        # Nueva consulta con JOINs
        query = """
        SELECT 
            rc.idRutaComercial, 
            aeo.descripcion AS Descripcion_Aeropuerto_Origen, 
            aed.descripcion AS Descripcion_Aeropuerto_Destino 
        FROM 
            RutaComercial rc 
        JOIN 
            Aeropuerto aeo ON rc.fk_idAeropuertoOrigen = aeo.idAeropuerto 
        JOIN 
            Aeropuerto aed ON rc.fk_idAeropuertoDestino = aed.idAeropuerto;
        """
        print(f"Ejecutando consulta: {query}")
        cursor.execute(query)
        results = cursor.fetchall()  # Obtener todos los resultados de la consulta
        print(f"Resultados obtenidos: {results}")  # Imprimir los resultados

        cursor.close()  # Cerrar el cursor después de la consulta
        return results  # Devolver los resultados para la respuesta
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


#----------------------------------------------------------------------------------------------------------------------------------------------

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