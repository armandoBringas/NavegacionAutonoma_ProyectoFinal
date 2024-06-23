# Importación de bibliotecas y módulos necesarios
import numpy as np  # NumPy se usa para operaciones numéricas
import cv2  # OpenCV para tareas de procesamiento de imágenes
import pygame  # Pygame para tareas de desarrollo de juegos y manejo de entradas de joystick

# Importación de clases necesarias desde los módulos controller y vehicle
from controller import Robot, Camera, GPS  # Clases Robot, Camera y GPS del módulo controller
from vehicle import Car, Driver  # Clases Car y Driver del módulo vehicle

# Importación de funciones y clases necesarias desde Keras
from keras.models import load_model  # Función para cargar un modelo preentrenado de Keras
from keras.optimizers import Adam  # Optimizador Adam para entrenar el modelo

# Constantes
THRESHOLD_DISTANCE_CAR = 6.5  # Distancia umbral para detección de coches en metros
CAR_SPEED = 30  # Velocidad en km/h cuando no se detecta ningún objeto o hay una distancia segura del coche
USE_CONTROLLER = False  # Opción para habilitar o deshabilitar el uso del controlador de videojuegos


class Controller:
    """
    La clase Controller es responsable de manejar las entradas del joystick si el flag USE_CONTROLLER está activado.
    Inicializa el joystick, obtiene el valor del eje y verifica si un botón está presionado.
    """

    DEAD_ZONE = 0.1  # La zona muerta es una pequeña área central del joystick que generalmente está alrededor
    # de la posición de reposo.

    def __init__(self):
        """
        Inicializa la clase Controller. Si USE_CONTROLLER está activado, inicializa pygame y el joystick.
        """
        if USE_CONTROLLER:  # Verificar si el flag USE_CONTROLLER está activado
            pygame.init()  # Inicializar todos los módulos importados de pygame
            pygame.joystick.init()  # Inicializar el módulo de joystick
            self.joystick = pygame.joystick.Joystick(0)  # Crear un nuevo objeto Joystick
            self.joystick.init()  # Inicializar el Joystick

    def get_axis(self, axis):
        """
        Retorna el valor del eje especificado si USE_CONTROLLER está activado.
        Si el valor absoluto del eje es menor que la DEAD_ZONE, retorna 0.
        Si USE_CONTROLLER está desactivado, retorna 0.

        Parámetros:
        axis (int): El eje del cual obtener el valor.

        Retorna:
        float: El valor del eje.
        """
        if USE_CONTROLLER:  # Verificar si el flag USE_CONTROLLER está activado
            value = self.joystick.get_axis(axis)  # Obtener la posición actual del eje dado
            return 0 if abs(value) < self.DEAD_ZONE else value  # Retornar 0 si el valor absoluto es
            # menor que la DEAD_ZONE
        return 0  # Si USE_CONTROLLER está desactivado, retornar 0

    def button_pressed(self, button):
        """
        Verifica si el botón especificado está presionado si USE_CONTROLLER está activado.
        Si USE_CONTROLLER está desactivado, retorna False.

        Parámetros:
        button (int): El botón a verificar si está presionado.

        Retorna:
        bool: True si el botón está presionado, False de otra manera.
        """
        if USE_CONTROLLER:  # Verificar si el flag USE_CONTROLLER está activado
            return self.joystick.get_button(button)  # Retornar True si el botón está presionado, de lo contrario False
        return False  # Si USE_CONTROLLER está desactivado, retornar False


class CarEngine:
    """
    La clase CarEngine es responsable de controlar los movimientos del coche y las interacciones con el entorno.
    Inicializa el coche, el conductor, la cámara, el lidar y la pantalla. También maneja la velocidad y el ángulo de
    dirección del coche.
    """

    MAX_ANGLE = 0.28  # Ángulo máximo de dirección

    def __init__(self):
        """
        Inicializa la clase CarEngine. Inicializa el coche, el conductor, la cámara, el lidar y la pantalla.
        """
        self.robot = Car()  # Inicializar el coche
        self.driver = Driver()  # Inicializar el conductor
        self.timestep = int(self.robot.getBasicTimeStep())  # Obtener el paso de tiempo básico del robot
        self.camera = self._initialize_device("camera")  # Inicializar la cámara
        self.front_camera = self._init_camera_recognition("Front Camera")  # Inicializar la cámara frontal
        # con reconocimiento
        self.gps = self._initialize_device("gps")  # Inicializar el GPS
        self.lidar = self._init_lidar("lidar")  # Inicializar el lidar
        self.display = self.robot.getDevice("display")  # Obtener el dispositivo de pantalla
        self.angle = 0.0  # Inicializar el ángulo de dirección
        self.speed = 25.0  # Inicializar la velocidad

    def _initialize_device(self, device_name):
        """
        Inicializa un dispositivo.

        Parámetros:
        device_name (str): El nombre del dispositivo a inicializar.

        Retorna:
        Device: El dispositivo inicializado.
        """
        device = self.robot.getDevice(device_name)  # Obtener el dispositivo
        device.enable(self.timestep)  # Habilitar el dispositivo
        return device

    def _init_camera_recognition(self, device_name):
        """
        Inicializa una cámara con reconocimiento.

        Parámetros:
        device_name (str): El nombre de la cámara a inicializar.

        Retorna:
        Camera: La cámara inicializada.
        """
        camera = self.robot.getDevice(device_name)  # Obtener la cámara
        camera.enable(self.timestep)  # Habilitar la cámara
        camera.recognitionEnable(self.timestep)  # Habilitar el reconocimiento en la cámara
        return camera

    def _init_lidar(self, device_name):
        """
        Inicializa un lidar.

        Parámetros:
        device_name (str): El nombre del lidar a inicializar.

        Retorna:
        Lidar: El lidar inicializado.
        """
        lidar = self.robot.getDevice(device_name)  # Obtener el lidar
        lidar.enable(self.timestep)  # Habilitar el lidar
        lidar.enablePointCloud()  # Habilitar la nube de puntos en el lidar
        return lidar

    def update_display(self):
        """
        Actualiza la pantalla con la velocidad actual y el ángulo de dirección.
        """
        speed = self.driver.getCurrentSpeed()  # Obtener la velocidad actual
        steering_angle = self.driver.getSteeringAngle()  # Obtener el ángulo de dirección actual
        print(f"Vehicle Speed: {speed:.2f} km/h, Steering Angle: {steering_angle:.5f} rad")  # Imprimir la
        # velocidad y el ángulo de dirección
        speed_label_str = "Speed: "  # Etiqueta de velocidad
        speed_value_str = f"{speed:.2f} km/h"  # Valor de velocidad
        steering_angle_label_str = "Steering Angle: "  # Etiqueta de ángulo de dirección
        steering_angle_value_str = f"{steering_angle:.5f} rad"  # Valor de ángulo de dirección
        self.display.setColor(0x000000)  # Establecer el color de la pantalla en negro
        self.display.fillRectangle(0, 0, self.display.getWidth(), self.display.getHeight())  # Llenar la
        # pantalla con el color
        aquamarine = 0x7FFFD4  # Color aguamarina
        white = 0xFFFFFF  # Color blanco
        self.display.setColor(aquamarine)  # Establecer el color de la pantalla en aguamarina
        self.display.drawText(speed_label_str, 5, 10)  # Dibujar la etiqueta de velocidad
        self.display.drawText(steering_angle_label_str, 5, 30)  # Dibujar la etiqueta de ángulo de dirección
        self.display.setColor(white)  # Establecer el color de la pantalla en blanco
        self.display.drawText(speed_value_str, 50, 10)  # Dibujar el valor de velocidad
        self.display.drawText(steering_angle_value_str, 100, 30)  # Dibujar el valor de ángulo de dirección

    def set_steering_angle(self, value):
        """
        Establece el ángulo de dirección. Si el valor absoluto de la entrada es menor que la zona muerta, establece el
        ángulo de dirección en 0.

        Parámetros:
        value (float): El valor para establecer el ángulo de dirección.
        """
        DEAD_ZONE = 0.06  # Zona muerta
        value = value if abs(value) > DEAD_ZONE else 0.0  # Si el valor absoluto de la entrada es menor que
        # la zona muerta, establecerlo en 0
        self.angle = self.MAX_ANGLE * value  # Establecer el ángulo de dirección

    def set_speed(self, kmh):
        """
        Establece la velocidad.

        Parámetros:
        kmh (float): La velocidad en km/h para establecer.
        """
        self.speed = kmh  # Establecer la velocidad
        self.driver.setCruisingSpeed(self.speed)  # Establecer la velocidad de crucero

    def update(self):
        """
        Actualiza la pantalla, el ángulo de dirección y la velocidad.
        """
        self.update_display()  # Actualizar la pantalla
        self.driver.setSteeringAngle(self.angle)  # Establecer el ángulo de dirección
        self.driver.setCruisingSpeed(self.speed)  # Establecer la velocidad de crucero

    def get_image(self):
        """
        Obtiene una imagen de la cámara, la redimensiona y la convierte al espacio de color BGR.

        Retorna:
        np.array: La imagen.
        """
        raw_image = self.camera.getImage()  # Obtener la imagen cruda de la cámara
        image = np.frombuffer(raw_image, np.uint8).reshape((self.camera.getHeight(), self.camera.getWidth(), 4))
        # Redimensionar la imagen cruda
        image = cv2.resize(image, (200, 66))  # Redimensionar la imagen
        image = image[35:, :, :]  # Recortar la imagen
        image = cv2.resize(image, (200, 66))  # Redimensionar la imagen
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)  # Convertir la imagen al espacio de color BGR
        return image

    def get_lid_ranges(self):
        """
        Obtiene los rangos del lidar, calcula el rango medio y detecta si se detecta un peatón o coche.

        Retorna:
        tuple: El rango medio, número de láseres, rango mínimo y detección.
        """
        range_image = self.lidar.getRangeImage()  # Obtener la imagen de rango del lidar
        ranges = [val for val in range_image if not np.isinf(val)]  # Obtener los rangos que no son infinitos
        num_lasers = len(ranges)  # Obtener el número de láseres
        mean_range = np.mean(ranges)  # Calcular el rango medio
        min_range = min(ranges) if ranges else float('inf')  # Obtener el rango mínimo si hay rangos, de lo
        # contrario establecerlo en infinito
        print(f'Num Lasers: {num_lasers}')  # Imprimir el número de láseres
        detection = None  # Inicializar la detección
        if num_lasers == 0:  # Si no hay láseres
            print("Detected: None")  # Imprimir que no se detecta nada
        elif num_lasers < 150:  # Si el número de láseres es menor que 150
            detection = "Pedestrian"  # Establecer la detección en peatón
            print("Detected: Pedestrian")  # Imprimir que se detecta un peatón
        else:  # Si el número de láseres no es menor que 150
            detection = "Car"  # Establecer la detección en coche
            print("Detected: Car")  # Imprimir que se detecta un coche
        return mean_range, num_lasers, min_range, detection  # Retornar el rango medio, número de láseres,
        # rango mínimo y detección


def main_loop(car, model, controller):
    """
    El bucle principal del programa. Obtiene una imagen del coche, predice el ángulo de dirección, establece el ángulo
    de dirección y la velocidad,y actualiza el coche. Si se detecta un peatón o coche, establece la velocidad en 0. Si
    se detecta un coche y el rango mínimo es menor que la distancia umbral, establece la velocidad en 0. Si no se detecta
    nada, establece la velocidad en la velocidad del coche. Si se presiona el botón del controlador, rompe el bucle.

    Parámetros:
    car (CarEngine): El coche.
    model (Model): El modelo.
    controller (Controller): El controlador.
    """
    try:
        TIMER = 30  # Temporizador
        COUNTER = 0  # Contador
        predicted_steering_angle = 0.0  # Ángulo de dirección predicho
        while car.robot.step() != -1:  # Mientras el robot esté funcionando
            if COUNTER == TIMER:  # Si el contador es igual al temporizador
                image = car.get_image()  # Obtener una imagen del coche
                preprocessed_image = np.array([image])  # Preprocesar la imagen
                predicted_steering_angle = model.predict(preprocessed_image)[0][0]  # Predecir el ángulo de dirección
                print(f"Predicted steering angle: {predicted_steering_angle}")  # Imprimir el ángulo de
                # dirección predicho
                COUNTER = 0  # Reiniciar el contador
                car.set_steering_angle(predicted_steering_angle)  # Establecer el ángulo de dirección
                dist, num_lasers, min_range, detection = car.get_lid_ranges()  # Obtener los rangos del lidar
                if detection == "Pedestrian":  # Si se detecta un peatón
                    car.set_speed(0)  # Establecer la velocidad en 0
                elif detection == "Car":  # Si se detecta un coche
                    if min_range < THRESHOLD_DISTANCE_CAR:  # Si el rango mínimo es menor que la distancia umbral
                        car.set_speed(0)  # Establecer la velocidad en 0
                    else:  # Si el rango mínimo no es menor que la distancia umbral
                        car.set_speed(CAR_SPEED)  # Establecer la velocidad en la velocidad del coche
                else:  # Si no se detecta nada
                    car.set_speed(CAR_SPEED)  # Establecer la velocidad en la velocidad del coche
                car.update()  # Actualizar el coche
                print(f"Vehicle Speed: {car.speed} km/h, Steering Angle: {car.angle} rad")  # Imprimir la velocidad
                # y el ángulo de dirección
            COUNTER += 1  # Incrementar el contador
            if USE_CONTROLLER:  # Si se usa el controlador
                pygame.event.pump()  # Bombear la cola de eventos
                if controller.button_pressed(0):  # Si se presiona el botón del controlador
                    break  # Romper el bucle
    finally:
        if USE_CONTROLLER:  # Si se usa el controlador
            pygame.quit()  # Salir de pygame
        print("Exiting the main loop.")  # Imprimir que se está saliendo del bucle principal


if __name__ == "__main__":
    car = CarEngine()  # Inicializar el coche
    controller = Controller()  # Inicializar el controlador
    model = load_model('../models/behavioral_cloning.keras')  # Cargar el modelo
    model.compile(Adam(learning_rate=0.001), loss='mse')  # Compilar el modelo
    main_loop(car, model, controller)  # Ejecutar el bucle principal
