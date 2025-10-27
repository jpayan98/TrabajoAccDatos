import libsql
import envyte

url = envyte.get("URL_DB")
auth_token = envyte.get("API_TOKEN")

# Conexión con Turso
conn = libsql.connect("aadut1", sync_url=url, auth_token=auth_token)
conn.sync()

def insertar():
    print("¿Qué quieres crear?")
    print("1. Tienda")
    print("2. Trabajador")
    print("3. Producto")
    print("4. Cliente")
    
    opcion = input("Elige una opción (1-4): ")

    match opcion:
        case "1":
            print("Has elegido crear una Tienda")
            CrearTienda()
        case "2":
            print("Has elegido crear un Trabajador")
            # Función para crear trabajador
        case "3":
            print("Has elegido crear un Producto")
            # Función para crear producto
        case "4":
            print("Has elegido crear un Cliente")
            # Función para crear cliente
        case _:  # caso por defecto si no es 1-4
            print("Opción no válida")

def CrearTienda():
    Nombre = input("que nombre quieres ponerle")
    