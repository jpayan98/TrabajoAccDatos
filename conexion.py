from libsql_client import create_client
from dotenv import load_dotenv
import os

# Cargar variables del archivo .env
load_dotenv()

url = os.getenv("URL_DB")
token = os.getenv("API_TOKEN")

# Conexión con Turso
client = create_client(url,token)
print("Conexión establecida con Turso:", url)

# BORRAR TABLAS
client.execute("DROP TABLE IF EXISTS FACTURAS;")
client.execute("DROP TABLE IF EXISTS PRODUCTOAS;")
client.execute("DROP TABLE IF EXISTS TRABAJADORES;")
client.execute("DROP TABLE IF EXISTS CLIENTES;")
client.execute("DROP TABLE IF EXISTS TIENDA;")

# CREAR TABLAS
client.execute('''
CREATE TABLE TIENDA (
    IDTIENDA INTEGER PRIMARY KEY AUTOINCREMENT,
    NOMBRE VARCHAR(100) NOT NULL,
    DIRECCION VARCHAR(150) NOT NULL,
    COD_POSTAL INTEGER NOT NULL DEFAULT 28941,
    PROFIT REAL DEFAULT 0
);
''')

client.execute('''
CREATE TABLE TRABAJADORES (
    IDTRABAJADOR INTEGER PRIMARY KEY AUTOINCREMENT,
    IDTIENDA INTEGER NOT NULL,
    NOMBRE VARCHAR(20) NOT NULL,
    APE1 VARCHAR(20) NOT NULL,
    APE2 VARCHAR(20),
    DNI VARCHAR(9) NOT NULL UNIQUE,
    RESIDENCIA VARCHAR(100) NOT NULL,
    TELEFONO VARCHAR(15),
    CONTACTO VARCHAR(100),
    HORARIO VARCHAR(20) CHECK(HORARIO IN ('COMPLETO','PARCIAL')),
    SUELDO REAL,
    FOREIGN KEY (IDTIENDA) REFERENCES TIENDA(IDTIENDA)
);
''')

client.execute('''
CREATE TABLE PRODUCTOAS (
    IDPRODUCTO INTEGER PRIMARY KEY AUTOINCREMENT,
    IDTIENDA INTEGER NOT NULL,
    NOMBRE VARCHAR(100) NOT NULL,
    DESCRIPCION VARCHAR(200),
    PRECIO REAL NOT NULL,
    STOCK INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (IDTIENDA) REFERENCES TIENDA(IDTIENDA)
);
''')

client.execute('''
CREATE TABLE CLIENTES (
    IDCLIENTE INTEGER PRIMARY KEY AUTOINCREMENT,
    NOMBRE VARCHAR(20) NOT NULL,
    APE1 VARCHAR(20) NOT NULL,
    APE2 VARCHAR(20),
    RESIDENCIA VARCHAR(100) NOT NULL,
    TELEFONO VARCHAR(9) CHECK(LENGTH(TELEFONO)=9),
    EMAIL VARCHAR(100) CHECK(EMAIL LIKE '%@%.%'),
    GASTO_TOTAL REAL DEFAULT 0,
    VIP VARCHAR(2) CHECK(VIP IN ('SI','NO'))
);
''')

client.execute('''
CREATE TABLE FACTURAS (
    IDFACTURA INTEGER PRIMARY KEY AUTOINCREMENT,
    IDPRODUCTO INTEGER NOT NULL,
    IDCLIENTE INTEGER NOT NULL,
    FECHACOMPRA TEXT NOT NULL,
    PRECIO_UD REAL,
    CANTIDAD INTEGER CHECK (CANTIDAD > 0),
    GASTO REAL,
    IVA INTEGER DEFAULT 21 NOT NULL,
    GASTO_TOTAL REAL,
    FOREIGN KEY (IDPRODUCTO) REFERENCES PRODUCTOAS(IDPRODUCTO),
    FOREIGN KEY (IDCLIENTE) REFERENCES CLIENTES(IDCLIENTE)
);
''')

# TRIGGERS
client.execute("DROP TRIGGER IF EXISTS trg_facturas_check_stock;")
client.execute('''
CREATE TRIGGER trg_facturas_check_stock
BEFORE INSERT ON FACTURAS
FOR EACH ROW
BEGIN
    SELECT
        CASE
            WHEN (SELECT STOCK FROM PRODUCTOAS WHERE IDPRODUCTO = NEW.IDPRODUCTO) IS NULL
                THEN RAISE(ABORT, 'Producto no existe.')
            WHEN (SELECT STOCK FROM PRODUCTOAS WHERE IDPRODUCTO = NEW.IDPRODUCTO) < NEW.CANTIDAD
                THEN RAISE(ABORT, 'No hay suficiente stock del producto.')
        END;
END;
''')

client.execute("DROP TRIGGER IF EXISTS trg_facturas_after_insert;")
client.execute('''
CREATE TRIGGER trg_facturas_after_insert
AFTER INSERT ON FACTURAS
FOR EACH ROW
BEGIN
    UPDATE FACTURAS
    SET
        PRECIO_UD = (SELECT PRECIO FROM PRODUCTOAS WHERE IDPRODUCTO = NEW.IDPRODUCTO),
        GASTO = NEW.CANTIDAD * (SELECT PRECIO FROM PRODUCTOAS WHERE IDPRODUCTO = NEW.IDPRODUCTO),
        GASTO_TOTAL = NEW.CANTIDAD * (SELECT PRECIO FROM PRODUCTOAS WHERE IDPRODUCTO = NEW.IDPRODUCTO) * (1.0 + NEW.IVA / 100.0)
    WHERE IDFACTURA = NEW.IDFACTURA;

    UPDATE PRODUCTOAS
    SET STOCK = STOCK - NEW.CANTIDAD
    WHERE IDPRODUCTO = NEW.IDPRODUCTO;
END;
''')

client.execute("DROP TRIGGER IF EXISTS trg_update_profit_after_factura;")
client.execute('''
CREATE TRIGGER trg_update_profit_after_factura
AFTER INSERT ON FACTURAS
FOR EACH ROW
BEGIN
    UPDATE TIENDA
    SET PROFIT = (
        SELECT
            COALESCE(SUM(f.GASTO), 0) - COALESCE((SELECT SUM(SUELDO) FROM TRABAJADORES tr WHERE tr.IDTIENDA = p.IDTIENDA), 0)
        FROM PRODUCTOAS p
        LEFT JOIN FACTURAS f ON f.IDPRODUCTO = p.IDPRODUCTO
        WHERE p.IDTIENDA = TIENDA.IDTIENDA
    )
    WHERE IDTIENDA = (SELECT IDTIENDA FROM PRODUCTOAS WHERE IDPRODUCTO = NEW.IDPRODUCTO);
END;
''')

# INSERTS
client.execute_many(
    "INSERT INTO TIENDA (NOMBRE, DIRECCION, COD_POSTAL) VALUES (?, ?, ?);",
    [("Tienda Central", "Calle Mayor 10", 28001),
     ("Sucursal Norte", "Av. de la Paz 45", 28941)]
)

client.execute_many('''
INSERT INTO TRABAJADORES (IDTIENDA, NOMBRE, APE1, APE2, DNI, RESIDENCIA, TELEFONO, CONTACTO, HORARIO, SUELDO)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
''', [
    (1, "Ana", "García", "López", "12345678A", "Madrid", "600111222", "ana@tienda.com", "COMPLETO", 1800.50),
    (2, "Luis", "Martín", "Pérez", "87654321B", "Alcalá", "600333444", "luis@tienda.com", "PARCIAL", 1200.75),
])

client.execute_many('''
INSERT INTO PRODUCTOAS (IDTIENDA, NOMBRE, DESCRIPCION, PRECIO, STOCK)
VALUES (?, ?, ?, ?, ?);
''', [
    (1, "Camiseta", "Camiseta de algodón 100%", 15.99, 50),
    (1, "Pantalón", "Pantalón vaquero azul", 29.99, 30),
    (2, "Zapatillas", "Zapatillas deportivas blancas", 45.50, 20)
])

client.execute_many('''
INSERT INTO CLIENTES (NOMBRE, APE1, APE2, RESIDENCIA, TELEFONO, EMAIL, GASTO_TOTAL, VIP)
VALUES (?, ?, ?, ?, ?, ?, ?, ?);
''', [
    ("Carlos", "Ruiz", "Santos", "Madrid", "611223344", "carlos@gmail.com", 0, "NO"),
    ("Laura", "Gómez", "Pérez", "Toledo", "622334455", "laura@gmail.com", 0, "SI")
])

client.execute_many('''
INSERT INTO FACTURAS (IDPRODUCTO, IDCLIENTE, FECHACOMPRA, CANTIDAD)
VALUES (?, ?, ?, ?);
''', [
    (1, 1, "2025-10-27", 2),
    (3, 2, "2025-10-27", 1)
])

# COMPROBACIONES
print("\n--- PRODUCTOS ---")
for row in client.execute("SELECT * FROM PRODUCTOAS;").rows:
    print(row)

print("\n--- FACTURAS ---")
for row in client.execute("SELECT * FROM FACTURAS;").rows:
    print(row)

print("\n--- TIENDAS (profit) ---")
for row in client.execute("SELECT * FROM TIENDA;").rows:
    print(row)

