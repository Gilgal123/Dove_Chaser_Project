# Module to set Servo object
"""
This module defines the Servo class and related functions for controlling
servo motors to aim at and track doves. It integrates calculations for angles
and ballistic adjustments based on real-world physics.

Modules:
    - Config: Contains configuration parameters like servo pin assignments, frequency, and debug mode.
    - time: Used for delays in servo control.
    - RPi.GPIO as GPIO: Library for GPIO pin control on Raspberry Pi.
    - Dove_object: Module for managing dove objects.
    - angles_map: Module for managing angle mappings.
    - math: Provides mathematical operations.

Functions:
    - deg_to_duty(deg): Converts an angle in degrees to a servo duty cycle.
    - real_alpha_calc_balistics(alpha_deg, OB): Computes the correct pitch angle
      using ballistics to account for distance and gravity.

Classes:
    - Servo: Manages servo motors for pitch and roll adjustments to aim at a target.
"""

import time
import RPi.GPIO as GPIO
import Config
import Dove_object
import angles_map
import math


def deg_to_duty(deg):
    """
    Convert an angle in degrees to a duty cycle for the servo.

    Args:
        deg (float): The angle in degrees to be converted.

    Returns:
        float: The corresponding duty cycle.
    """
    return (deg * (Config.MAX_DUTY - Config.MIN_DUTY) / 180 + Config.MIN_DUTY)


def real_alpha_calc_balistics(alpha_deg, OB):
    """
    Calculate the corrected pitch angle based on direct angle to the target,
    height in pixels, and field of view.

    Args:
        alpha_deg (float): Direct angle to the target in degrees.
        OB (float): Height of the target (dove) in pixels.

    Returns:
        float: The corrected angle for aiming, or NaN if the target is out of range.
    """
    FOV = math.radians(Config.FOV_deg)
    alpha = math.radians(min(alpha_deg))

    # Step 1: Calculate the distance to the target.
    D = (Config.REAL_DOVE_HEIGHT * Config.HEIGHT_PIXEL) / (2 * OB * math.tan(FOV / 2))

    # Step 2: Calculate the ballistic correction angle.
    E = (Config.GRAVITY_CONSTANT * D) / (Config.INITIAL_V ** 2)
    dis = 1.0 - 2.0 * E * math.sin(alpha) - (E * math.cos(alpha)) ** 2
    if dis < 0:
        print("Too far - abort")
        return float('nan')

    real_alpha = math.degrees(math.atan((1 - dis ** 0.5) / (E * math.cos(alpha))))

    if real_alpha > 45:
        print("Invalid angle - abort")
        return float('nan')

    return real_alpha


class Servo:
    """
    Class to manage servo motors for targeting and tracking.

    Attributes:
        pitch_deg (int): Current pitch angle of the servo in degrees.
        pitch_servo (PWM): PWM instance for controlling the pitch servo.
        roll_servo (PWM): PWM instance for controlling the roll servo.
        alpha_to_beta_map (dict): Map of angles for ballistic adjustments.
        beta_to_alpha_map (dict): Reverse map of angles for ballistic adjustments.
    """

    def __init__(self):
        """
        Initialize the servo motors and their parameters.
        """
        self.pitch_deg = Config.PITCH_DEG_DOWN
        GPIO.setmode(GPIO.BOARD)
        self.pitch_servo = GPIO.PWM(Config.PITCH_SERVO_PIN, Config.FREQ)
        self.pitch_servo.start(deg_to_duty(self.pitch_deg))
        self.roll_servo = GPIO.PWM(Config.ROLL_SERVO_PIN, Config.FREQ)
        self.roll_servo.start(Config.STATIC_DUTY)
        self.alpha_to_beta_map, self.beta_to_alpha_map = angles_map.alpha_beta_maps()

    def print_servos(self):
        """
        Print the current status of the servos. Debug mode only.
        """
        print("Pitch servo angle: ", self.pitch_deg, '\n', Config.sys.stderr)

    def Aim_side(self, dove):
        """
        Adjust the roll servo to center the dove horizontally in the frame.

        Args:
            dove (Dove): Dove object to track.

        Returns:
            bool: True if successful, False otherwise.
        """
        x_center, y_center = dove.get_center()
        timeout = Config.TIMEOUT_S
        undetected_to = 5

        while ((x_center < Config.LEFT_AIM) or (x_center > Config.RIGHT_AIM)) and (timeout > 0):
            dove.print_dove()
            if not dove.is_dove():
                while undetected_to > 0:
                    if dove.is_dove():
                        break
                    time.sleep(Config.ROLL_TIME_AIM)
                    undetected_to -= Config.ROLL_TIME_AIM
                if not dove.is_dove():
                    print("Dove gone!\n")
                    return False
            undetected_to = 5

            duty = Config.RIGHT_DUTY if x_center < Config.LEFT_AIM else Config.LEFT_DUTY
            self.roll_servo.ChangeDutyCycle(duty)
            time.sleep(Config.ROLL_TIME_AIM)
            self.roll_servo.ChangeDutyCycle(Config.STATIC_DUTY)
            x_center, y_center = dove.get_center()
            timeout -= Config.ROLL_TIME_AIM

        if timeout <= 0:
            print("Aim Failed!")
            return False
        print("Roll Aim success!")
        return True

    def Aim_pitch(self, dove):
        """
        Adjust the pitch servo to center the dove vertically in the frame.

        Args:
            dove (Dove): Dove object to track.

        Returns:
            bool: True if successful, False otherwise.
        """
        x_center, y_center = dove.get_center()
        timeout = Config.TIMEOUT_S
        undetected_to = 5

        while ((y_center is None) or ((y_center < Config.TOP_AIM) or (y_center > Config.BOTTOM_AIM))) and (timeout > 0):
            if not dove.is_dove():
                while undetected_to > 0:
                    if dove.is_dove():
                        break
                    time.sleep(Config.ROLL_TIME_AIM)
                    undetected_to -= Config.ROLL_TIME_AIM
                if not dove.is_dove():
                    print("Dove gone!\n")
                    return False
            undetected_to = 5

            self.pitch_deg += 1 if y_center < Config.TOP_AIM else -1
            if self.pitch_deg < self.alpha_to_beta_map[-16] or self.pitch_deg > self.alpha_to_beta_map[45]:
                print("not in pitch range")
                return False
            self.pitch_servo.ChangeDutyCycle(deg_to_duty(self.pitch_deg))
            time.sleep(Config.ROLL_TIME_AIM)
            x_center, y_center = dove.get_center()
            timeout -= Config.ROLL_TIME_AIM

        if timeout <= 0:
            print("Aim Failed!")
            return False
        print("Pitch Aim success!")
        return True

    def final_pitch_aim(self, height):
        """
        Perform the final pitch adjustment based on ballistic calculations.

        Args:
            height (float): Height of the dove in pixels.

        Returns:
            bool: True if successful, False otherwise.
        """
        naive_alpha = self.beta_to_alpha_map[round(self.pitch_deg)]
        real_alpha = real_alpha_calc_balistics(naive_alpha, height)
        if math.isnan(real_alpha):
            return False
        self.pitch_deg = round(self.alpha_to_beta_map[round(real_alpha)], 0)
        self.pitch_servo.ChangeDutyCycle(deg_to_duty(self.pitch_deg))

    def pose_change(self):
        """
        Rotate the roll servo to a new static pose and toggle the pitch angle.
        """
        duty = Config.RIGHT_DUTY
        self.roll_servo.ChangeDutyCycle(duty)
        time.sleep(Config.ROLL_TIME_STATIC)
        self.roll_servo.ChangeDutyCycle(Config.STATIC_DUTY)
        time.sleep(0.5)
        if Config.DEBUG:
            print("Rotate right - static\n")
        self.pitch_deg = Config.PITCH_DEG_UP if self.pitch_deg == Config.PITCH_DEG_DOWN else Config.PITCH_DEG_DOWN
        self.pitch_servo.ChangeDutyCycle(deg_to_duty(self.pitch_deg))

    def reset_pitch(self):
        """
        Reset the pitch servo to its default downward position.
        """
        self.pitch_deg = Config.PITCH_DEG_DOWN
        self.pitch_servo.ChangeDutyCycle(deg_to_duty(self.pitch_deg))
