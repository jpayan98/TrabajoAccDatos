import sqlite3
import libsql
import envyte

print("=== SELECCIONA MODO DE CONEXIÓN ===")
print("1. Base de datos local (SQLite)")
print("2. Base de datos en la nube (Turso)")
opcion = input("Opción: ")

match opcion:
    case "1":
        conn = sqlite3.connect("tienda.db")
        print("💾 Conectado a base de datos local SQLite.")
        PyC=";"
    case "2":
        url = envyte.get("URL_DB")
        auth_token = envyte.get("API_TOKEN")
        conn = libsql.connect("aadut1", sync_url=url, auth_token=auth_token)
        PyC=""
        conn.sync()
        print("🌐 Conectado a base de datos Turso.")
    case _:
        print("❌ Opción no válida. Usando SQLite por defecto.")
        conn = sqlite3.connect("tienda.db")
        