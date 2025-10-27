import libsql
import envyte

url = envyte.get("URL_DB")
auth_token = envyte.get("API_TOKEN")

# Conexión con Turso
conn = libsql.connect("aadut1", sync_url=url, auth_token=auth_token)
conn.sync()

# --- BORRAR TABLAS ---
conn.execute("PRAGMA foreign_keys = OFF;")
conn.execute("DROP TABLE IF EXISTS FACTURAS;")
conn.execute("DROP TABLE IF EXISTS PRODUCTOS;")
conn.execute("DROP TABLE IF EXISTS TRABAJADORES;")
conn.execute("DROP TABLE IF EXISTS CLIENTES;")
conn.execute("DROP TABLE IF EXISTS TIENDA;")
conn.execute("PRAGMA foreign_keys = ON;")

# --- CREAR TABLAS ---
conn.execute('''
CREATE TABLE TIENDA (
    IDTIENDA INTEGER PRIMARY KEY AUTOINCREMENT,
    NOMBRE VARCHAR(100) NOT NULL,
    DIRECCION VARCHAR(150) NOT NULL,
    COD_POSTAL INTEGER NOT NULL DEFAULT 28941,
    PROFIT REAL DEFAULT 0
);
''')

conn.execute('''
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

conn.execute('''
CREATE TABLE PRODUCTOS (
    IDPRODUCTO INTEGER PRIMARY KEY AUTOINCREMENT,
    IDTIENDA INTEGER NOT NULL,
    NOMBRE VARCHAR(100) NOT NULL,
    DESCRIPCION VARCHAR(200),
    PRECIO REAL NOT NULL,
    STOCK INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (IDTIENDA) REFERENCES TIENDA(IDTIENDA)
);
''')

conn.execute('''
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

conn.execute('''
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
    FOREIGN KEY (IDPRODUCTO) REFERENCES PRODUCTOS(IDPRODUCTO),
    FOREIGN KEY (IDCLIENTE) REFERENCES CLIENTES(IDCLIENTE)
);
''')

# --- TRIGGERS ---
conn.execute("DROP TRIGGER IF EXISTS trg_facturas_check_stock;")
conn.execute('''
CREATE TRIGGER trg_facturas_check_stock
BEFORE INSERT ON FACTURAS
FOR EACH ROW
BEGIN
    SELECT
        CASE
            WHEN (SELECT STOCK FROM PRODUCTOS WHERE IDPRODUCTO = NEW.IDPRODUCTO) IS NULL
                THEN RAISE(ABORT, 'Producto no existe.')
            WHEN (SELECT STOCK FROM PRODUCTOS WHERE IDPRODUCTO = NEW.IDPRODUCTO) < NEW.CANTIDAD
                THEN RAISE(ABORT, 'No hay suficiente stock del producto.')
        END;
END;
''')

conn.execute("DROP TRIGGER IF EXISTS trg_facturas_after_insert;")
conn.execute('''
CREATE TRIGGER trg_facturas_after_insert
AFTER INSERT ON FACTURAS
FOR EACH ROW
BEGIN
    UPDATE FACTURAS
    SET
        PRECIO_UD = (SELECT PRECIO FROM PRODUCTOS WHERE IDPRODUCTO = NEW.IDPRODUCTO),
        GASTO = NEW.CANTIDAD * (SELECT PRECIO FROM PRODUCTOS WHERE IDPRODUCTO = NEW.IDPRODUCTO),
        GASTO_TOTAL = NEW.CANTIDAD * (SELECT PRECIO FROM PRODUCTOS WHERE IDPRODUCTO = NEW.IDPRODUCTO) * (1.0 + NEW.IVA / 100.0)
    WHERE IDFACTURA = NEW.IDFACTURA;

    UPDATE PRODUCTOS
    SET STOCK = STOCK - NEW.CANTIDAD
    WHERE IDPRODUCTO = NEW.IDPRODUCTO;
END;
''')

conn.execute("DROP TRIGGER IF EXISTS trg_update_profit_after_factura;")
conn.execute('''
CREATE TRIGGER trg_update_profit_after_factura
AFTER INSERT ON FACTURAS
FOR EACH ROW
BEGIN
    UPDATE TIENDA
    SET PROFIT = (
        SELECT
            COALESCE(SUM(f.GASTO), 0) - COALESCE((SELECT SUM(SUELDO) FROM TRABAJADORES tr WHERE tr.IDTIENDA = p.IDTIENDA), 0)
        FROM PRODUCTOS p
        LEFT JOIN FACTURAS f ON f.IDPRODUCTO = p.IDPRODUCTO
        WHERE p.IDTIENDA = TIENDA.IDTIENDA
    )
    WHERE IDTIENDA = (SELECT IDTIENDA FROM PRODUCTOS WHERE IDPRODUCTO = NEW.IDPRODUCTO);
END;
''')

# --- INSERTS ---
conn.executemany(
    "INSERT INTO TIENDA (NOMBRE, DIRECCION, COD_POSTAL) VALUES (?, ?, ?);",
    [("Tienda Central", "Calle Mayor 10", 28001),
     ("Sucursal Norte", "Av. de la Paz 45", 28941)]
)

conn.executemany('''
INSERT INTO TRABAJADORES (IDTIENDA, NOMBRE, APE1, APE2, DNI, RESIDENCIA, TELEFONO, CONTACTO, HORARIO, SUELDO)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
''', [
    (1, "Ana", "García", "López", "12345678A", "Madrid", "600111222", "ana@tienda.com", "COMPLETO", 1800.50),
    (2, "Luis", "Martín", "Pérez", "87654321B", "Alcalá", "600333444", "luis@tienda.com", "PARCIAL", 1200.75),
])

conn.executemany('''
INSERT INTO PRODUCTOS (IDTIENDA, NOMBRE, DESCRIPCION, PRECIO, STOCK)
VALUES (?, ?, ?, ?, ?);
''', [
    (1, "Camiseta", "Camiseta de algodón 100%", 15.99, 50),
    (1, "Pantalón", "Pantalón vaquero azul", 29.99, 30),
    (2, "Zapatillas", "Zapatillas deportivas blancas", 45.50, 20)
])

conn.executemany('''
INSERT INTO CLIENTES (NOMBRE, APE1, APE2, RESIDENCIA, TELEFONO, EMAIL, GASTO_TOTAL, VIP)
VALUES (?, ?, ?, ?, ?, ?, ?, ?);
''', [
    ("Carlos", "Ruiz", "Santos", "Madrid", "611223344", "carlos@gmail.com", 0, "NO"),
    ("Laura", "Gómez", "Pérez", "Toledo", "622334455", "laura@gmail.com", 0, "SI")
])

conn.executemany('''
INSERT INTO FACTURAS (IDPRODUCTO, IDCLIENTE, FECHACOMPRA, CANTIDAD)
VALUES (?, ?, ?, ?);
''', [
    (1, 1, "2025-10-27", 2),
    (3, 2, "2025-10-27", 1)
])

conn.execute('''Commit''')


# --- COMPROBACIONES ---
print("\n--- PRODUCTOS ---")
for row in conn.execute("SELECT * FROM PRODUCTOS;").fetchall():
    print(row)

print("\n--- FACTURAS ---")
for row in conn.execute("SELECT * FROM FACTURAS;").fetchall():
    print(row)

print("\n--- TIENDAS (profit) ---")
for row in conn.execute("SELECT * FROM TIENDA;").fetchall():
    print(row)


