# Module to set Dove object
"""
This module defines the Dove class, which represents an object (dove) with attributes
for its position, height, and validity. It also includes utility functions for
data processing and object management.

Modules:
    - Config: A configuration module with predefined constants like FRAME_TO_PITCH and DEBUG mode.
    - numpy (np): A library for numerical computations and handling arrays.

Functions:
    - s_median(arr): Computes the median of an array while ignoring NaN values.

Classes:
    - Dove: Represents a dove object with methods to update its state, check validity,
            and retrieve its position and height.

"""

import Config
import numpy as np


def s_median(arr):
    """
    Calculate the median of an array, ignoring NaN values.

    Args:
        arr (array-like): Input array of numeric values.

    Returns:
        float or None: The median of the non-NaN values in the array,
                       or None if the array contains only NaN values.
    """
    filtered_data = np.array([x for x in arr if not np.isnan(x)])
    if len(filtered_data) == 0:
        return None
    return np.median(filtered_data)


class Dove:
    """
    A class representing a dove with position, height, and validity attributes.

    Attributes:
        is_valid (bool): Whether the dove is valid.
        x_center (int): The x-coordinate of the dove's center.
        y_center (numpy array): Array storing the y-coordinates of the dove's center over frames.
        height (numpy array): Array storing the dove's height over frames.
        index (int): The current index for circular buffer management.
    """

    def __init__(self, is_valid=False, x_center=0, y_center=0, height=0):
        """
        Initialize a new Dove instance.

        Args:
            is_valid (bool): Whether the dove is valid. Default is False.
            x_center (int): The x-coordinate of the dove's center. Default is 0.
            y_center (int): The initial y-coordinate of the dove's center. Default is 0.
            height (int): The initial height of the dove. Default is 0.
        """
        self.is_valid = is_valid
        self.x_center = x_center
        self.y_center = np.full(Config.FRAME_TO_PITCH, np.nan)
        self.height = np.full(Config.FRAME_TO_PITCH, np.nan)
        self.index = 0
        if Config.DEBUG:  # Debug print
            print("Created dove\n", Config.sys.stderr)

    def print_dove(self):
        """
        Print the dove's status, including its validity, position, and height.

        Note:
            This method is called only in DEBUG mode.
        """
        print("Dove status:\n")
        print("is valid: ", self.is_valid, '\n', Config.sys.stderr)
        if self.is_valid:
            print("x_center: ", self.x_center, '\n', Config.sys.stderr)
            print("y_center: ", self.y_center, '\n', Config.sys.stderr)
            print("height: ", self.height, '\n', Config.sys.stderr)

    def update_dove(self, is_valid, x_center=0, y_center=0, height=0):
        """
        Update the dove's status, including validity, position, and height.

        Args:
            is_valid (bool): Whether the dove is valid.
            x_center (int): The new x-coordinate of the dove's center. Default is 0.
            y_center (int): The new y-coordinate of the dove's center. Default is 0.
            height (int): The new height of the dove. Default is 0.
        """
        self.is_valid = is_valid
        if not is_valid:
            self.y_center[self.index] = np.nan
            self.height[self.index] = np.nan
        else:
            self.x_center = x_center
            self.y_center[self.index] = y_center
            self.height[self.index] = height
        self.index = (self.index + 1) % Config.FRAME_TO_PITCH

    def is_dove(self):
        """
        Check if the dove is valid.

        Returns:
            bool: True if the dove is valid, False otherwise.
        """
        return self.is_valid

    def get_center(self):
        """
        Get the dove's center position.

        Returns:
            tuple: A tuple containing the x-coordinate and the median y-coordinate
                   (ignoring NaN values).
        """
        return self.x_center, s_median(self.y_center)

    def get_height(self):
        """
        Get the dove's height.

        Returns:
            float or None: The median height of the dove (ignoring NaN values).
        """
        return s_median(self.height)
