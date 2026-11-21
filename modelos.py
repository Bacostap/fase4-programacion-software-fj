# Importamos ABC y abstractmethod para poder hacer clases abstractas como pide el anexo
from abc import ABC, abstractmethod
# Traemos nuestras excepciones y la clase de logs del otro archivo
from excepciones_logs import DatosInvalidosError, RegistroLogs


# Clase abstracta general para todas las entidades del sistema (clientes, servicios, reservas)
class EntidadBase(ABC):
    # Constructor que recibe el codigo o identificacion
    def __init__(self, identificacion):
        # Revisamos que la identificacion no venga vacia ni con puros espacios
        if not identificacion or str(identificacion).strip() == "":
            # Si viene vacia lanzamos nuestra excepcion personalizada
            raise DatosInvalidosError("La identificacion no puede quedar vacia.")
        # Guardamos el id como atributo privado usando dos guiones bajos (encapsulacion)
        self.__identificacion = str(identificacion).strip()

    # Usamos @property para poder leer el id privado desde afuera sin que lo modifiquen
    @property
    def identificacion(self):
        # Devolvemos el valor del id privado
        return self.__identificacion

    # Metodo abstracto que obliga a las clases hijas a tener su propia validacion
    @abstractmethod
    def validar_datos(self):
        # No lleva codigo aqui porque cada clase hija lo hace a su manera
        pass

    # Metodo abstracto para mostrar la informacion resumida
    @abstractmethod
    def ver_detalle(self):
        # Cada clase hija implementara este metodo
        pass


# Clase Cliente que hereda de EntidadBase
class Cliente(EntidadBase):
    # Constructor para crear un cliente nuevo
    def __init__(self, documento, nombre, correo):
        # Llamamos al constructor de EntidadBase para guardar el documento como identificacion
        super().__init__(documento)
        # Asignamos el nombre usando el setter para que se valide de una vez
        self.nombre = nombre
        # Asignamos el correo usando el setter para revisar que tenga arroba
        self.correo = correo
        # Llamamos a validar_datos para revisar el documento
        self.validar_datos()
        # Guardamos en el archivo txt que se creo este cliente
        RegistroLogs.guardar_log("EVENTO", f"Se registro el cliente {self.nombre} con documento {self.identificacion}")

    # Getter para leer el nombre privado
    @property
    def nombre(self):
        # Retornamos el nombre guardado
        return self.__nombre

    # Setter para validar el nombre antes de guardarlo
    @nombre.setter
    def nombre(self, nuevo_nombre):
        # Verificamos que sea texto y tenga por lo menos 3 letras
        if not isinstance(nuevo_nombre, str) or len(nuevo_nombre.strip()) < 3:
            # Lanzamos error si el nombre es muy corto o no es texto
            raise DatosInvalidosError("El nombre debe tener minimo 3 letras.")
        # Guardamos el nombre limpio en el atributo privado
        self.__nombre = nuevo_nombre.strip()

    # Getter para leer el correo privado
    @property
    def correo(self):
        # Retornamos el correo guardado
        return self.__correo

    # Setter para validar que el correo parezca un correo real
    @correo.setter
    def correo(self, nuevo_correo):
        # Revisamos que tenga '@' y un punto '.'
        if not isinstance(nuevo_correo, str) or "@" not in nuevo_correo or "." not in nuevo_correo:
            # Si no tiene arroba o punto lanzamos excepcion
            raise DatosInvalidosError(f"El correo '{nuevo_correo}' no es valido.")
        # Guardamos el correo en minusculas
        self.__correo = nuevo_correo.strip().lower()

    # Implementacion del metodo abstracto validar_datos para Cliente
    def validar_datos(self):
        # Validamos que el documento tenga al menos 5 caracteres
        if len(self.identificacion) < 5:
            # Si es muy corto lanzamos error
            raise DatosInvalidosError("El documento debe tener al menos 5 caracteres.")
        # Si todo esta bien devolvemos True
        return True

    # Implementacion del metodo abstracto ver_detalle para Cliente
    def ver_detalle(self):
        # Retornamos un texto sencillo con los datos del cliente
        return f"Cliente: {self.nombre} | Doc: {self.identificacion} | Correo: {self.correo}"


# Clase abstracta Servicio que hereda de EntidadBase
class Servicio(EntidadBase, ABC):
    # Constructor base para cualquier servicio de Software FJ
    def __init__(self, codigo, nombre_servicio, valor_hora, disponible=True):
        # Guardamos el codigo usando el constructor de EntidadBase
        super().__init__(codigo)
        # Guardamos los atributos privados del servicio
        self.__nombre_servicio = nombre_servicio
        self.__valor_hora = valor_hora
        self.__disponible = bool(disponible)
        # Validamos los datos basicos del servicio
        self.validar_datos()

    # Getter para ver el nombre del servicio
    @property
    def nombre_servicio(self):
        # Devolvemos el nombre privado
        return self.__nombre_servicio

    # Getter para ver cuanto cuesta la hora
    @property
    def valor_hora(self):
        # Devolvemos el precio por hora
        return self.__valor_hora

    # Getter para saber si esta libre u ocupado
    @property
    def disponible(self):
        # Devolvemos True o False
        return self.__disponible

    # Setter para cambiar si el servicio esta disponible o no
    @disponible.setter
    def disponible(self, estado):
        # Actualizamos el estado booleano
        self.__disponible = bool(estado)

    # Validacion comun para todos los servicios
    def validar_datos(self):
        # Revisamos que el servicio tenga nombre
        if not isinstance(self.__nombre_servicio, str) or self.__nombre_servicio.strip() == "":
            # Lanzamos error si no tiene nombre
            raise DatosInvalidosError("Falta el nombre del servicio.")
        # Revisamos que el valor por hora sea mayor a cero
        if not isinstance(self.__valor_hora, (int, float)) or self.__valor_hora <= 0:
            # Lanzamos error si ponen precios negativos o en cero
            raise DatosInvalidosError("El valor por hora debe ser mayor a cero.")
        # Todo correcto
        return True

    # Metodo abstracto que cada tipo de servicio va a sobrescribir (polimorfismo)
    @abstractmethod
    def calcular_costo(self, horas, descuento=0.0, con_iva=False):
        # Sirve como metodo sobrecargado porque descuento y con_iva son opcionales
        pass


# Primer servicio especializado: Reserva de Salas
class ReservaSala(Servicio):
    # Constructor con capacidad de personas y si tiene proyector
    def __init__(self, codigo, nombre_servicio, valor_hora, capacidad, tiene_proyector=True):
        # Llamamos al constructor de la clase padre Servicio
        super().__init__(codigo, nombre_servicio, valor_hora)
        # Validamos que la capacidad de la sala sea mayor a 0
        if not isinstance(capacidad, int) or capacidad <= 0:
            # Lanzamos error si la capacidad es invalida
            raise DatosInvalidosError("La capacidad de la sala debe ser mayor a 0 personas.")
        # Guardamos los atributos propios de la sala
        self.__capacidad = capacidad
        self.__tiene_proyector = bool(tiene_proyector)
        # Registramos en el log que se creo la sala
        RegistroLogs.guardar_log("EVENTO", f"Servicio de sala creado: {self.nombre_servicio} ({self.identificacion})")

    # Sobrescribimos calcular_costo para las salas (polimorfismo y sobrecarga)
    def calcular_costo(self, horas, descuento=0.0, con_iva=False):
        # Multiplicamos las horas por el valor de la sala
        total = self.valor_hora * horas
        # Si pide proyector le sumamos 15000 pesos fijos
        if self.__tiene_proyector:
            # Sumamos el cobro adicional del proyector
            total = total + 15000
        # Si mandaron descuento lo restamos
        total = total - (total * descuento)
        # Si pidieron calcular con IVA le sumamos el 19%
        if con_iva:
            # Multiplicamos por 1.19
            total = total * 1.19
        # Devolvemos el valor redondeado
        return round(total, 2)

    # Implementacion de ver_detalle para la sala
    def ver_detalle(self):
        # Texto para indicar si tiene proyector
        proyector = "con proyector" if self.__tiene_proyector else "sin proyector"
        # Retornamos la informacion de la sala
        return f"Sala [{self.identificacion}]: {self.nombre_servicio} ({self.__capacidad} pers, {proyector}) - ${self.valor_hora}/h"


# Segundo servicio especializado: Alquiler de Equipos
class AlquilerEquipo(Servicio):
    # Constructor con el tipo de equipo y cuantos equipos va a alquilar
    def __init__(self, codigo, nombre_servicio, valor_hora, tipo_equipo, cantidad=1):
        # Llamamos al constructor de Servicio
        super().__init__(codigo, nombre_servicio, valor_hora)
        # Validamos que escriban que equipo es y que la cantidad sea positiva
        if not tipo_equipo or cantidad <= 0:
            # Lanzamos error si faltan datos del equipo
            raise DatosInvalidosError("Debe poner el tipo de equipo y una cantidad mayor a 0.")
        # Guardamos tipo y cantidad en atributos privados
        self.__tipo_equipo = tipo_equipo.strip()
        self.__cantidad = int(cantidad)
        # Guardamos el evento en el log
        RegistroLogs.guardar_log("EVENTO", f"Servicio de equipo creado: {self.nombre_servicio} ({self.identificacion})")

    # Sobrescribimos calcular_costo multiplicando tambien por la cantidad de equipos
    def calcular_costo(self, horas, descuento=0.0, con_iva=False):
        # Calculamos tarifa por horas y por cantidad de equipos
        total = self.valor_hora * horas * self.__cantidad
        # Aplicamos descuento si lo hay
        total = total - (total * descuento)
        # Sumamos IVA si se paso el parametro en True
        if con_iva:
            # Agregamos el 19%
            total = total * 1.19
        # Retornamos el resultado redondeado
        return round(total, 2)

    # Implementacion de ver_detalle para equipos
    def ver_detalle(self):
        # Retornamos el resumen del alquiler de equipo
        return f"Equipo [{self.identificacion}]: {self.nombre_servicio} ({self.__tipo_equipo} x{self.__cantidad}) - ${self.valor_hora}/h"


# Tercer servicio especializado: Asesorias Especializadas
class AsesoriaEspecializada(Servicio):
    # Constructor con el tema de asesoria y la modalidad
    def __init__(self, codigo, nombre_servicio, valor_hora, tema, modalidad="Virtual"):
        # Llamamos al constructor padre
        super().__init__(codigo, nombre_servicio, valor_hora)
        # Validamos que la modalidad solo sea Virtual o Presencial
        if modalidad not in ("Virtual", "Presencial"):
            # Si escriben otra cosa lanzamos error
            raise DatosInvalidosError("La modalidad solo puede ser 'Virtual' o 'Presencial'.")
        # Guardamos tema y modalidad
        self.__tema = tema.strip()
        self.__modalidad = modalidad
        # Guardamos el evento en el archivo txt
        RegistroLogs.guardar_log("EVENTO", f"Servicio de asesoria creado: {self.nombre_servicio} ({self.identificacion})")

    # Sobrescribimos calcular_costo agregando transporte si es presencial
    def calcular_costo(self, horas, descuento=0.0, con_iva=False):
        # Calculamos el valor base por horas
        total = self.valor_hora * horas
        # Si el asesor tiene que ir presencial cobramos 20000 de transporte
        if self.__modalidad == "Presencial":
            # Sumamos el recargo
            total = total + 20000
        # Aplicamos descuento si viene en los parametros
        total = total - (total * descuento)
        # Aplicamos IVA si viene en True
        if con_iva:
            # Sumamos el 19%
            total = total * 1.19
        # Retornamos el total
        return round(total, 2)

    # Implementacion de ver_detalle para asesorias
    def ver_detalle(self):
        # Retornamos el detalle de la asesoria
        return f"Asesoria [{self.identificacion}]: {self.nombre_servicio} (Tema: {self.__tema}, {self.__modalidad}) - ${self.valor_hora}/h"