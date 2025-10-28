import libsql
import envyte
import sys

url = envyte.get("URL_DB")
auth_token = envyte.get("API_TOKEN")

# Conexión con Turso
conn = libsql.connect("aadut1", sync_url=url, auth_token=auth_token)
conn.sync()

def menu_principal():
    while True:
        print("\n" + "="*50)
        print("          SISTEMA DE GESTIÓN DE TIENDAS")
        print("="*50)
        print("1. ➕ Insertar datos")
        print("2. 👁️  Consultar datos")
        print("3. ✏️  Actualizar datos")
        print("4. 🗑️  Eliminar datos")
        print("5. ❌ Salir del programa")
        print("="*50)

        opcion = input("Elige una opción (1-5): ")

        match opcion:
            case "1":
                menu_insertar()
            case "2":
                menu_consultar()
            case "3":
                menu_actualizar()
            case "4":
                menu_eliminar()
            case "5":
                print("👋 Saliendo del programa...")
                conn.close()
                sys.exit(0)
            case _:
                print("❌ Opción no válida. Inténtalo de nuevo.")

# ==================== FUNCIONES DE INSERCIÓN ====================

def InsertarTienda():
    nombre = input("Nombre de la tienda: ")
    direccion = input("Dirección de la tienda: ")
    cod_postal = input("Código postal (por defecto 28941): ") or "28941"

    try:
        conn.execute(
            "INSERT INTO TIENDA (NOMBRE, DIRECCION, COD_POSTAL) VALUES (?, ?, ?);",
            (nombre, direccion, int(cod_postal))
        )
        conn.commit()
        print(f"✅ Tienda '{nombre}' creada correctamente.\n")
        # Mostrar tienda creada de forma segura
        for row in conn.execute("SELECT * FROM TIENDA WHERE NOMBRE = ?;", (nombre,)).fetchall():
            print(row)
    except Exception as e:
        print("❌ Error al crear la tienda:", e)

def InsertarTrabajador():
    print("\n--- Tiendas disponibles ---")
    tiendas = conn.execute("SELECT IDTIENDA, NOMBRE FROM TIENDA;").fetchall()
    for tienda in tiendas:
        print(f"ID: {tienda[0]} - {tienda[1]}")
    
    try:
        idtienda = int(input("\nID de la tienda: "))
        nombre = input("Nombre: ")
        ape1 = input("Primer apellido: ")
        ape2 = input("Segundo apellido (opcional): ") or None
        dni = input("DNI: ")
        residencia = input("Residencia: ")
        telefono = input("Teléfono (opcional): ") or None
        contacto = input("Contacto (email): ")
        horario = input("Horario (COMPLETO/PARCIAL): ").upper()
        sueldo = float(input("Sueldo: "))

        conn.execute('''
        INSERT INTO TRABAJADORES (IDTIENDA, NOMBRE, APE1, APE2, DNI, RESIDENCIA, TELEFONO, CONTACTO, HORARIO, SUELDO)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        ''', (idtienda, nombre, ape1, ape2, dni, residencia, telefono, contacto, horario, sueldo))
        conn.commit()
        print(f"✅ Trabajador '{nombre} {ape1}' creado correctamente.\n")
        
        # Mostrar trabajador creado de forma segura
        for row in conn.execute("SELECT * FROM TRABAJADORES WHERE DNI = ?;", (dni,)).fetchall():
            print(row)
    except Exception as e:
        print("❌ Error al crear el trabajador:", e)

def InsertarProducto():
    print("\n--- Tiendas disponibles ---")
    tiendas = conn.execute("SELECT IDTIENDA, NOMBRE FROM TIENDA;").fetchall()
    for tienda in tiendas:
        print(f"ID: {tienda[0]} - {tienda[1]}")
    
    try:
        idtienda = int(input("\nID de la tienda: "))
        nombre = input("Nombre del producto: ")
        descripcion = input("Descripción: ") or None
        precio = float(input("Precio: "))
        stock = int(input("Stock: "))

        conn.execute('''
        INSERT INTO PRODUCTOS (IDTIENDA, NOMBRE, DESCRIPCION, PRECIO, STOCK)
        VALUES (?, ?, ?, ?, ?);
        ''', (idtienda, nombre, descripcion, precio, stock))
        conn.commit()
        print(f"✅ Producto '{nombre}' creado correctamente.\n")
        
        # Mostrar producto creado de forma segura
        for row in conn.execute("SELECT * FROM PRODUCTOS WHERE NOMBRE = ? AND IDTIENDA = ?;", (nombre, idtienda)).fetchall():
            print(row)
    except Exception as e:
        print("❌ Error al crear el producto:", e)

def InsertarCliente():
    try:
        nombre = input("Nombre: ")
        ape1 = input("Primer apellido: ")
        ape2 = input("Segundo apellido (opcional): ") or None
        residencia = input("Residencia: ")
        
        # Validar teléfono
        while True:
            telefono = input("Teléfono (9 dígitos): ")
            if len(telefono) == 9 and telefono.isdigit():
                break
            print("❌ El teléfono debe tener exactamente 9 dígitos.")
        
        # Validar email
        while True:
            email = input("Email: ")
            if '@' in email and '.' in email:
                break
            print("❌ Email debe contener '@' y '.'")
        
        # Validar VIP
        while True:
            vip = input("VIP (SI/NO): ").upper()
            if vip in ['SI', 'NO']:
                break
            print("❌ VIP debe ser 'SI' o 'NO'")

        conn.execute('''
        INSERT INTO CLIENTES (NOMBRE, APE1, APE2, RESIDENCIA, TELEFONO, EMAIL, VIP, GASTO_TOTAL)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        ''', (nombre, ape1, ape2, residencia, telefono, email, vip, 0.0))
        conn.commit()
        print(f"✅ Cliente '{nombre} {ape1}' creado correctamente.\n")
        
        # Mostrar cliente creado de forma segura
        print("📋 Cliente creado:")
        for row in conn.execute("SELECT * FROM CLIENTES WHERE EMAIL = ?;", (email,)).fetchall():
            print(row)
            
    except Exception as e:
        print("❌ Error al crear el cliente:", e)

def InsertarFactura():
    print("\n--- Productos disponibles ---")
    productos = conn.execute("SELECT IDPRODUCTO, NOMBRE, PRECIO, STOCK FROM PRODUCTOS;").fetchall()
    for producto in productos:
        print(f"ID: {producto[0]} - {producto[1]} - Precio: {producto[2]}€ - Stock: {producto[3]}")
    
    print("\n--- Clientes disponibles ---")
    clientes = conn.execute("SELECT IDCLIENTE, NOMBRE, APE1 FROM CLIENTES;").fetchall()
    for cliente in clientes:
        print(f"ID: {cliente[0]} - {cliente[1]} {cliente[2]}")
    
    try:
        idproducto = int(input("\nID del producto: "))
        idcliente = int(input("ID del cliente: "))
        fecha = input("Fecha de compra (YYYY-MM-DD): ")
        cantidad = int(input("Cantidad: "))
        iva = input("IVA (por defecto 21): ") or "21"

        # Verificar stock antes de insertar
        stock_actual = conn.execute("SELECT STOCK FROM PRODUCTOS WHERE IDPRODUCTO = ?", (idproducto,)).fetchone()
        if not stock_actual:
            print("❌ Error: El producto no existe.")
            return
        if stock_actual[0] < cantidad:
            print(f"❌ Error: Stock insuficiente. Stock actual: {stock_actual[0]}")
            return

        conn.execute('''
        INSERT INTO FACTURAS (IDPRODUCTO, IDCLIENTE, FECHACOMPRA, CANTIDAD, IVA)
        VALUES (?, ?, ?, ?, ?);
        ''', (idproducto, idcliente, fecha, cantidad, int(iva)))
        conn.commit()
        print("✅ Factura creada correctamente.\n")
        
        # Obtener la última factura insertada con índices correctos
        factura = conn.execute('''
        SELECT 
            f.IDFACTURA, f.IDPRODUCTO, f.IDCLIENTE, f.FECHACOMPRA, 
            f.PRECIO_UD, f.CANTIDAD, f.GASTO, f.IVA, f.GASTO_TOTAL,
            p.NOMBRE as producto_nombre, 
            c.NOMBRE || ' ' || c.APE1 as cliente_nombre
        FROM FACTURAS f
        JOIN PRODUCTOS p ON f.IDPRODUCTO = p.IDPRODUCTO
        JOIN CLIENTES c ON f.IDCLIENTE = c.IDCLIENTE
        WHERE f.IDFACTURA = (SELECT MAX(IDFACTURA) FROM FACTURAS)
        ''').fetchone()
        
        if factura:
            print("📄 Factura creada:")
            print(f"   ID Factura: {factura[0]}")
            print(f"   Producto: {factura[9]} (ID: {factura[1]})")
            print(f"   Cliente: {factura[10]} (ID: {factura[2]})")
            print(f"   Fecha: {factura[3]}")
            print(f"   Precio unidad: {factura[4]}€")
            print(f"   Cantidad: {factura[5]}")
            print(f"   Gasto (sin IVA): {factura[6]}€")
            print(f"   IVA: {factura[7]}%")
            print(f"   Gasto Total (con IVA): {factura[8]}€")
        
    except Exception as e:
        print("❌ Error al crear la factura:", e)

# ==================== MENÚ INSERTAR ====================
def menu_insertar():
    while True:
        print("\n" + "="*40)
        print("           INSERTAR DATOS")
        print("="*40)
        print("1. 🏪 Insertar Tienda")
        print("2. 👨‍💼 Insertar Trabajador")
        print("3. 📦 Insertar Producto")
        print("4. 👥 Insertar Cliente")
        print("5. 🧾 Insertar Factura")
        print("6. ↩️  Volver al menú principal")
        print("="*40)
        opcion = input("Elige una opción (1-6): ")
        match opcion:
            case "1":
                print("Has elegido crear una Tienda")
                InsertarTienda()
            case "2":
                print("Has elegido crear un Trabajador")
                InsertarTrabajador()
            case "3":
                print("Has elegido crear un Producto")
                InsertarProducto()
            case "4":
                print("Has elegido crear un Cliente")
                InsertarCliente()
            case "5":
                print("Has elegido crear una Factura")
                InsertarFactura()
            case "6":
                break
            case _:
                print("❌ Opción no válida. Inténtalo de nuevo.")

# ==================== MENÚ CONSULTAR ====================
def menu_consultar():
    while True:
        print("\n" + "="*40)
        print("           CONSULTAR DATOS")
        print("="*40)
        print("1. 🏪 Consultar Tiendas")
        print("2. 👨‍💼 Consultar Trabajadores")
        print("3. 📦 Consultar Productos")
        print("4. 👥 Consultar Clientes")
        print("5. 🧾 Consultar Facturas")
        print("6. 🔍 Consulta personalizada")
        print("7. ↩️  Volver al menú principal")
        print("="*40)
        opcion = input("Elige una opción (1-7): ")
        match opcion:
            case "1":
                consultar_tiendas()
            case "2":
                consultar_trabajadores()
            case "3":
                consultar_productos()
            case "4":
                consultar_clientes()
            case "5":
                consultar_facturas()
            case "6":
                consulta_personalizada()
            case "7":
                break
            case _:
                print("❌ Opción no válida. Inténtalo de nuevo.")

def consultar_tiendas():
    print("\n--- TIENDAS ---")
    try:
        tiendas = conn.execute("SELECT * FROM TIENDA;").fetchall()
        if not tiendas:
            print("No hay tiendas registradas.")
            return
        
        for tienda in tiendas:
            print(f"ID: {tienda[0]} | Nombre: {tienda[1]} | Dirección: {tienda[2]} | Código Postal: {tienda[3]} | Profit: {tienda[4]}€")
    except Exception as e:
        print("❌ Error al consultar tiendas:", e)

def consultar_trabajadores():
    print("\n--- TRABAJADORES ---")
    try:
        trabajadores = conn.execute('''
        SELECT t.*, ti.NOMBRE as tienda_nombre 
        FROM TRABAJADORES t 
        JOIN TIENDA ti ON t.IDTIENDA = ti.IDTIENDA;
        ''').fetchall()
        
        if not trabajadores:
            print("No hay trabajadores registrados.")
            return
        
        for trab in trabajadores:
            print(f"ID: {trab[0]} | Tienda: {trab[9]} | Nombre: {trab[2]} {trab[3]} {trab[4] or ''} | DNI: {trab[5]} | Tel: {trab[7]} | Sueldo: {trab[10]}€")
    except Exception as e:
        print("❌ Error al consultar trabajadores:", e)

def consultar_productos():
    print("\n--- PRODUCTOS ---")
    try:
        productos = conn.execute('''
        SELECT p.*, t.NOMBRE as tienda_nombre 
        FROM PRODUCTOS p 
        JOIN TIENDA t ON p.IDTIENDA = t.IDTIENDA;
        ''').fetchall()
        
        if not productos:
            print("No hay productos registrados.")
            return
        
        for prod in productos:
            print(f"ID: {prod[0]} | Tienda: {prod[6]} | Nombre: {prod[2]} | Precio: {prod[4]}€ | Stock: {prod[5]} | Desc: {prod[3]}")
    except Exception as e:
        print("❌ Error al consultar productos:", e)

def consultar_clientes():
    print("\n--- CLIENTES ---")
    try:
        clientes = conn.execute("SELECT * FROM CLIENTES;").fetchall()
        if not clientes:
            print("No hay clientes registrados.")
            return
        
        for cliente in clientes:
            print(f"ID: {cliente[0]} | Nombre: {cliente[1]} {cliente[2]} {cliente[3] or ''} | Tel: {cliente[5]} | Email: {cliente[6]} | Gasto Total: {cliente[7]}€ | VIP: {cliente[8]}")
    except Exception as e:
        print("❌ Error al consultar clientes:", e)

def consultar_facturas():
    print("\n--- FACTURAS ---")
    try:
        facturas = conn.execute('''
        SELECT f.*, p.NOMBRE as producto_nombre, c.NOMBRE || ' ' || c.APE1 as cliente_nombre
        FROM FACTURAS f
        JOIN PRODUCTOS p ON f.IDPRODUCTO = p.IDPRODUCTO
        JOIN CLIENTES c ON f.IDCLIENTE = c.IDCLIENTE
        ORDER BY f.FECHACOMPRA DESC;
        ''').fetchall()
        
        if not facturas:
            print("No hay facturas registradas.")
            return
        
        for fact in facturas:
            print(f"ID: {fact[0]} | Fecha: {fact[3]} | Producto: {fact[9]} | Cliente: {fact[10]} | Cantidad: {fact[5]} | Total: {fact[8]}€")
    except Exception as e:
        print("❌ Error al consultar facturas:", e)

def consulta_personalizada():
    """
    Construye y ejecuta un SELECT guiado por consola.
    - Pide tablas 1 a 1 (ENTER vacío pasa a campos).
    - Si hay >1 tabla, pregunta cómo unirlas (NATURAL JOIN / coma / expresión manual).
    - Pide campos (vacío -> *) y WHERE opcional.
    Usa la conexión global `conn`.
    """
    print("\n=== CONSULTA SQL INTERACTIVA ===")
    print("Introduce los nombres de las tablas UNA a UNA. Pulsa ENTER vacío para pasar al siguiente paso.\n")

    # --- Recoger tablas una a una ---
    tablas_lista = []
    contador = 1
    while True:
        entrada = input(f"Tabla #{contador} (ENTER vacío para terminar): ").strip()
        if entrada == "":
            break
        tablas_lista.append(entrada)
        contador += 1

    if not tablas_lista:
        print("❌ No se ha indicado ninguna tabla. Abortando consulta.")
        return

    # --- Si hay varias tablas, elegir método de unión ---
    if len(tablas_lista) > 1:
        print("\nHas introducido varias tablas:", ", ".join(tablas_lista))
        print("Elige cómo unirlas:")
        print("  1) NATURAL JOIN (recomendado si las tablas tienen columnas con mismo nombre)")
        print("  2) COMA (producto cartesiano)")
        print("  3) ESCRIBIR EXPRESIÓN JOIN manual (por ejemplo: 'PRODUCTOS p INNER JOIN FACTURAS f ON p.IDPRODUCTO=f.IDPRODUCTO')")
        modo_union = input("Opción (1/2/3) [1]: ").strip() or "1"

        if modo_union == "1":
            tablas_expr = " NATURAL JOIN ".join(tablas_lista)
        elif modo_union == "2":
            tablas_expr = ", ".join(tablas_lista)
        elif modo_union == "3":
            tablas_expr = input("Escribe la expresión JOIN completa: ").strip()
            if not tablas_expr:
                print("❌ Expresión JOIN vacía. Abortando.")
                return
        else:
            print("Opción inválida, usando NATURAL JOIN por defecto.")
            tablas_expr = " NATURAL JOIN ".join(tablas_lista)
    else:
        tablas_expr = tablas_lista[0]

    # --- Campos ---
    campos = input("\nIngresa los nombres de los campos (formato: TABLA.CAMPO) o deja vacío para todos (*): ").strip()
    if not campos:
        campos = "*"

    # --- WHERE ---
    where = input("Ingresa condición WHERE (ej: PRECIO>20 AND NOMBRE LIKE '%L%') o deja vacío si no hay: ").strip()

    # Construir consulta
    sql = f"SELECT {campos} FROM {tablas_expr}"
    if where:
        sql += f" WHERE {where}"

    print("\n📘 Consulta generada:")
    print(sql)

    # Ejecutar y mostrar resultados
    try:
        cursor = conn.execute(sql)
        # Si la consulta no devuelve filas (p. ej. es DML), cursor.description será None
        if cursor.description:
            resultados = cursor.fetchall()
            if resultados:
                print("\n✅ Resultados:")
                for fila in resultados:
                    print(fila)
            else:
                print("\n⚠️ La consulta se ejecutó correctamente pero no devolvió resultados.")
        else:
            # Consulta de modificación o sin resultado
            # Intentamos commit/sync dependiendo del tipo de conexión
            try:
                # Si la conexión tiene commit (sqlite), lo usamos; si tiene sync (libsql), lo usamos
                if hasattr(conn, "commit"):
                    conn.commit()
                if hasattr(conn, "sync"):
                    conn.sync()
            except Exception:
                pass
            print("\n✅ Consulta ejecutada (sin resultados que mostrar).")
    except Exception as e:
        print("\n❌ Error al ejecutar la consulta:", e)


# ==================== MENÚ ACTUALIZAR ====================
def menu_actualizar():
    while True:
        print("\n" + "="*40)
        print("           ACTUALIZAR DATOS")
        print("="*40)
        print("1. 🏪 Actualizar Tienda")
        print("2. 👨‍💼 Actualizar Trabajador")
        print("3. 📦 Actualizar Producto")
        print("4. 👥 Actualizar Cliente")
        print("5. ↩️  Volver al menú principal")
        print("="*40)

        opcion = input("Elige una opción (1-5): ")

        match opcion:
            case "1":
                actualizar_tienda()
            case "2":
                actualizar_trabajador()
            case "3":
                actualizar_producto()
            case "4":
                actualizar_cliente()
            case "5":
                break
            case _:
                print("❌ Opción no válida. Inténtalo de nuevo.")

def actualizar_tienda():
    consultar_tiendas()
    try:
        id_tienda = int(input("\nID de la tienda a actualizar: "))
        nombre = input("Nuevo nombre (dejar vacío para no cambiar): ")
        direccion = input("Nueva dirección (dejar vacío para no cambiar): ")
        cod_postal = input("Nuevo código postal (dejar vacío para no cambiar): ")
        
        campos = []
        valores = []
        
        if nombre:
            campos.append("NOMBRE = ?")
            valores.append(nombre)
        if direccion:
            campos.append("DIRECCION = ?")
            valores.append(direccion)
        if cod_postal:
            campos.append("COD_POSTAL = ?")
            valores.append(int(cod_postal))
        
        if not campos:
            print("❌ No se especificaron campos para actualizar.")
            return
        
        valores.append(id_tienda)
        query = f"UPDATE TIENDA SET {', '.join(campos)} WHERE IDTIENDA = ?"
        conn.execute(query, valores)
        conn.commit()
        print("✅ Tienda actualizada correctamente.")
        
    except Exception as e:
        print("❌ Error al actualizar tienda:", e)

def actualizar_trabajador():
    consultar_trabajadores()
    try:
        id_trabajador = int(input("\nID del trabajador a actualizar: "))
        sueldo = input("Nuevo sueldo (dejar vacío para no cambiar): ")
        horario = input("Nuevo horario (COMPLETO/PARCIAL, dejar vacío para no cambiar): ")
        telefono = input("Nuevo teléfono (dejar vacío para no cambiar): ")
        
        campos = []
        valores = []
        
        if sueldo:
            campos.append("SUELDO = ?")
            valores.append(float(sueldo))
        if horario:
            campos.append("HORARIO = ?")
            valores.append(horario.upper())
        if telefono:
            campos.append("TELEFONO = ?")
            valores.append(telefono)
        
        if not campos:
            print("❌ No se especificaron campos para actualizar.")
            return
        
        valores.append(id_trabajador)
        query = f"UPDATE TRABAJADORES SET {', '.join(campos)} WHERE IDTRABAJADOR = ?"
        conn.execute(query, valores)
        conn.commit()
        print("✅ Trabajador actualizado correctamente.")
        
    except Exception as e:
        print("❌ Error al actualizar trabajador:", e)

def actualizar_producto():
    consultar_productos()
    try:
        id_producto = int(input("\nID del producto a actualizar: "))
        precio = input("Nuevo precio (dejar vacío para no cambiar): ")
        stock = input("Nuevo stock (dejar vacío para no cambiar): ")
        descripcion = input("Nueva descripción (dejar vacío para no cambiar): ")
        
        campos = []
        valores = []
        
        if precio:
            campos.append("PRECIO = ?")
            valores.append(float(precio))
        if stock:
            campos.append("STOCK = ?")
            valores.append(int(stock))
        if descripcion:
            campos.append("DESCRIPCION = ?")
            valores.append(descripcion)
        
        if not campos:
            print("❌ No se especificaron campos para actualizar.")
            return
        
        valores.append(id_producto)
        query = f"UPDATE PRODUCTOS SET {', '.join(campos)} WHERE IDPRODUCTO = ?"
        conn.execute(query, valores)
        conn.commit()
        print("✅ Producto actualizado correctamente.")
        
    except Exception as e:
        print("❌ Error al actualizar producto:", e)

def actualizar_cliente():
    consultar_clientes()
    try:
        id_cliente = int(input("\nID del cliente a actualizar: "))
        telefono = input("Nuevo teléfono (dejar vacío para no cambiar): ")
        email = input("Nuevo email (dejar vacío para no cambiar): ")
        vip = input("Nuevo estado VIP (SI/NO, dejar vacío para no cambiar): ")
        
        campos = []
        valores = []
        
        if telefono:
            campos.append("TELEFONO = ?")
            valores.append(telefono)
        if email:
            campos.append("EMAIL = ?")
            valores.append(email)
        if vip:
            campos.append("VIP = ?")
            valores.append(vip.upper())
        
        if not campos:
            print("❌ No se especificaron campos para actualizar.")
            return
        
        valores.append(id_cliente)
        query = f"UPDATE CLIENTES SET {', '.join(campos)} WHERE IDCLIENTE = ?"
        conn.execute(query, valores)
        conn.commit()
        print("✅ Cliente actualizado correctamente.")
        
    except Exception as e:
        print("❌ Error al actualizar cliente:", e)

# ==================== MENÚ ELIMINAR ====================
def menu_eliminar():
    while True:
        print("\n" + "="*40)
        print("           ELIMINAR DATOS")
        print("="*40)
        print("1. 🏪 Eliminar Tienda")
        print("2. 👨‍💼 Eliminar Trabajador")
        print("3. 📦 Eliminar Producto")
        print("4. 👥 Eliminar Cliente")
        print("5. 🧾 Eliminar Factura")
        print("6. ↩️  Volver al menú principal")
        print("="*40)

        opcion = input("Elige una opción (1-6): ")

        match opcion:
            case "1":
                eliminar_tienda()
            case "2":
                eliminar_trabajador()
            case "3":
                eliminar_producto()
            case "4":
                eliminar_cliente()
            case "5":
                eliminar_factura()
            case "6":
                break
            case _:
                print("❌ Opción no válida. Inténtalo de nuevo.")

def eliminar_tienda():
    consultar_tiendas()
    try:
        id_tienda = int(input("\nID de la tienda a eliminar: "))
        confirmar = input("¿Estás seguro de que quieres eliminar esta tienda? (s/n): ")
        if confirmar.lower() == 's':
            conn.execute("DELETE FROM TIENDA WHERE IDTIENDA = ?", (id_tienda,))
            conn.commit()
            print("✅ Tienda eliminada correctamente.")
        else:
            print("❌ Eliminación cancelada.")
    except Exception as e:
        print("❌ Error al eliminar tienda:", e)

def eliminar_trabajador():
    consultar_trabajadores()
    try:
        id_trabajador = int(input("\nID del trabajador a eliminar: "))
        confirmar = input("¿Estás seguro de que quieres eliminar este trabajador? (s/n): ")
        if confirmar.lower() == 's':
            conn.execute("DELETE FROM TRABAJADORES WHERE IDTRABAJADOR = ?", (id_trabajador,))
            conn.commit()
            print("✅ Trabajador eliminado correctamente.")
        else:
            print("❌ Eliminación cancelada.")
    except Exception as e:
        print("❌ Error al eliminar trabajador:", e)

def eliminar_producto():
    consultar_productos()
    try:
        id_producto = int(input("\nID del producto a eliminar: "))
        confirmar = input("¿Estás seguro de que quieres eliminar este producto? (s/n): ")
        if confirmar.lower() == 's':
            conn.execute("DELETE FROM PRODUCTOS WHERE IDPRODUCTO = ?", (id_producto,))
            conn.commit()
            print("✅ Producto eliminado correctamente.")
        else:
            print("❌ Eliminación cancelada.")
    except Exception as e:
        print("❌ Error al eliminar producto:", e)

def eliminar_cliente():
    consultar_clientes()
    try:
        id_cliente = int(input("\nID del cliente a eliminar: "))
        confirmar = input("¿Estás seguro de que quieres eliminar este cliente? (s/n): ")
        if confirmar.lower() == 's':
            conn.execute("DELETE FROM CLIENTES WHERE IDCLIENTE = ?", (id_cliente,))
            conn.commit()
            print("✅ Cliente eliminado correctamente.")
        else:
            print("❌ Eliminación cancelada.")
    except Exception as e:
        print("❌ Error al eliminar cliente:", e)

def eliminar_factura():
    consultar_facturas()
    try:
        id_factura = int(input("\nID de la factura a eliminar: "))
        confirmar = input("¿Estás seguro de que quieres eliminar esta factura? (s/n): ")
        if confirmar.lower() == 's':
            conn.execute("DELETE FROM FACTURAS WHERE IDFACTURA = ?", (id_factura,))
            conn.commit()
            print("✅ Factura eliminada correctamente.")
        else:
            print("❌ Eliminación cancelada.")
    except Exception as e:
        print("❌ Error al eliminar factura:", e)

# ==================== INICIO DEL PROGRAMA ====================
if __name__ == "__main__":
    menu_principal()