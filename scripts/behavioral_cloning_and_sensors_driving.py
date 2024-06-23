import os
import csv
import numpy as np
import cv2
from datetime import datetime
import pygame
from controller import Robot, Camera, GPS, LidarPoint
from vehicle import Car, Driver


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
        # print("="*46)
        # print("Num objects: ",num_obj)
        areas = []
        for i in range(num_obj):
            obj = self.front_camera.getRecognitionObjects()[i]
            id = obj.getId()
            sizes = obj.getSize()
            area = abs(sizes[0] * sizes[1])
            # print(id)
            # print(f"Alto: {sizes[0]}")
            # print(f"Ancho: {sizes[1]}")
            # print(f"Area: {area}" )
            if area < 50.0:
                areas.append(area)
        return areas

    def get_lid_ranges(self):
        range_image = self.lidar.getRangeImage()

        ranges = [val for val in range_image if np.isinf(val) != True]
        num_lasers = len(ranges)
        mean_range = np.mean(ranges)
        # print(mean_range)
        # print(f'Num Lasers: {len(ranges)}')
        return mean_range, num_lasers


def main_loop(car, controller):
    try:
        while car.robot.step() != -1:
            pygame.event.pump()

            if controller.button_pressed(0):
                break

            # car.sensor_detection()
            areas_detec = car.get_obj_areas()

            print(f"Areas: {areas_detec}")
            dist, num_lasers = car.get_lid_ranges()
            # print(f"Range: {proximity}")

            axis_steering = controller.get_axis(0)
            axis_speed = controller.get_axis(1)

            car.set_steering_angle(axis_steering)
            car.set_speed(0)
            car.update()

    finally:
        pygame.quit()


if __name__ == "__main__":
    car = CarEngine()
    controller = Controller()
    main_loop(car, controller)