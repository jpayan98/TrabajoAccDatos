import sqlite3

DB_FILE = "practicatursojesusjuangarci.db"

with sqlite3.connect(DB_FILE) as conn:
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    # BORRAR TABLAS (orden por dependencias)
    cursor.execute("DROP TABLE IF EXISTS FACTURAS;")
    cursor.execute("DROP TABLE IF EXISTS PRODUCTOAS;")
    cursor.execute("DROP TABLE IF EXISTS TRABAJADORES;")
    cursor.execute("DROP TABLE IF EXISTS CLIENTES;")
    cursor.execute("DROP TABLE IF EXISTS TIENDA;")

    # CREAR TABLAS
    cursor.execute('''
    CREATE TABLE TIENDA (
        IDTIENDA INTEGER PRIMARY KEY AUTOINCREMENT,
        NOMBRE VARCHAR(100) NOT NULL,
        DIRECCION VARCHAR(150) NOT NULL,
        COD_POSTAL INTEGER NOT NULL DEFAULT 28941,
        PROFIT REAL DEFAULT 0
    );
    ''')

    cursor.execute('''
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

    cursor.execute('''
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

    cursor.execute('''
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

    cursor.execute('''
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

    # TRIGGERS (compatibles con SQLite)

    # 1) BEFORE INSERT: comprueba stock y aborta si no hay suficiente
    cursor.execute("DROP TRIGGER IF EXISTS trg_facturas_check_stock;")
    cursor.execute('''
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

    # 2) AFTER INSERT: calcula PRECIO_UD, GASTO, GASTO_TOTAL y resta stock
    cursor.execute("DROP TRIGGER IF EXISTS trg_facturas_after_insert;")
    cursor.execute('''
    CREATE TRIGGER trg_facturas_after_insert
    AFTER INSERT ON FACTURAS
    FOR EACH ROW
    BEGIN
        -- Actualiza los campos calculados en la propia factura
        UPDATE FACTURAS
        SET
            PRECIO_UD = (SELECT PRECIO FROM PRODUCTOAS WHERE IDPRODUCTO = NEW.IDPRODUCTO),
            GASTO = NEW.CANTIDAD * (SELECT PRECIO FROM PRODUCTOAS WHERE IDPRODUCTO = NEW.IDPRODUCTO),
            GASTO_TOTAL = NEW.CANTIDAD * (SELECT PRECIO FROM PRODUCTOAS WHERE IDPRODUCTO = NEW.IDPRODUCTO) * (1.0 + NEW.IVA / 100.0)
        WHERE IDFACTURA = NEW.IDFACTURA;

        -- Resta el stock del producto
        UPDATE PRODUCTOAS
        SET STOCK = STOCK - NEW.CANTIDAD
        WHERE IDPRODUCTO = NEW.IDPRODUCTO;
    END;
    ''')

    # 3) AFTER INSERT/UPDATE/DELETE en FACTURAS: recalcula PROFIT de la tienda afectada
    # Nota: SQLite no soporta MERGE ni UPDATE ... FROM. Recalculamos por tienda afectada.
    cursor.execute("DROP TRIGGER IF EXISTS trg_update_profit_after_factura;")
    cursor.execute('''
    CREATE TRIGGER trg_update_profit_after_factura
    AFTER INSERT ON FACTURAS
    FOR EACH ROW
    BEGIN
        -- Recalcula profit solo para la tienda del producto insertado
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
    # Para UPDATE o DELETE en FACTURAS deberías crear triggers similares que llamen la misma subconsulta.
    # (Por simplicidad aquí añadimos solo el AFTER INSERT; si quieres, agrego los de UPDATE y DELETE.)

    # DATOS DE PRUEBA (coherentes con columnas)
    cursor.executemany(
        "INSERT INTO TIENDA (NOMBRE, DIRECCION, COD_POSTAL) VALUES (?, ?, ?);",
        [("Tienda Central", "Calle Mayor 10", 28001),
         ("Sucursal Norte", "Av. de la Paz 45", 28941)]
    )

    cursor.executemany('''
        INSERT INTO TRABAJADORES (IDTIENDA, NOMBRE, APE1, APE2, DNI, RESIDENCIA, TELEFONO, CONTACTO, HORARIO, SUELDO)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    ''', [
        (1, "Ana", "García", "López", "12345678A", "Madrid", "600111222", "ana@tienda.com", "COMPLETO", 1800.50),
        (2, "Luis", "Martín", "Pérez", "87654321B", "Alcalá", "600333444", "luis@tienda.com", "PARCIAL", 1200.75),
    ])

    cursor.executemany('''
        INSERT INTO PRODUCTOAS (IDTIENDA, NOMBRE, DESCRIPCION, PRECIO, STOCK)
        VALUES (?, ?, ?, ?, ?);
    ''', [
        (1, "Camiseta", "Camiseta de algodón 100%", 15.99, 50),
        (1, "Pantalón", "Pantalón vaquero azul", 29.99, 30),
        (2, "Zapatillas", "Zapatillas deportivas blancas", 45.50, 20)
    ])

    cursor.executemany('''
        INSERT INTO CLIENTES (NOMBRE, APE1, APE2, RESIDENCIA, TELEFONO, EMAIL, GASTO_TOTAL, VIP)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    ''', [
        ("Carlos", "Ruiz", "Santos", "Madrid", "611223344", "carlos@gmail.com", 0, "NO"),
        ("Laura", "Gómez", "Pérez", "Toledo", "622334455", "laura@gmail.com", 0, "SI")
    ])

    # Insertar facturas de prueba (estas activarán triggers)
    cursor.executemany('''
        INSERT INTO FACTURAS (IDPRODUCTO, IDCLIENTE, FECHACOMPRA, CANTIDAD)
        VALUES (?, ?, ?, ?);
    ''', [
        (1, 1, "2025-10-27", 2),   # válido, restará stock de producto 1
        (3, 2, "2025-10-27", 1)    # válido, restará stock de producto 3
    ])

    # COMPROBACIONES
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print("Tablas en la BD:", cursor.fetchall())

    print("\n--- PRODUCTOS ---")
    for r in cursor.execute("SELECT * FROM PRODUCTOAS;"):
        print(r)

    print("\n--- FACTURAS ---")
    for r in cursor.execute("SELECT * FROM FACTURAS;"):
        print(r)

    print("\n--- TIENDAS (profit) ---")
    for r in cursor.execute("SELECT * FROM TIENDA;"):
        print(r)

    print("\n✅ Script ejecutado correctamente.")


