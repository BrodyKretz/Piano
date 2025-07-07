#!/usr/bin/env python3
# config.py - Configuration settings and initialization for the application

import pygame
import pygame.mixer

# Screen dimensions
WIDTH, HEIGHT = 1600, 1080  # Wide format for better space utilization
TITLE = "Piano Hand Detector"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (220, 220, 220)
RED = (255, 0, 0)
GREEN = (100, 200, 100)
DARK_GREEN = (70, 170, 70)
BLUE = (100, 150, 255)
DARK_BLUE = (70, 120, 220)
YELLOW = (255, 255, 0)
IVORY = (255, 255, 240)

# Layout dimensions
BUTTON_AREA_HEIGHT = 80
BUTTON_HEIGHT = 50
BUTTON_WIDTH = 150  # Wider buttons
BUTTON_MARGIN = 30

# Camera area
CAMERA_AREA_HEIGHT = 480
# Initialize rect in initialize_pygame since it requires pygame to be initialized first

# Calibration panel area
CALIBRATION_AREA_WIDTH = 300
CALIBRATION_AREA_LEFT = WIDTH - CALIBRATION_AREA_WIDTH - 20
CALIBRATION_AREA_TOP = BUTTON_AREA_HEIGHT + 20
CALIBRATION_AREA_HEIGHT = CAMERA_AREA_HEIGHT

# Terminal area
TERMINAL_WIDTH = 300
TERMINAL_LEFT = 20
TERMINAL_TOP = BUTTON_AREA_HEIGHT + 20
TERMINAL_HEIGHT = CAMERA_AREA_HEIGHT

# Piano settings
PIANO_TOP = BUTTON_AREA_HEIGHT + CAMERA_AREA_HEIGHT + 60
PIANO_HEIGHT = 220
WHITE_KEY_WIDTH = 24
BLACK_KEY_WIDTH = WHITE_KEY_WIDTH * 0.6
BLACK_KEY_HEIGHT = PIANO_HEIGHT * 0.6

# Slider area
SLIDER_AREA_HEIGHT = 40
SLIDER_AREA_TOP = BUTTON_AREA_HEIGHT + CAMERA_AREA_HEIGHT + 10

# Piano sound settings
NUM_KEYS = 88
START_NOTE = 21  # A0 MIDI note number
KEY_PATTERN = [True, False, True, False, True, True, False, True, False, True, False, True]  # W,B,W,B,W,W,B,W,B,W,B,W

# Button configuration
BUTTON_LABELS = ["Begin", "Add/Remove Overlay", "Keyboard Mode", "Auto Calibrate", "Manual Calibrate", "Quit Program"]
BUTTON_COLORS = [BLUE, BLUE, BLUE, BLUE, BLUE, GREEN]
BUTTON_ACTIVE_COLORS = [DARK_BLUE, DARK_BLUE, DARK_BLUE, DARK_BLUE, DARK_BLUE, DARK_GREEN]

# Global objects that will be initialized later
CAMERA_DISPLAY_RECT = None
buttons = None
recording = False
camera_active = False
overlay_active = False
piano_overlay_active = False
keyboard_overlay_active = False
calibration_mode = False
manual_calibration_mode = False

def initialize_pygame():
    """Initialize pygame and return screen and clock objects"""
    global CAMERA_DISPLAY_RECT
    
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
    
    # Create display surface
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    
    # Create clock for timing
    clock = pygame.time.Clock()
    
    # Initialize camera display rect now that pygame is initialized
    CAMERA_DISPLAY_RECT = pygame.Rect(WIDTH//2 - 320, BUTTON_AREA_HEIGHT + 20, 640, 480)
    
    print("Pygame initialized successfully")
    return screen, clock

# Create buttons
def create_buttons():
    """Create button objects for the UI"""
    global buttons
    
    buttons = []
    for i, label in enumerate(BUTTON_LABELS):
        x = BUTTON_MARGIN + i * (BUTTON_WIDTH + BUTTON_MARGIN)
        y = (BUTTON_AREA_HEIGHT - BUTTON_HEIGHT) // 2
        buttons.append({
            "rect": pygame.Rect(x, y, BUTTON_WIDTH, BUTTON_HEIGHT),
            "label": label,
            "active": False,
            "color": BUTTON_COLORS[i],
            "active_color": BUTTON_ACTIVE_COLORS[i]
        })
    return buttons