import pymysql

# Conexión única a MySQL (misma instancia, distintas BD)
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='admin',  # Reemplaza con tu contraseña real
    cursorclass=pymysql.cursors.DictCursor
)

def sync_table(table_name):
    try:
        with conn.cursor() as cursor:
            # Deshabilitar las restricciones de clave foránea
            cursor.execute("SET foreign_key_checks = 0;")
            
            # Obtener datos desde db_aeropuerto_a.table_name
            cursor.execute(f"SELECT * FROM db_aeropuerto_a.{table_name}")
            rows = cursor.fetchall()

            # Limpiar tabla en db_aeropuerto_c.table_name
            cursor.execute(f"DELETE FROM db_aeropuerto_c.{table_name}")

            # Preparar los datos para la inserción masiva
            if rows:
                # Obtener las columnas de la tabla (suponiendo que todas las filas tienen las mismas columnas)
                columns = ', '.join(rows[0].keys())
                values = ', '.join(['%s'] * len(rows[0]))

                # Crear una lista con los valores de todas las filas
                values_rows = [tuple(row.values()) for row in rows]

                # Insertar los datos en db_aeropuerto_c.table_name
                sql = f"INSERT INTO db_aeropuerto_c.{table_name} ({columns}) VALUES ({values})"
                cursor.executemany(sql, values_rows)

            # Habilitar nuevamente las restricciones de clave foránea
            cursor.execute("SET foreign_key_checks = 1;")

        conn.commit()
        print(f"✅ Sincronización de la tabla {table_name} completada correctamente.")
    except Exception as e:
        print(f"❌ Error durante la sincronización de la tabla {table_name}: {str(e)}")

# Lista de tablas a sincronizar
tables = [
    'vuelo', 
    'aerolinea',
    'aerolinea_has_aeropuerto',
    'aeropuerto',
    'asiento',
    'avion',
    'categoria',
    'ciudad',
    'destino',
    'pais',
    'pasajero',
    'rutacomercial',
    'servidores'
]

# Ejecutar sincronización para todas las tablas
for table in tables:
    sync_table(table)

# Cerrar conexión al final
conn.close()
