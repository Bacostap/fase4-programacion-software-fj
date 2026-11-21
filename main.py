# Importamos nuestras excepciones y el manejador de logs
from excepciones_logs import ErrorSoftwareFJ, RegistroLogs
# Importamos los modelos de clientes y servicios
from modelos import Cliente, ReservaSala, AlquilerEquipo, AsesoriaEspecializada
# Importamos la reserva y el sistema que maneja las listas
from reservas import Reserva, SistemaGestionFJ


# Funcion principal donde probamos 12 operaciones (buenas y malas) sin que el programa se caiga
def correr_pruebas():
    # Creamos el objeto principal del sistema
    sistema = SistemaGestionFJ()
    print("=== PRUEBAS DEL SISTEMA SOFTWARE FJ (12 OPERACIONES) ===\n")

    # 1. Registrar un cliente valido (usando try / except / else)
    try:
        # Creamos el primer cliente con datos bien escritos
        c1 = Cliente("10154321", "Camila Torres", "camila.torres@gmail.com")
        sistema.registrar_cliente(c1)
    except ErrorSoftwareFJ as e:
        RegistroLogs.guardar_log("ERROR", f"Operacion 1 fallo: {e}")
    else:
        # El else corre solo si no hubo ningun error en el try
        print("1. [OK] Cliente registrado:", c1.nombre)

    # 2. Registrar un segundo cliente valido
    try:
        # Creamos el segundo cliente
        c2 = Cliente("79854123", "Andres Rojas", "arojas@correo.edu.co")
        sistema.registrar_cliente(c2)
    except ErrorSoftwareFJ as e:
        RegistroLogs.guardar_log("ERROR", f"Operacion 2 fallo: {e}")
    else:
        print("2. [OK] Cliente registrado:", c2.nombre)

    # 3. Intentar registrar un cliente con correo malo (sin @)
    try:
        # Esto debe lanzar DatosInvalidosError
        c_malo = Cliente("11223344", "Juan Perez", "juanperez.gmail.com")
        sistema.registrar_cliente(c_malo)
    except ErrorSoftwareFJ as e:
        # Guardamos el error en el txt y seguimos ejecutando normal
        RegistroLogs.guardar_log("ERROR", f"Operacion 3 controlada: {e}")
        print("3. [ERROR CONTROLADO]", e)

    # 4. Intentar registrar un cliente repetido
    try:
        # Ponemos el mismo documento de Camila para probar el control de duplicados
        c_repetido = Cliente("10154321", "Camila Copia", "copia@gmail.com")
        sistema.registrar_cliente(c_repetido)
    except ErrorSoftwareFJ as e:
        RegistroLogs.guardar_log("ERROR", f"Operacion 4 controlada: {e}")
        print("4. [ERROR CONTROLADO]", e)

    # 5. Crear servicio valido 1: Sala de reuniones
    try:
        # Creamos una sala para 10 personas con proyector
        sala1 = ReservaSala("S01", "Sala Juntas Principal", 45000, capacidad=10, tiene_proyector=True)
        sistema.registrar_servicio(sala1)
    except ErrorSoftwareFJ as e:
        RegistroLogs.guardar_log("ERROR", f"Operacion 5 fallo: {e}")
    else:
        print("5. [OK] Servicio creado:", sala1.ver_detalle())

    # 6. Crear servicio valido 2: Alquiler de equipos
    try:
        # Creamos alquiler de 2 portatiles
        equipo1 = AlquilerEquipo("E01", "Combo Portatiles", 20000, tipo_equipo="Portatil Lenovo", cantidad=2)
        sistema.registrar_servicio(equipo1)
    except ErrorSoftwareFJ as e:
        RegistroLogs.guardar_log("ERROR", f"Operacion 6 fallo: {e}")
    else:
        print("6. [OK] Servicio creado:", equipo1.ver_detalle())

    # 7. Crear servicio valido 3: Asesoria especializada
    try:
        # Creamos asesoria presencial
        asesoria1 = AsesoriaEspecializada("A01", "Soporte Redes", 70000, tema="Seguridad Informatica", modalidad="Presencial")
        sistema.registrar_servicio(asesoria1)
    except ErrorSoftwareFJ as e:
        RegistroLogs.guardar_log("ERROR", f"Operacion 7 fallo: {e}")
    else:
        print("7. [OK] Servicio creado:", asesoria1.ver_detalle())

    # 8. Intentar crear un servicio con precio negativo
    try:
        # Esto debe fallar porque el valor por hora es -10000
        sala_mala = ReservaSala("S99", "Sala Error", -10000, capacidad=5)
        sistema.registrar_servicio(sala_mala)
    except ErrorSoftwareFJ as e:
        RegistroLogs.guardar_log("ERROR", f"Operacion 8 controlada: {e}")
        print("8. [ERROR CONTROLADO]", e)

    # 9. Hacer una reserva exitosa usando descuento e IVA (metodo sobrecargado)
    try:
        # Reservamos la sala S01 por 3 horas, 10% de descuento y con IVA
        res1 = Reserva("R001", c1, sala1, horas=3, descuento=0.10, con_iva=True)
        sistema.crear_reserva(res1)
    except ErrorSoftwareFJ as e:
        RegistroLogs.guardar_log("ERROR", f"Operacion 9 fallo: {e}")
    else:
        print("9. [OK] Reserva creada:", res1.ver_detalle())

    # 10. Intentar reservar la misma sala que ya quedo ocupada (encadenamiento de excepciones)
    try:
        # Como sala1 esta ocupada por res1, esto debe lanzar ReservaInvalidaError encadenada
        res_fallida = Reserva("R002", c2, sala1, horas=2)
        sistema.crear_reserva(res_fallida)
    except ErrorSoftwareFJ as e:
        # Mostramos tambien cual fue la causa interna (__cause__)
        RegistroLogs.guardar_log("ERROR", f"Operacion 10 controlada: {e} | Causa: {e.__cause__}")
        print(f"10. [ERROR CONTROLADO] {e} (Motivo: {e.__cause__})")

    # 11. Hacer una segunda reserva exitosa (Asesoria sin descuento y sin IVA)
    try:
        # Aqui usamos los valores por defecto de calcular_costo
        res2 = Reserva("R003", c2, asesoria1, horas=2)
        sistema.crear_reserva(res2)
    except ErrorSoftwareFJ as e:
        RegistroLogs.guardar_log("ERROR", f"Operacion 11 fallo: {e}")
    else:
        print("11. [OK] Reserva creada:", res2.ver_detalle())

    # 12. Cancelar reserva y probar doble cancelacion (usando try / except / finally)
    try:
        # Cancelamos res1 (esto libera la sala S01)
        res1.cancelar_reserva()
        print("12a. [OK] Se cancelo la reserva R001 y la sala quedo libre.")
        # Intentamos volver a cancelar res1 para provocar error controlado
        res1.cancelar_reserva()
    except ErrorSoftwareFJ as e:
        RegistroLogs.guardar_log("ERROR", f"Operacion 12b controlada: {e}")
        print("12b. [ERROR CONTROLADO]", e)
    finally:
        # El finally cierra la simulacion asegurando que quede registrada en el txt
        RegistroLogs.guardar_log("EVENTO", "Fin de la simulacion de las 12 operaciones.")
        print("\n[FINALLY] Pruebas terminadas. Revisa el archivo 'logs_sistema.txt'.")

    # Imprimimos el resumen de las listas en memoria
    sistema.imprimir_resumen()


# Arrancamos el programa
if __name__ == "__main__":
    correr_pruebas()
