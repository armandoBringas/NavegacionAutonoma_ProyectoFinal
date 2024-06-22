# Bibliotecas para interacciones con el sistema operativo y operaciones de archivos CSV
import os
import csv

# Biblioteca para operaciones de fecha y hora
from datetime import datetime

# Bibliotecas para operaciones numéricas y procesamiento de imágenes
import numpy as np
import cv2

# Biblioteca para desarrollo de juegos y manejo de entradas del joystick
import pygame

# Bibliotecas para control de robots y vehículos
from controller import Robot, Camera, GPS
from vehicle import Car, Driver


class FileHandler:
    """
    Una clase utilizada para manejar operaciones de archivos como crear directorios,
    escribir en archivos CSV y guardar imágenes.
    """

    def __init__(self, folder="train_images", csv_file="images.csv", save_images=False):
        """
        Inicializar la clase FileHandler.

        Parámetros:
        folder (str): El nombre de la carpeta donde se guardarán las imágenes.
        csv_file (str): El nombre del archivo CSV donde se guardarán los nombres
                        de las imágenes y los ángulos de dirección.
        save_images (bool): Una bandera que indica si se deben guardar las imágenes o no.
        """
        self.folder = folder  # El nombre de la carpeta donde se guardarán las imágenes.
        self.csv_file = csv_file  # El nombre del archivo CSV donde se guardarán los nombres
        # de las imágenes y los ángulos de dirección.
        self.save_images = save_images  # Una bandera que indica si se deben guardar las imágenes o no.
        self._directory_exists()  # Verificar si el directorio existe, si no, crearlo.
        self.last_row = self._get_last_row()  # Obtener el último número de fila del archivo CSV.
        self.pic_num = 0 if self.last_row == 0 else self.last_row - 1
        # Establecer el número de imagen en 0 si el último número de fila es 0,
        # de lo contrario, establecerlo en el último número de fila menos 1.
        self.csv_writer = self._csv_writer()  # Inicializar el escritor de CSV.
        self.csv_file_handler = open(self.csv_file, mode='a', newline='') if self.save_images else None
        # Abrir el manejador de archivos CSV en modo de adición si save_images es True,
        # de lo contrario, establecerlo en None.
        self.last_image = None  # Inicializar la última imagen en None.

    def _directory_exists(self):
        """
        Verificar si el directorio existe, si no, crearlo.
        """
        if self.save_images and not os.path.exists(self.folder):
            os.makedirs(self.folder)

    def _get_last_row(self):
        """
        Obtener el último número de fila del archivo CSV.

        Retorna:
        int: El último número de fila.
        """
        if not os.path.isfile(self.csv_file):
            return 0  # Si el archivo CSV no existe, retornar 0.
        with open(self.csv_file, mode='r') as f:  # Abrir el archivo CSV en modo de lectura.
            last_row = 0  # Inicializar el último número de fila en 0.
            reader = csv.reader(f)  # Crear un lector de CSV para el archivo.
            for last_row, _ in enumerate(reader, 1):
                pass  # Enumerar sobre las filas en el archivo CSV, comenzando la cuenta desde 1.
            return last_row  # Después de recorrer todas las filas, retornar el último número de fila.

    def _csv_writer(self):
        """
        Inicializar el escritor de CSV.

        Retorna:
        csv.writer: El escritor de CSV.
        """
        if not self.save_images:
            return None  # Si save_images es False, retornar None.
        csv_file = open(self.csv_file, mode='a', newline='')  # Abrir el archivo CSV en modo de adición.
        csv_writer = csv.writer(csv_file)  # Crear un escritor de CSV para el archivo.
        if not self._csv_exist_and_content():
            csv_writer.writerow(["Image Name", "Steering Angle"])
            # Si el archivo CSV no existe o no tiene contenido, escribir la fila de encabezado en el archivo CSV.
        return csv_writer  # Retornar el escritor de CSV.

    def _csv_exist_and_content(self):
        """
        Verificar si el archivo CSV existe y tiene contenido.

        Retorna:
        bool: True si el archivo CSV existe y tiene contenido, False en caso contrario.
        """
        return os.path.isfile(self.csv_file) and os.path.getsize(self.csv_file) > 0

    def write_path_image(self, steering_angle):
        """
        Escribir la ruta de la imagen y el ángulo de dirección en el archivo CSV.

        Parámetros:
        steering_angle (float): El ángulo de dirección.
        """
        current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M")
        # Obtener la fecha y hora actuales y formatearlas como "YYYY-MM-DD_HH-MM".
        file_name = os.path.join(self.folder, f"M-{current_datetime}-{self.pic_num}.png")
        # Crear el nombre del archivo uniendo el nombre de la carpeta, la fecha y hora formateadas,
        # y el número de imagen, y agregando la extensión ".png".
        if file_name != self.last_image:
            self.csv_writer.writerow([file_name, steering_angle])
            # Escribir el nombre del archivo y el ángulo de dirección en el archivo CSV.
            print(f"Image saved: {file_name}, Steering angle: {steering_angle}")
            # Imprimir un mensaje indicando que la imagen ha sido guardada y mostrando el nombre del archivo
            # y el ángulo de dirección.
            self.last_image = file_name  # Establecer el nombre del archivo de la última imagen
            # en el nombre del archivo actual.
            self.pic_num += 1  # Incrementar el número de imagen en 1.

    def flush_and_close(self):
        """
        Vaciar y cerrar el manejador de archivos CSV.
        """
        if self.save_images:
            self.csv_file_handler.flush()
            self.csv_file_handler.close()


class Controller:
    """
    Una clase utilizada para manejar las entradas del joystick.
    """

    DEAD_ZONE = 0.05

    def __init__(self):
        """
        Inicializar la clase Controller.
        """
        pygame.init()
        pygame.joystick.init()
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()

    def get_axis(self, axis):
        """
        Obtener el valor del eje especificado.

        Parámetros:
        axis (int): El número del eje.

        Retorna:
        float: El valor del eje. Si el valor absoluto es menor que la zona muerta, retorna 0.0.
        """
        value = self.joystick.get_axis(axis)
        return 0.0 if abs(value) < self.DEAD_ZONE else value

    def button_pressed(self, button):
        """
        Verificar si el botón especificado está presionado.

        Parámetros:
        button (int): El número del botón.

        Retorna:
        bool: True si el botón está presionado, False en caso contrario.
        """
        return self.joystick.get_button(button)


class CarEngine:
    """
    Una clase utilizada para controlar los movimientos del coche y mostrar la velocidad y el ángulo de dirección.
    """

    def __init__(self):
        """
        Inicializar la clase CarEngine.
        """
        self.robot = Car()  # Crear una instancia de la clase Car para controlar los movimientos del coche.
        self.driver = Driver()  # Crear una instancia de la clase Driver para controlar las acciones del conductor.
        self.timestep = int(self.robot.getBasicTimeStep())
        # Obtener el paso de tiempo básico del robot, que es el intervalo de tiempo entre dos pasos
        # consecutivos de control.
        self.camera = self._initialize_device("camera")  # Inicializar el dispositivo de cámara para capturar imágenes.
        self.gps = self._initialize_device("gps")  # Inicializar el dispositivo GPS para obtener las coordenadas GPS.
        self.display = self.robot.getDevice("display")  # Obtener el dispositivo de visualización para mostrar la
        # velocidad y el ángulo de dirección.
        self.angle = 0.0  # Establecer el ángulo de dirección inicial en 0.0.
        self.speed = 30.0  # Establecer la velocidad inicial en 30.0 km/h.
        self.MAX_STEERING = 1.0  # Establecer el ángulo de dirección máximo en 1.0.

    def _initialize_device(self, device_name):
        """
        Inicializar el dispositivo especificado.

        Parámetros:
        device_name (str): El nombre del dispositivo.

        Retorna:
        Device: El dispositivo inicializado.
        """
        device = self.robot.getDevice(device_name)
        device.enable(self.timestep)
        return device

    def set_steering_angle(self, joystick_value):
        """
        Establecer el ángulo de dirección basado en el valor del joystick.

        Parámetros:
        joystick_value (float): El valor del joystick.
        """
        self.angle = self.MAX_STEERING * joystick_value

    def set_speed(self, kmh):
        """
        Establecer la velocidad del coche.

        Parámetros:
        kmh (float): La velocidad en kilómetros por hora.
        """
        self.speed = kmh

    def update_display(self):
        """
        Actualizar la pantalla con la velocidad actual y el ángulo de dirección.
        """
        speed = self.driver.getCurrentSpeed()  # Obtener la velocidad actual del conductor.
        steering_angle = self.driver.getSteeringAngle()
        # Obtener el ángulo de dirección actual del conductor.

        speed_label_str = "Speed: "  # Definir la cadena de etiqueta de velocidad.
        speed_value_str = f"{speed:.2f} km/h"  # Formatear la cadena de valor de velocidad con la velocidad actual.
        steering_angle_label_str = "Steering Angle: "
        # Definir la cadena de etiqueta del ángulo de dirección.
        steering_angle_value_str = f"{steering_angle:.5f} rad"
        # Formatear la cadena de valor del ángulo de dirección con el ángulo de dirección actual.

        self.display.setColor(0x000000)  # Establecer el color de la pantalla a negro.
        self.display.fillRectangle(0, 0, self.display.getWidth(), self.display.getHeight())
        # Rellenar el rectángulo de la pantalla con el color actual.

        aquamarine = 0x7FFFD4  # Definir el color aguamarina.
        white = 0xFFFFFF  # Definir el color blanco.

        self.display.setColor(aquamarine)  # Establecer el color de la pantalla a aguamarina.
        self.display.drawText(speed_label_str, 5, 10)
        # Dibujar la cadena de etiqueta de velocidad en la posición especificada.
        self.display.drawText(steering_angle_label_str, 5, 30)
        # Dibujar la cadena de etiqueta del ángulo de dirección en la posición especificada.

        self.display.setColor(white)  # Establecer el color de la pantalla a blanco.
        self.display.drawText(speed_value_str, 50, 10)
        # Dibujar la cadena de valor de velocidad en la posición especificada.
        self.display.drawText(steering_angle_value_str, 100, 30)
        # Dibujar la cadena de valor del ángulo de dirección en la posición especificada.

    def update(self):
        """
        Actualizar la pantalla y establecer el ángulo de dirección y la velocidad de crucero.
        """
        self.update_display()
        self.driver.setSteeringAngle(self.angle)
        self.driver.setCruisingSpeed(self.speed)

    def get_image(self):
        """
        Obtener la imagen actual de la cámara.

        Retorna:
        np.array: La imagen como un array de numpy.
        """
        raw_image = self.camera.getImage()  # Obtener la imagen actual de la cámara como una imagen sin procesar.
        return np.frombuffer(raw_image, np.uint8).reshape(
            (self.camera.getHeight(), self.camera.getWidth(), 4)
        )
        # Convertir la imagen sin procesar a un array de numpy con la forma correcta y retornarla.


def main_loop(car, controller, image_saver):
    """
    El bucle principal del programa. Maneja los movimientos del coche en función de las entradas del controlador
    y guarda imágenes si es necesario.

    Parámetros:
    car (CarEngine): El objeto motor del coche que controla los movimientos del coche
                     y muestra la velocidad y el ángulo de dirección.
    controller (Controller): El objeto controlador que maneja las entradas del joystick.
    image_saver (FileHandler): El objeto manejador de archivos que maneja las operaciones de archivos
                               como crear directorios, escribir en archivos CSV y guardar imágenes.

    La función se ejecuta en un bucle hasta que se presiona el botón 0 en el controlador. En cada iteración del bucle,
    procesa la cola de eventos de pygame, verifica si se presiona el botón 0 y, de ser así, rompe el bucle.
    Si el atributo save_images del objeto image_saver es True y el contador de pasos es mayor o igual a steps_per_second,
    escribe la ruta de la imagen y el ángulo de dirección en el archivo CSV y guarda la imagen. Luego, reinicia el contador
    de pasos a 0. Obtiene los valores de los ejes 0 y 1 del controlador, establece el ángulo de dirección del coche
    en función del valor del eje 0 y actualiza el coche. Después del bucle, vacía y cierra el manejador de archivos CSV
    y cierra pygame.
    """
    steps_per_second = 5  # Definir el número de pasos por segundo.
    step_counter = 0  # Inicializar el contador de pasos en 0.
    try:
        while car.robot.step() != -1:
            pygame.event.pump()  # Procesar eventos de pygame.

            if controller.button_pressed(0):  # Si se presiona el botón 0, romper el bucle.
                break

            step_counter += 1  # Incrementar el contador de pasos en 1.
            if image_saver.save_images and (step_counter >= steps_per_second):
                image_saver.write_path_image(axis_steering)
                car.camera.saveImage(image_saver.last_image, 1)
                # Guardar la imagen.
                step_counter = 0  # Reiniciar el contador de pasos.

            axis_steering = controller.get_axis(0)  # Obtener el valor del eje 0.
            axis_speed = controller.get_axis(1)  # Obtener el valor del eje 1.

            car.set_steering_angle(axis_steering)  # Establecer el ángulo de dirección del coche.
            car.update()  # Actualizar el coche.

    finally:
        image_saver.flush_and_close()  # Vaciar y cerrar el manejador de archivos CSV.
        pygame.quit()  # Cerrar pygame.


if __name__ == "__main__":
    car = CarEngine()
    # Crear una instancia de la clase CarEngine. Esta clase se utiliza para controlar los movimientos del coche
    # y mostrar la velocidad y el ángulo de dirección.

    controller = Controller()
    # Crear una instancia de la clase Controller. Esta clase se utiliza para manejar las entradas del joystick.

    image_saver = FileHandler()
    # Crear una instancia de la clase FileHandler. Esta clase se utiliza para manejar operaciones de archivos
    # como crear directorios, escribir en archivos CSV y guardar imágenes.

    main_loop(car, controller, image_saver)
    # Llamar al bucle principal del programa con el coche, el controlador y el manejador de archivos como argumentos.
    # El bucle principal maneja los movimientos del coche en función de las entradas del controlador
    # y guarda imágenes si es necesario.
