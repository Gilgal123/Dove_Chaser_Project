# Configuration Module for Dove Chaser System
"""
This module contains all constants, GPIO port definitions, and servo parameters
used in the Dove Chaser system. The system detects doves and operates the mechanical
components to aim and shoot a deterrent (water). Below are the configuration settings
used throughout the system.

Constants:
    - DEBUG: Debug mode flag.
    - DELTA_FRAME: Time between frames.
    - TIMEOUT_S: Time allowed to look for a dove.
    - SHOOTING_TIME: Duration for shooting.
    - MIN_DOVE_HEIGHT: Minimum height for a valid bird detection.
    - FIELD OF VIEW: Camera field of view in degrees.
    - SERVO CONTROL: Parameters for controlling the servos.
    - GPIO PORTS: Pin mappings for LEDs and servos.

"""

# ============================
# Debug and Timing Constants
# ============================
DEBUG = True  # Enables or disables debug mode (prints/logging)

DELTA_FRAME = 0.05      # Default time between frames in seconds (for normal mode)
DELTA_FRAME_dyn = 0.035 # Dynamic time between frames (for dove detection)
DELTA_FRAME_stat = 0.1  # Static time between frames (for servo control)
TIMEOUT_S = 15          # Maximum time to wait for a dove in seconds
SHOOTING_TIME = 1       # Time duration for shooting (water deterrent) in seconds
ROLL_TIME_AIM = 0.1     # Time for rolling while aiming
ROLL_TIME_STATIC = 2    # Time for rolling 30 degrees in static mode
PITCH_DEG_DOWN = 65     # Pitch angle (downward) for servo
PITCH_DEG_UP = 97       # Pitch angle (upward) for servo
RELATIVE_ROLL_SPEED = 0.5  # Relative roll speed (-1 to 1, - left, + right)

# ============================
# Bird Detection Constants
# ============================
BIRD_CLASS_ID = 16      # Class ID of bird in Jetson detection model
BIRD_CLASS_ID_2 = 17    # Secondary class ID for alternative bird types
FRAME_TO_VANISH = 10    # Number of frames to determine if a dove has vanished
FRAME_TO_PITCH = 10     # Number of frames to average for picking median of dove y_center
MIN_DOVE_HEIGHT = 1     # Minimum height (in pixels) for bird detection
REAL_DOVE_HEIGHT = 0.2  # Real-world height of the dove (meters)

# ============================
# Field of View and Aiming Constants
# ============================
FOV_deg = 16.7         # Field of view of the camera in degrees
TOP_AIM = 160          # Upper aiming limit in pixels
MIDDLE_PIXEL = 180     # Middle of the frame (used for centering)
HEIGHT_PIXEL = 360     # Height of the image frame (pixels)
BOTTOM_AIM = 200       # Lower aiming limit in pixels
LEFT_AIM = 310         # Left aiming limit in pixels
RIGHT_AIM = 330        # Right aiming limit in pixels

# ============================
# Gravity and Initial Velocity
# ============================
GRAVITY_CONSTANT = 9.81 # Gravitational constant (m/s^2)
INITIAL_V = 5.2        # Initial velocity of water in m/s (to shoot)

# ============================
# GPIO Port Assignments
# ============================
LED_G_PORT = 37        # GPIO pin for green LED (active when no dove detected)
LED_R_PORT = 35        # GPIO pin for red LED (active when dove detected)
SHOOT_PUMP_PORT = 31   # GPIO pin to control water pump (active when shooting)
PUMP_IS_FULL_PORT = 29 # GPIO pin to check if pump has water (1 if full)
PITCH_SERVO_PIN = 32   # GPIO pin for pitch servo control (vertical movement)
ROLL_SERVO_PIN = 33    # GPIO pin for roll servo control (horizontal movement)

# ============================
# Servo Control Constants
# ============================
FREQ = 50              # Frequency of the servo signals in Hz
MAX_DUTY = 15          # Max duty cycle for pitch servo
MIN_DUTY = 0           # Min duty cycle for pitch servo
RIGHT_DUTY = 7.1       # Duty cycle to move servo to the right
STATIC_DUTY = 7.5      # Duty cycle for static servo position
LEFT_DUTY = 7.9        # Duty cycle to move servo to the left

# ============================
# Ballistic Calculation Parameters
# ============================
l1 = 7.4  # Distance factor for ballistic calculations
l2 = 1.64 # Constant for ballistic trajectory
l3 = 1.55 # Constant for ballistic trajectory
l4 = 7.9  # Constant for ballistic trajectory
l5 = 3.2  # Constant for ballistic trajectory
lim = 12  # Limit for ballistic calculations
s_cal = 90 # Calibration constant for ballistic trajectory

