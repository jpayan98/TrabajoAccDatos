import sqlite3
import libsql
import envyte

url = envyte.get("URL_DB")
auth_token = envyte.get("API_TOKEN")

# Conexión con Turso
conn = libsql.connect("aadut1", sync_url=url, auth_token=auth_token)
conn.sync()