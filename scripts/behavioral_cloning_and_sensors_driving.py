import os
import csv
import numpy as np
import cv2
from datetime import datetime
import pygame
from controller import Robot, Camera, GPS
from vehicle import Car, Driver
from keras.models import load_model
from keras.optimizers import Adam

# Constants
THRESHOLD_DISTANCE_CAR = 5.0  # Threshold distance for car detection in meters
CAR_SPEED = 40  # Speed in km/h when no object is detected or safe distance from car
USE_CONTROLLER = False  # Option to enable or disable the use of video game controller


class Controller:
    DEAD_ZONE = 0.1

    def __init__(self):
        if USE_CONTROLLER:
            pygame.init()
            pygame.joystick.init()
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()

    def get_axis(self, axis):
        if USE_CONTROLLER:
            value = self.joystick.get_axis(axis)
            return 0 if abs(value) < self.DEAD_ZONE else value
        return 0

    def button_pressed(self, button):
        if USE_CONTROLLER:
            return self.joystick.get_button(button)
        return False


class CarEngine:
    MAX_ANGLE = 0.28

    def __init__(self):
        self.robot = Car()
        self.driver = Driver()
        self.timestep = int(self.robot.getBasicTimeStep())
        self.camera = self._initialize_device("camera")
        self.front_camera = self._init_camera_recognition("Front Camera")
        self.gps = self._initialize_device("gps")
        self.lidar = self._init_lidar("lidar")
        self.display = self.robot.getDevice("display")
        self.angle = 0.0
        self.speed = 25.0

    def _initialize_device(self, device_name):
        device = self.robot.getDevice(device_name)
        device.enable(self.timestep)
        return device

    def _init_camera_recognition(self, device_name):
        camera = self.robot.getDevice(device_name)
        camera.enable(self.timestep)
        camera.recognitionEnable(self.timestep)
        return camera

    def _init_lidar(self, device_name):
        lidar = self.robot.getDevice(device_name)
        lidar.enable(self.timestep)
        lidar.enablePointCloud()
        return lidar

    def update_display(self):
        speed = self.driver.getCurrentSpeed()
        steering_angle = self.driver.getSteeringAngle()
        speed_label_str = "Speed: "
        speed_value_str = f"{speed:.2f} km/h"
        steering_angle_label_str = "Steering Angle: "
        steering_angle_value_str = f"{steering_angle:.5f} rad"
        self.display.setColor(0x000000)
        self.display.fillRectangle(0, 0, self.display.getWidth(), self.display.getHeight())
        aquamarine = 0x7FFFD4
        white = 0xFFFFFF
        self.display.setColor(aquamarine)
        self.display.drawText(speed_label_str, 5, 10)
        self.display.drawText(steering_angle_label_str, 5, 30)
        self.display.setColor(white)
        self.display.drawText(speed_value_str, 50, 10)
        self.display.drawText(steering_angle_value_str, 100, 30)

    def set_steering_angle(self, value):
        DEAD_ZONE = 0.06
        value = value if abs(value) > DEAD_ZONE else 0.0
        self.angle = self.MAX_ANGLE * value

    def set_speed(self, kmh):
        self.speed = kmh
        self.driver.setCruisingSpeed(self.speed)

    def update(self):
        self.update_display()
        self.driver.setSteeringAngle(self.angle)
        self.driver.setCruisingSpeed(self.speed)

    def get_image(self):
        raw_image = self.camera.getImage()
        image = np.frombuffer(raw_image, np.uint8).reshape((self.camera.getHeight(), self.camera.getWidth(), 4))
        image = cv2.resize(image, (200, 66))
        image = image[35:, :, :]
        image = cv2.resize(image, (200, 66))
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
        return image

    def get_lid_ranges(self):
        range_image = self.lidar.getRangeImage()
        ranges = [val for val in range_image if not np.isinf(val)]
        num_lasers = len(ranges)
        mean_range = np.mean(ranges)
        min_range = min(ranges) if ranges else float('inf')
        print(f'Num Lasers: {num_lasers}')
        detection = None
        if num_lasers == 0:
            print("Detected: None")
        elif num_lasers < 150:
            detection = "Pedestrian"
            print("Detected: Pedestrian")
        else:
            detection = "Car"
            print("Detected: Car")
        return mean_range, num_lasers, min_range, detection


def main_loop(car, model, controller):
    try:
        TIMER = 30
        COUNTER = 0
        predicted_steering_angle = 0.0
        while car.robot.step() != -1:
            if COUNTER == TIMER:
                image = car.get_image()
                preprocessed_image = np.array([image])
                predicted_steering_angle = model.predict(preprocessed_image)[0][0]
                print(f"Predicted steering angle: {predicted_steering_angle}")
                COUNTER = 0
                car.set_steering_angle(predicted_steering_angle)
                dist, num_lasers, min_range, detection = car.get_lid_ranges()
                if detection == "Pedestrian":
                    car.set_speed(0)
                elif detection == "Car":
                    if min_range < THRESHOLD_DISTANCE_CAR:
                        car.set_speed(0)
                    else:
                        car.set_speed(CAR_SPEED)
                else:
                    car.set_speed(CAR_SPEED)
                car.update()
            COUNTER += 1
            if USE_CONTROLLER:
                pygame.event.pump()
                if controller.button_pressed(0):
                    break
    finally:
        if USE_CONTROLLER:
            pygame.quit()
        print("Exiting the main loop.")


if __name__ == "__main__":
    car = CarEngine()
    controller = Controller()
    model = load_model('../models/behavioral_cloning.keras')
    model.compile(Adam(learning_rate=0.001), loss='mse')
    main_loop(car, model, controller)
