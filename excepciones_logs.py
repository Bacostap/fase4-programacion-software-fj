# Importamos datetime para poder sacar la fecha y hora actual cuando pase un error o evento
from datetime import datetime


# Creamos nuestra propia clase base de errores para el proyecto Software FJ
class ErrorSoftwareFJ(Exception):
    # Este es el constructor que recibe el texto del error
    def __init__(self, mensaje):
        # Le pasamos el mensaje a la clase Exception que ya viene en Python
        super().__init__(mensaje)


# Error personalizado para cuando el usuario mete datos malos o deja cosas vacias
class DatosInvalidosError(ErrorSoftwareFJ):
    # Constructor del error de datos
    def __init__(self, mensaje):
        # Agregamos un texto inicial para saber que tipo de falla fue
        super().__init__("Error en los datos: " + mensaje)


# Error personalizado para cuando intentan reservar una sala o equipo que ya esta ocupado
class ServicioNoDisponibleError(ErrorSoftwareFJ):
    # Constructor del error de disponibilidad
    def __init__(self, mensaje):
        # Mandamos el aviso a la clase padre
        super().__init__("Servicio no disponible: " + mensaje)


# Error personalizado para problemas con las reservas (horas en cero, descuentos raros, etc.)
class ReservaInvalidaError(ErrorSoftwareFJ):
    # Constructor del error de reserva
    def __init__(self, mensaje):
        # Mandamos el mensaje a la clase base
        super().__init__("Problema con la reserva: " + mensaje)


# Error personalizado para cuando alguien quiere hacer algo que no se puede (como cancelar dos veces)
class OperacionNoPermitidaError(ErrorSoftwareFJ):
    # Constructor del error de operacion
    def __init__(self, mensaje):
        # Mandamos el mensaje a la clase padre
        super().__init__("Accion no permitida: " + mensaje)


# Clase para guardar todo lo que pasa en un archivo txt sin usar bases de datos
class RegistroLogs:
    # Nombre del archivo donde se van a guardar los eventos y los errores
    nombre_archivo = "logs_sistema.txt"

    # Metodo para escribir una linea nueva en el archivo de texto
    @staticmethod
    def guardar_log(tipo, detalle):
        # Definimos la variable archivo en None por si falla al abrirlo
        archivo = None
        # Sacamos la fecha y hora de este momento
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Armamos el renglon que vamos a escribir en el txt
        renglon = f"[{ahora}] {tipo}: {detalle}\n"

        # Usamos try / except / finally como pide la guia para manejar archivos de forma segura
        try:
            # Abrimos el archivo en modo 'a' (append) para agregar al final sin borrar lo anterior
            archivo = open(RegistroLogs.nombre_archivo, "a", encoding="utf-8")
            # Escribimos el renglon en el archivo
            archivo.write(renglon)
        except IOError as e:
            # Si hay un problema con el archivo en Windows/Mac avisamos en consola pero no cerramos el programa
            print("No se pudo escribir en el archivo de logs:", e)
        finally:
            # El finally siempre se ejecuta, haya error o no, para cerrar el archivo
            if archivo is not None:
                # Cerramos el archivo para que se guarden bien los cambios
                archivo.close()