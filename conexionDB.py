import libsql
import envyte

"""Crea y devuelve la conexión con Turso."""
url = envyte.get("URL_DB")
auth_token = envyte.get("API_TOKEN")
conn = libsql.connect("aadut1", sync_url=url, auth_token=auth_token)
conn.sync()
