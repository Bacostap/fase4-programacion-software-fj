# Importamos nuestras excepciones y el manejador de logs
from excepciones_logs import (
    DatosInvalidosError,
    ServicioNoDisponibleError,
    ReservaInvalidaError,
    OperacionNoPermitidaError,
    RegistroLogs,
)
# Importamos las clases del archivo modelos
from modelos import EntidadBase, Cliente, Servicio


# Clase Reserva que une a un Cliente con un Servicio
class Reserva(EntidadBase):
    # Constructor de la reserva
    def __init__(self, codigo_reserva, cliente, servicio, horas, descuento=0.0, con_iva=False):
        # Guardamos el codigo usando el constructor de EntidadBase
        super().__init__(codigo_reserva)
        # Verificamos que si nos pasen un objeto de tipo Cliente
        if not isinstance(cliente, Cliente):
            # Lanzamos error si no es un cliente valido
            raise DatosInvalidosError("Debe asignar un cliente valido a la reserva.")
        # Verificamos que si nos pasen un objeto de tipo Servicio
        if not isinstance(servicio, Servicio):
            # Lanzamos error si no es un servicio valido
            raise DatosInvalidosError("Debe asignar un servicio valido a la reserva.")

        # Guardamos los datos privados de la reserva
        self.__cliente = cliente
        self.__servicio = servicio
        self.__horas = horas
        self.__descuento = descuento
        self.__con_iva = con_iva
        self.__estado = "PENDIENTE"
        self.__costo_final = 0.0

        # Validamos que las horas y el descuento tengan sentido
        self.validar_datos()

    # Getter para consultar el estado de la reserva
    @property
    def estado(self):
        # Retornamos PENDIENTE, CONFIRMADA o CANCELADA
        return self.__estado

    # Getter para consultar cuanto costo la reserva
    @property
    def costo_final(self):
        # Retornamos el valor calculado
        return self.__costo_final

    # Validacion de reglas de la reserva
    def validar_datos(self):
        # Las horas tienen que ser mayores a cero
        if not isinstance(self.__horas, (int, float)) or self.__horas <= 0:
            # Lanzamos error de reserva invalida
            raise ReservaInvalidaError("Las horas de reserva deben ser mayores a 0.")
        # El descuento debe estar entre 0% (0.0) y 50% (0.5)
        if self.__descuento < 0 or self.__descuento > 0.5:
            # Lanzamos error si ponen un descuento absurdo
            raise ReservaInvalidaError("El descuento debe estar entre 0.0 y 0.5.")
        # Todo correcto
        return True

    # Metodo para procesar el cobro usando polimorfismo y encadenamiento de excepciones
    def procesar_reserva(self):
        # Usamos try/except para atrapar el error original y encadenarlo como pide el anexo
        try:
            # Revisamos si el servicio esta libre
            if not self.__servicio.disponible:
                # Si esta ocupado lanzamos ServicioNoDisponibleError
                raise ServicioNoDisponibleError(
                    f"El servicio '{self.__servicio.nombre_servicio}' ya esta ocupado."
                )
            # Llamamos al metodo calcular_costo del servicio que corresponda (polimorfismo)
            self.__costo_final = self.__servicio.calcular_costo(
                self.__horas, descuento=self.__descuento, con_iva=self.__con_iva
            )
            # Comprobamos que el costo no haya dado cero o negativo
            if self.__costo_final <= 0:
                # Lanzamos error matematico si algo salio mal
                raise ValueError("El total calculado no puede ser cero o negativo.")
        except Exception as error_previo:
            # Encadenamos la excepcion usando 'from error_previo' como exige la guia
            raise ReservaInvalidaError(
                f"No se pudo procesar la reserva {self.identificacion}"
            ) from error_previo

        # Si todo salio bien lo anotamos en el archivo txt
        RegistroLogs.guardar_log(
            "EVENTO",
            f"Reserva {self.identificacion} procesada para {self.__cliente.nombre}. Total: ${self.__costo_final}",
        )

    # Metodo para confirmar la reserva y marcar el servicio como ocupado
    def confirmar_reserva(self):
        # No dejamos confirmar si ya la habian cancelado antes
        if self.__estado == "CANCELADA":
            # Lanzamos error de operacion no permitida
            raise OperacionNoPermitidaError("No se puede confirmar una reserva cancelada.")
        # Si todavia no se ha calculado el costo, la procesamos primero
        if self.__costo_final == 0.0:
            # Llamamos a procesar_reserva
            self.procesar_reserva()
        # Cambiamos el estado a CONFIRMADA
        self.__estado = "CONFIRMADA"
        # Ponemos el servicio en False para que nadie mas lo reserve mientras este en uso
        self.__servicio.disponible = False
        # Guardamos el evento en el archivo de logs
        RegistroLogs.guardar_log("EVENTO", f"Reserva {self.identificacion} CONFIRMADA.")

    # Metodo para cancelar la reserva y volver a dejar libre el servicio
    def cancelar_reserva(self):
        # Si ya estaba cancelada lanzamos error para evitar doble cancelacion
        if self.__estado == "CANCELADA":
            # Lanzamos excepcion personalizada
            raise OperacionNoPermitidaError(f"La reserva {self.identificacion} ya estaba cancelada.")
        # Cambiamos el estado a CANCELADA
        self.__estado = "CANCELADA"
        # Volvemos a poner disponible el servicio
        self.__servicio.disponible = True
        # Anotamos la cancelacion en el log
        RegistroLogs.guardar_log("EVENTO", f"Reserva {self.identificacion} CANCELADA.")

    # Implementacion de ver_detalle para la reserva
    def ver_detalle(self):
        # Retornamos toda la info de la reserva en una sola linea
        return (
            f"Reserva [{self.identificacion}] ({self.__estado}) -> Cliente: {self.__cliente.nombre} | "
            f"Servicio: {self.__servicio.nombre_servicio} | Horas: {self.__horas} | Total: ${self.__costo_final}"
        )


# Clase que guarda todo en listas de Python en memoria (sin bases de datos)
class SistemaGestionFJ:
    # Constructor que crea las listas vacias
    def __init__(self):
        # Lista donde se guardan los clientes
        self.lista_clientes = []
        # Lista donde se guardan los servicios
        self.lista_servicios = []
        # Lista donde se guardan las reservas
        self.lista_reservas = []
        # Anotamos en el txt que arranco el programa
        RegistroLogs.guardar_log("EVENTO", "Inicio del sistema Software FJ en memoria.")

    # Metodo para meter un cliente a la lista revisando que no este repetido
    def registrar_cliente(self, cliente):
        # Buscamos si ya hay alguien con ese mismo documento
        for c in self.lista_clientes:
            # Comparamos identificaciones
            if c.identificacion == cliente.identificacion:
                # Si ya existe lanzamos error
                raise DatosInvalidosError(f"El documento {cliente.identificacion} ya esta registrado.")
        # Si no estaba repetido lo agregamos a la lista
        self.lista_clientes.append(cliente)

    # Metodo para meter un servicio a la lista revisando que no se repita el codigo
    def registrar_servicio(self, servicio):
        # Recorremos la lista de servicios actuales
        for s in self.lista_servicios:
            # Comparamos codigos
            if s.identificacion == servicio.identificacion:
                # Lanzamos error si el codigo ya existe
                raise DatosInvalidosError(f"El codigo de servicio {servicio.identificacion} ya existe.")
        # Agregamos el servicio a la lista
        self.lista_servicios.append(servicio)

    # Metodo para confirmar y guardar una reserva en la lista
    def crear_reserva(self, reserva):
        # Primero intentamos confirmarla (aqui se valida disponibilidad y costos)
        reserva.confirmar_reserva()
        # Si no fallo nada la metemos a la lista de reservas
        self.lista_reservas.append(reserva)

    # Metodo para imprimir en pantalla todo lo que quedo guardado en las listas
    def imprimir_resumen(self):
        # Imprimimos un separador sencillo
        print("\n------------------------------------------------------------")
        print("RESUMEN FINAL DE DATOS EN MEMORIA - SOFTWARE FJ")
        print("------------------------------------------------------------")
        # Mostramos los clientes
        print("Clientes registrados:", len(self.lista_clientes))
        for c in self.lista_clientes:
            print(" *", c.ver_detalle())
        # Mostramos los servicios
        print("\nServicios registrados:", len(self.lista_servicios))
        for s in self.lista_servicios:
            print(" *", s.ver_detalle())
        # Mostramos las reservas
        print("\nReservas registradas:", len(self.lista_reservas))
        for r in self.lista_reservas:
            print(" *", r.ver_detalle())
        print("------------------------------------------------------------")