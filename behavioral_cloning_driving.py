# Bibliotecas para el procesamiento de imágenes
import cv2
import numpy as np

# Biblioteca para interactuar con el sistema operativo
import os

# Bibliotecas para aprendizaje automático
from keras.models import load_model
from keras.optimizers import Adam

# Bibliotecas para el control de robots y vehículos
from controller import Robot, Camera, GPS
from vehicle import Car, Driver


class CarEngine:
    """
    La clase CarEngine encapsula la funcionalidad del motor de un coche en el contexto de una simulación.
    Incluye métodos para inicializar dispositivos, actualizar la pantalla, configurar el ángulo de dirección
    y la velocidad, actualizar el estado del coche y obtener la imagen de la cámara del coche.
    """

    def __init__(self):
        """
        Inicializa la instancia de CarEngine con valores predeterminados.
        Configura el robot, el conductor, el timestep, la cámara, el GPS, la pantalla, el ángulo,
        la velocidad y el ángulo máximo.
        """
        self.robot = Car()  # Instancia de la clase Car
        self.driver = Driver()  # Instancia de la clase Driver
        self.timestep = int(self.robot.getBasicTimeStep())  # Timestep básico del robot
        self.camera = self._initialize_device("camera")  # Inicializar el dispositivo de cámara
        self.gps = self._initialize_device("gps")  # Inicializar el dispositivo GPS
        self.display = self.robot.getDevice("display")  # Obtener el dispositivo de pantalla
        self.angle = 0.0  # Ángulo de dirección inicial
        self.speed = 25.0  # Velocidad inicial
        self.MAX_ANGLE = 0.28  # Ángulo de dirección máximo

    def _initialize_device(self, device_name):
        """
        Inicializa un dispositivo en el robot.

        Este método recupera un dispositivo del robot por su nombre, lo habilita con el timestep del robot
        y devuelve el dispositivo.

        Args:
            device_name (str): El nombre del dispositivo a inicializar.

        Returns:
            Device: El dispositivo inicializado.
        """
        device = self.robot.getDevice(device_name)  # Obtener el dispositivo del robot
        device.enable(self.timestep)  # Habilitar el dispositivo con el timestep del robot
        return device  # Devolver el dispositivo inicializado

    def update_display(self):
        """
        Actualiza la pantalla en la interfaz del robot.

        Este método recupera la velocidad actual y el ángulo de dirección del robot, los formatea en cadenas
        de texto, y los muestra en la interfaz del robot. Primero se limpia la pantalla con un color negro,
        luego se dibujan las etiquetas de velocidad y ángulo de dirección en color aguamarina,
        y los valores reales se dibujan en color blanco.

        La velocidad se muestra en km/h y el ángulo de dirección se muestra en radianes.
        """
        # Obtener la velocidad actual del robot
        speed = self.driver.getCurrentSpeed()

        # Obtener el ángulo de dirección actual del robot
        steering_angle = self.driver.getSteeringAngle()

        # Preparar las etiquetas y los valores para la velocidad y el ángulo de dirección
        speed_label_str = "Speed: "
        speed_value_str = f"{speed:.2f} km/h"
        steering_angle_label_str = "Steering Angle: "
        steering_angle_value_str = f"{steering_angle:.5f} rad"

        # Limpiar la pantalla con color negro
        self.display.setColor(0x000000)
        self.display.fillRectangle(0, 0, self.display.getWidth(), self.display.getHeight())

        # Definir los colores para las etiquetas y los valores
        aquamarine = 0x7FFFD4
        white = 0xFFFFFF

        # Dibujar las etiquetas de velocidad y ángulo de dirección en color aguamarina
        self.display.setColor(aquamarine)
        self.display.drawText(speed_label_str, 5, 10)
        self.display.drawText(steering_angle_label_str, 5, 30)

        # Dibujar los valores de velocidad y ángulo de dirección en color blanco
        self.display.setColor(white)
        self.display.drawText(speed_value_str, 50, 10)
        self.display.drawText(steering_angle_value_str, 100, 30)

    def set_steering_angle(self, value):
        """
        Configura el ángulo de dirección del coche.

        Este método toma un valor como entrada, verifica si su valor absoluto es mayor que el umbral
        de la zona muerta, y si lo es, establece el ángulo de dirección del coche al producto del ángulo
        de dirección máximo y el valor de entrada. Si el valor absoluto de la entrada no es mayor que el umbral
        de la zona muerta, el ángulo de dirección se establece en 0.

        Se espera que el valor de entrada esté en el rango de -1 a 1, y se mapea al rango de -MAX_ANGLE a MAX_ANGLE.

        Args:
            value (float): El ángulo de dirección deseado en el rango de -1 a 1.
        """
        DEAD_ZONE = 0.06
        value = value if abs(value) > DEAD_ZONE else 0.0
        # Mapear los valores de -1 a 1 a -MAX_ANGLE a MAX_ANGLE
        self.angle = self.MAX_ANGLE * value

    def set_speed(self, kmh):
        """
        Configura la velocidad de crucero del coche.

        Este método toma un valor de velocidad en kilómetros por hora (km/h) como entrada
        y establece la velocidad de crucero del coche a este valor.

        Args:
            kmh (float): La velocidad de crucero deseada en km/h.
        """
        self.speed = kmh  # Establecer la velocidad del coche
        self.driver.setCruisingSpeed(self.speed)  # Establecer la velocidad de crucero del coche

    def update(self):
        """
        Actualiza el estado del coche.

        Este método actualiza la pantalla en la interfaz del robot, establece el ángulo de dirección del coche
        y establece la velocidad de crucero del coche. La pantalla se actualiza con la velocidad actual
        y el ángulo de dirección del coche. El ángulo de dirección se establece en el ángulo actual del coche.
        La velocidad de crucero se establece en la velocidad actual del coche.
        """
        self.update_display()  # Actualizar la pantalla en la interfaz del robot
        self.driver.setSteeringAngle(self.angle)  # Establecer el ángulo de dirección del coche
        self.driver.setCruisingSpeed(self.speed)  # Establecer la velocidad de crucero del coche

    def get_image(self):
        """
        Recupera una imagen de la cámara del coche y la procesa.

        Este método recupera una imagen sin procesar de la cámara del coche, la convierte en un array de numpy
        y la redimensiona para que coincida con las dimensiones de la cámara. Luego, la imagen se redimensiona
        a un tamaño estándar de 200x66 píxeles para mantener la consistencia. Se recorta una parte de la imagen
        para enfocarse en las partes relevantes, y la imagen recortada se redimensiona nuevamente al tamaño estándar.
        Finalmente, el color de la imagen se convierte de formato BGRA a BGR, y se devuelve la imagen procesada.

        Returns:
            np.ndarray: La imagen procesada de la cámara del coche.
        """
        raw_image = self.camera.getImage()  # Obtener la imagen sin procesar de la cámara
        # Convertir la imagen sin procesar en un array de numpy y redimensionarla para que coincida con las
        # dimensiones de la cámara
        image = np.frombuffer(raw_image, np.uint8).reshape(
            (self.camera.getHeight(), self.camera.getWidth(), 4)
        )
        image = cv2.resize(image, (200, 66))  # Redimensionar la imagen a 200x66 píxeles
        image = image[35:, :, :]  # Recortar la imagen para enfocarse en las partes relevantes
        image = cv2.resize(image, (200, 66))  # Redimensionar la imagen recortada a 200x66 píxeles
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)  # Convertir el color de la imagen de formato BGRA a BGR
        return image  # Devolver la imagen procesada


def main_loop(car, model):
    """
    El bucle principal de la simulación del coche.

    Esta función toma una instancia de CarEngine y un modelo entrenado como entrada, y ejecuta el bucle principal
    de la simulación del coche. El bucle se ejecuta mientras el método step del robot no devuelva -1,
    lo que indica el final de la simulación.

    En cada iteración del bucle, si un contador alcanza un valor de temporizador predefinido, la función recupera
    una imagen de la cámara del coche, procesa la imagen y utiliza el modelo para predecir el ángulo de dirección
    basado en la imagen procesada. El ángulo de dirección predicho se establece como el ángulo de dirección del coche,
    y la velocidad del coche se establece en un valor fijo. Se actualiza el estado del coche y el contador se
    reinicia a 0.
    Si el contador no alcanza el valor del temporizador, simplemente se incrementa.

    Si ocurre una excepción durante la ejecución del bucle, la función imprime un mensaje indicando la salida
    del bucle principal.

    Args:
        car (CarEngine): La instancia de CarEngine a controlar.
        model (Model): El modelo entrenado a utilizar para predecir el ángulo de dirección.
    """
    try:
        TIMER = 30  # El valor del temporizador para actualizar el estado del coche
        COUNTER = 0  # Un contador para rastrear el número de iteraciones
        predicted_steering_angle = 0.0  # El ángulo de dirección predicho
        while car.robot.step() != -1:  # Ejecutar el bucle mientras el método step del robot no devuelva -1
            if COUNTER == TIMER:  # Si el contador alcanza el valor del temporizador
                image = car.get_image()  # Obtener una imagen de la cámara del coche
                preprocessed_image = np.array([image])  # Procesar la imagen

                # Utilizar el modelo para predecir el ángulo de dirección basado en la imagen procesada
                predicted_steering_angle = model.predict(preprocessed_image)[0][0]
                print(f"Predicted steering angle: {predicted_steering_angle}")
                # Imprimir el ángulo de dirección predicho
                COUNTER = 0  # Reiniciar el contador

                car.set_steering_angle(predicted_steering_angle)
                # Establecer el ángulo de dirección del coche al ángulo de dirección predicho
                car.set_speed(25)  # Establecer la velocidad del coche a un valor fijo

                car.update()  # Actualizar el estado del coche
            COUNTER += 1  # Incrementar el contador
    finally:
        print("Exiting the main loop.")  # Imprimir un mensaje indicando la salida del bucle principal


if __name__ == "__main__":
    # Crear una instancia de la clase CarEngine. Esta clase encapsula la funcionalidad del motor de un coche
    # en el contexto de una simulación.
    car = CarEngine()

    # Cargar el modelo entrenado desde el archivo 'gear_fifth.keras'. El modelo se carga sin compilar.
    # El parámetro 'safe_mode' se establece en False, lo que significa que el modelo se carga incluso
    # si se guardó con una versión superior de Keras. El parámetro 'compile' se establece en False,
    # lo que significa que el modelo se carga sin su estado compilado.
    model = load_model('gear_fifth.keras', safe_mode=False, compile=False)

    # Compilar el modelo con el optimizador Adam y una tasa de aprendizaje de 0.001.
    # La función de pérdida se establece en 'mse' (error cuadrático medio).
    model.compile(Adam(learning_rate=0.001), loss='mse')

    # Ejecutar el bucle principal de la simulación del coche con la instancia de CarEngine y el modelo
    # entrenado como entrada.
    main_loop(car, model)
