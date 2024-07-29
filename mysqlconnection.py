import mysql.connector as db
import mysql.connector
from mysql.connector import Error


connection = None  # Inicializar la variable connection

try:
    # Conexión a la base de datos
    connection = mysql.connector.connect(
        host='127.0.0.1',          # Por lo general, 'localhost' si estás trabajando localmente
        database='db2', # El nombre de tu base de datos
        user='root',        # Tu usuario de MySQL
        password='ovalle82',  # Tu contraseña de MySQL
        port= "3307"
    )

    if connection.is_connected():
        db_Info = connection.get_server_info()
        print(f"Conectado al servidor MySQL versión {db_Info}")
        cursor = connection.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        print(f"Conectado a la base de datos {record}")

        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        print("Tablas en la base de datos:")
        for table in tables:
            print(table[0])

except Error as e:
    print(f"Error al conectarse a MySQL: {e}")

finally:
    if connection is not None and connection.is_connected():
        cursor.close()
        connection.close()
        print("La conexión a MySQL se ha cerrado")