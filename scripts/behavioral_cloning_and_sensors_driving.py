import os
import csv
import numpy as np
import cv2
from datetime import datetime
import pygame
from controller import Robot, Camera, GPS, LidarPoint
from vehicle import Car, Driver

class file_handler:
    def __init__(self, folder="train_images", csv_file="images.csv", save_images = True):
        # Attributes
        self.folder = folder
        self.csv_file = csv_file
        self.save_images = save_images
        self._directory_exists()
        self.last_row = self._get_last_row()
        self.pic_num = 0 if self.last_row == 0 else self.last_row - 1
        self.csv_writer = self._csv_writer()
        self.csv_file_handler = open(self.csv_file, mode='a', newline='') if self.save_images is True else None
        self.last_image = None

    #Methods

    def _directory_exists(self):
        if self.save_images and not os.path.exists(self.folder):
            os.makedirs(self.folder)
    
    def _get_last_row(self):
        if not os.path.isfile(self.csv_file):
            return 0
        with open(self.csv_file, mode='r') as f:
            last_row = 0
            reader = csv.reader(f)
            for last_row, _ in enumerate(reader,1):
                pass
            return last_row

    def _csv_writer(self):
        if self.save_images is False:
            return None
        csv_file = open(self.csv_file, mode='a', newline='')
        csv_writer = csv.writer(csv_file)
        if self._csv_exist_and_content() is False:
            csv_writer.writerow(["Image Name", "Steering Angle"])
        return csv_writer
    
    def _csv_exist_and_content(self):
        return os.path.isfile(self.csv_file) and os.path.getsize(self.csv_file) > 0
    
    def write_path_image(self, steering_angle):
        current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M")
        file_name = os.path.join(self.folder, f"M-{current_datetime}-{self.pic_num}.png")
        if file_name != self.last_image:
            self.csv_writer.writerow([file_name, steering_angle])
            print(f"Image saved: {file_name}, Steering angle: {steering_angle}")
            self.last_image = file_name
            self.pic_num += 1      

    def flush_and_close(self):
        if self.save_images is True:
            self.csv_file_handler.flush()
            self.csv_file_handler.close()

class Controller:
    DEAD_ZONE = 0.1

    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()

    def get_axis(self, axis):
        value = self.joystick.get_axis(axis)
        return 0 if abs(value) < self.DEAD_ZONE else value

    def button_pressed(self, button):
        return self.joystick.get_button(button)

class CarEngine:
    def __init__(self):
        self.robot = Car()
        self.driver = Driver()
        self.timestep = int(self.robot.getBasicTimeStep())
        self.camera = self._initialize_device("camera")
        self.front_camera = self._init_camera_recognition("Front Camera")
        self.gps = self._initialize_device("gps")
        self.lidar = self._init_lidar("lidar")
        self.angle = 0.0
        self.speed = 0.0

    def _initialize_device(self, device_name):
        device = self.robot.getDevice(device_name)
        device.enable(self.timestep)
        return device

    def _init_camera_recognition(self, device_name):
        camara = self.robot.getDevice(device_name)
        camara.enable(self.timestep)
        camara.recognitionEnable(self.timestep)
        return camara

    def _init_lidar(self, device_name):
        lidar = self.robot.getDevice(device_name)
        lidar.enable(self.timestep)
        lidar.enablePointCloud()
        return lidar

    def set_steering_angle(self, wheel_angle):
        if (wheel_angle - self.angle) > 0.1:
            wheel_angle = self.angle + 0.1
        if (wheel_angle - self.angle) < -0.1:
            wheel_angle = self.angle - 0.1
        self.angle = max(min(wheel_angle, 0.5), -0.5)

    def set_speed(self, kmh):
        self.speed = kmh

    def update(self):
        self.driver.setSteeringAngle(self.angle)
        self.driver.setCruisingSpeed(self.speed)

    def get_image(self):
        raw_image = self.camera.getImage()
        return np.frombuffer(raw_image, np.uint8).reshape(
            (self.camera.getHeight(), self.camera.getWidth(), 4)
        )

    def get_obj_areas(self):
        num_obj = self.front_camera.getRecognitionNumberOfObjects()
        #print("="*46)
        #print("Num objects: ",num_obj)
        areas = []
        for i in range(num_obj):
            obj = self.front_camera.getRecognitionObjects()[i]
            id = obj.getId()
            sizes = obj.getSize()
            area = abs(sizes[0] * sizes[1])
            #print(id)
            #print(f"Alto: {sizes[0]}")
            #print(f"Ancho: {sizes[1]}")
            #print(f"Area: {area}" )
            if area < 50.0:
                areas.append(area)
        return areas

    def get_lid_ranges(self):
        range_image = self.lidar.getRangeImage()
        
        ranges = [val for val in range_image if np.isinf(val) != True]
        num_lasers = len(ranges)
        mean_range = np.mean(ranges)
        #print(mean_range)
        #print(f'Num Lasers: {len(ranges)}')
        return mean_range,  num_lasers

def main_loop(car, controller):
    try:
        while car.robot.step() != -1:
            pygame.event.pump()

            if controller.button_pressed(0):
                break
            
            #car.sensor_detection()
            areas_detec = car.get_obj_areas()
            
            print(f"Areas: {areas_detec}")
            dist, num_lasers = car.get_lid_ranges()
            #print(f"Range: {proximity}")

            axis_steering = controller.get_axis(0)
            axis_speed = controller.get_axis(1)

            car.set_steering_angle(axis_steering)
            car.set_speed(0)
            car.update()

    finally:
        #file_handler.flush_and_close()
        pygame.quit()

if __name__ == "__main__":
    car = CarEngine()
    controller = Controller()
    main_loop(car, controller)