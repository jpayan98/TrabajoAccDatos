import sqlite3

with sqlite3.connect("practicatursojesusjuangarci.db") as conn:
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS TIENDA")
    cursor.execute("DROP TABLE IF EXISTS TRABAJADORES")
    cursor.execute("DROP TABLE IF EXISTS PRODUCTOAS")
    cursor.execute("DROP TABLE IF EXISTS CLIENTES")
    cursor.execute("DROP TABLE IF EXISTS FACTURASS")

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print(cursor.fetchall())


    cursor.execute('''CREATE TABLE IF NOT EXISTS empleados (
                    id INTEGER PRIMARY KEY,
                   name TEXT NOT NULL,
                   salary REAL NOT NULL
                   )''')
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print(cursor.fetchall())

    #cursor.execute("INSERT INTO empleados (name, salary) VALUES ('Juan', 20000), ('Maria', 25000)")
    conn.commit()
    
    
    cursor.execute("SELECT * FROM empleados")
    
    for r in cursor.fetchall():
        print(r)