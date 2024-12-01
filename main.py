#!/usr/bin/env python3
"""
Dove Chaser System
==================
This script operates the Dove Chaser system, which detects and deters doves using:
- A Jetson Nano for real-time bird detection via neural networks.
- Servo motors for precise aiming.
- A water pump to deter birds.
- GPIO controls for LED indicators and pump mechanisms.

The system utilizes multithreading for real-time detection and control while maintaining responsiveness.

Modules:
- Config: Stores configuration constants.
- Dove_object: Manages the dove state.
- Servo: Controls servo motor operations.
- jetson_inference and jetson_utils: Provide neural network-based dove detection.

Usage:
Run this script to initiate the Dove Chaser system. Ensure all hardware is connected and configured as per the `Config` module.
"""

import threading
import time
import sys
import signal
import math
import Config
import Dove_object
import Servo
import RPi.GPIO as GPIO
from jetson_inference import detectNet
from jetson_utils import videoSource, videoOutput
import jetson_utils


def signal_handle(sig, frame):
    """
    Handle the Ctrl+C signal to safely clean up GPIO resources before exiting.

    Args:
        sig: The signal number.
        frame: Current stack frame.
    """
    print("Ctrl+C detected, cleaning up GPIO.")
    GPIO.cleanup()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handle)


def apply_zoom_with_sharpening(frame, zoom_factor=2):
    """
    Apply zoom to a frame with optional sharpening.

    Args:
        frame: The input frame (Jetson video frame).
        zoom_factor: The factor by which to zoom the frame (default 2).

    Returns:
        Processed frame after applying zoom.
    """
    if zoom_factor == 1:
        return frame

    width, height = frame.width, frame.height
    new_width, new_height = int(width / zoom_factor), int(height / zoom_factor)
    x1, y1 = (width - new_width) // 2, (height - new_height) // 2
    x2, y2 = x1 + new_width, y1 + new_height

    cropped_frame = jetson_utils.cudaAllocMapped(width=new_width, height=new_height, format=frame.format)
    jetson_utils.cudaCrop(frame, cropped_frame, (x1, y1, x2, y2))
    jetson_utils.cudaDeviceSynchronize()
    return cropped_frame


def find_closest_bird(bird_detections, frame_width, frame_height):
    """
    Identify the bird closest to the center of the frame.

    Args:
        bird_detections (list): List of detected bird objects.
        frame_width (int): Width of the frame in pixels.
        frame_height (int): Height of the frame in pixels.

    Returns:
        closest_bird: The bird detection closest to the frame's center, or None if no bird is valid.
    """
    frame_center_x, frame_center_y = frame_width / 2, frame_height / 2
    min_distance = float('inf')
    closest_bird = None

    for detection in bird_detections:
        x_center, y_center = detection.Center
        if detection.Height >= Config.MIN_DOVE_HEIGHT:
            distance = math.sqrt((x_center - frame_center_x) ** 2 + (y_center - frame_center_y) ** 2)
            if distance < min_distance:
                min_distance = distance
                closest_bird = detection

    return closest_bird


def detect_dove(dove):
    """
    Continuously detect doves using a neural network and update the Dove object.

    Args:
        dove (Dove_object.Dove): Object to store detection state.
    """
    net = detectNet("ssd-mobilenet-v2", threshold=0.4)
    camera = videoSource("csi://0")
    output = videoOutput("display://0")

    while True:
        org_img = camera.Capture()
        if org_img is None:
            continue

        img = apply_zoom_with_sharpening(org_img)
        detections = net.Detect(img)
        bird_detections = [d for d in detections if d.ClassID in {Config.BIRD_CLASS_ID, Config.BIRD_CLASS_ID_2}]

        detected_dove, x_center, y_center, height = False, 0, 0, 0
        if bird_detections:
            closest_dove = find_closest_bird(bird_detections, img.width, img.height)
            if closest_dove:
                detected_dove = True
                x_center, y_center = closest_dove.Center
                height = closest_dove.Height

        dove.update_dove(detected_dove, x_center, y_center, height)
        if Config.DEBUG:
            output.Render(img)

        time.sleep(Config.DELTA_FRAME)


def wait_for_dove(dove):
    """
    Monitor for the presence of a dove for a specific timeout period.

    Args:
        dove (Dove_object.Dove): Dove object to check for updates.

    Returns:
        bool: True if a dove is detected within the timeout, False otherwise.
    """
    time_out = Config.TIMEOUT_S
    if Config.DEBUG:
        print("Waiting for a dove...")

    while time_out > 0:
        if dove.is_dove():
            print("Dove detected!")
            return True
        time.sleep(Config.DELTA_FRAME)
        time_out -= Config.DELTA_FRAME

    print("No dove detected within timeout.")
    return False


def aim(dove, servo):
    """
    Aim the servos to center the dove in the frame.

    Args:
        dove (Dove_object.Dove): Dove object with position updates.
        servo (Servo.Servo): Servo control object.

    Returns:
        bool: True if aiming succeeds, False otherwise.
    """
    max_attempts = 5
    x_center, y_center = dove.get_center()
    print("Aiming at dove...")

    while not (Config.LEFT_AIM <= x_center <= Config.RIGHT_AIM and
               Config.TOP_AIM <= y_center <= Config.BOTTOM_AIM):
        if max_attempts == 0:
            return False
        servo.Aim_side(dove)
        servo.Aim_pitch(dove)
            if not dove.is_dove():
                return False
        x_center, y_center = dove.get_center()
        max_attempts -= 1

    servo.final_pitch_aim(dove.get_height())
    return True


def init():
    """
    Initialize all hardware and create worker threads.

    Returns:
        tuple: (Dove_object.Dove, Servo.Servo) initialized objects.
    """
    dove = Dove_object.Dove()
    GPIO.setmode(GPIO.BOARD)
    servo = Servo.Servo()

    GPIO.setup(Config.LED_G_PORT, GPIO.OUT)
    GPIO.setup(Config.LED_R_PORT, GPIO.OUT)
    GPIO.setup(Config.SHOOT_PUMP_PORT, GPIO.OUT)
    GPIO.setup(Config.PUMP_IS_FULL_PORT, GPIO.IN)

    GPIO.output(Config.LED_G_PORT, GPIO.HIGH)
    GPIO.output(Config.LED_R_PORT, GPIO.LOW)
    GPIO.output(Config.SHOOT_PUMP_PORT, GPIO.LOW)

    detection_thread = threading.Thread(target=detect_dove, args=(dove,))
    detection_thread.start()

    return dove, servo


def main():
    """
    Main execution loop for the Dove Chaser system.
    """
    dove, servo = init()
    print("Initialization complete. Starting main loop.")

    while True:
        GPIO.output(Config.SHOOT_PUMP_PORT, GPIO.LOW)
        GPIO.output(Config.LED_G_PORT, GPIO.HIGH)
        GPIO.output(Config.LED_R_PORT, GPIO.LOW)

        if not wait_for_dove(dove):
            servo.pose_change()
            continue

        GPIO.output(Config.LED_R_PORT, GPIO.HIGH)
        Config.DELTA_FRAME = Config.DELTA_FRAME_dyn

        if not aim(dove, servo):
            servo.pose_change()
            continue

        if GPIO.input(Config.PUMP_IS_FULL_PORT):
            GPIO.output(Config.SHOOT_PUMP_PORT, GPIO.HIGH)
            time.sleep(Config.SHOOTING_TIME)
            GPIO.output(Config.SHOOT_PUMP_PORT, GPIO.LOW)
            servo.reset_pitch()


if __name__ == "__main__":
    main()
