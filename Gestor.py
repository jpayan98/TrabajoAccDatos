from conexionDB import conectar_db

# Crear una única conexión reutilizable
conn = conectar_db()

def insertar():
    print("\n¿Qué quieres crear?")
    print("1. Tienda")
    print("2. Trabajador")
    print("3. Producto")
    print("4. Cliente")

    opcion = input("Elige una opción (1-4): ")

    match opcion:
        case "1":
            print("Has elegido crear una Tienda")
            crear_tienda()
        case "2":
            print("Has elegido crear un Trabajador")
            crear_trabajador()
        case "3":
            print("Has elegido crear un Producto")
            crear_producto()
        case "4":
            print("Has elegido crear un Cliente")
            crear_cliente()
        case _:
            print("❌ Opción no válida")

def crear_tienda():
    nombre = input("Nombre de la tienda: ")
    direccion = input("Dirección: ")
    cod_postal = input("Código postal: ")

    try:
        conn.execute(
            "INSERT INTO TIENDA (NOMBRE, DIRECCION, COD_POSTAL) VALUES (?, ?, ?);",
            (nombre, direccion, int(cod_postal))
        )
        conn.execute("COMMIT;")
        print("✅ Tienda creada correctamente.")
    except Exception as e:
        print(f"❌ Error al crear la tienda: {e}")

def crear_trabajador():
    id_tienda = input("ID de la tienda donde trabaja: ")
    nombre = input("Nombre: ")
    ape1 = input("Primer apellido: ")
    ape2 = input("Segundo apellido (opcional): ")
    dni = input("DNI: ")
    residencia = input("Residencia: ")
    telefono = input("Teléfono: ")
    contacto = input("Email de contacto: ")
    horario = input("Horario (COMPLETO/PARCIAL): ")
    sueldo = input("Sueldo: ")

    try:
        conn.execute('''
            INSERT INTO TRABAJADORES (IDTIENDA, NOMBRE, APE1, APE2, DNI, RESIDENCIA, TELEFONO, CONTACTO, HORARIO, SUELDO)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        ''', (int(id_tienda), nombre, ape1, ape2, dni, residencia, telefono, contacto, horario.upper(), float(sueldo)))
        conn.execute("COMMIT;")
        print("✅ Trabajador creado correctamente.")
    except Exception as e:
        print(f"❌ Error al crear el trabajador: {e}")

def crear_producto():
    id_tienda = input("ID de la tienda: ")
    nombre = input("Nombre del producto: ")
    descripcion = input("Descripción: ")
    precio = input("Precio: ")
    stock = input("Stock inicial: ")

    try:
        conn.execute('''
            INSERT INTO PRODUCTOS (IDTIENDA, NOMBRE, DESCRIPCION, PRECIO, STOCK)
            VALUES (?, ?, ?, ?, ?);
        ''', (int(id_tienda), nombre, descripcion, float(precio), int(stock)))
        conn.execute("COMMIT;")
        print("✅ Producto creado correctamente.")
    except Exception as e:
        print(f"❌ Error al crear el producto: {e}")

def crear_cliente():
    nombre = input("Nombre: ")
    ape1 = input("Primer apellido: ")
    ape2 = input("Segundo apellido (opcional): ")
    residencia = input("Residencia: ")
    telefono = input("Teléfono (9 dígitos): ")
    email = input("Email: ")
    vip = input("¿Cliente VIP? (SI/NO): ")

    try:
        conn.execute('''
            INSERT INTO CLIENTES (NOMBRE, APE1, APE2, RESIDENCIA, TELEFONO, EMAIL, GASTO_TOTAL, VIP)
            VALUES (?, ?, ?, ?, ?, ?, 0, ?);
        ''', (nombre, ape1, ape2, residencia, telefono, email, vip.upper()))
        conn.execute("COMMIT;")
        print("✅ Cliente creado correctamente.")
    except Exception as e:
        print(f"❌ Error al crear el cliente: {e}")

# --- Ejecución principal ---
if __name__ == "__main__":
    print("🚀 Gestor de Base de Datos - Sistema de Tiendas")
    print("==============================================")
    
    while True:
        insertar()
        continuar = input("\n¿Quieres insertar otro registro? (s/n): ")
        if continuar.lower() != "s":
            print("👋 Saliendo del gestor.")
            break

    conn.close()