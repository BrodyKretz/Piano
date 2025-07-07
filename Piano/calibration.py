#!/usr/bin/env python3
# calibration.py - Handles skin color calibration for hand detection

import cv2
import numpy as np
import pygame
import config
from terminal import add_terminal_message

# Import these modules only when needed to avoid circular imports
hand_detection_module = None

# Global variables for calibration
calibration_mode = False
calibration_rect = None  # Will define a rectangle where user should place hand
calibration_countdown = 0
calibration_samples = []

# Global variables for manual calibration
manual_calibration_mode = False
manual_min_h, manual_max_h = 0, 20  # Initial HSV range values
manual_min_s, manual_max_s = 20, 255
manual_min_v, manual_max_v = 70, 255
slider_active = None  # Track which slider is being adjusted

def _import_modules():
    """Import dependent modules only when needed to avoid circular imports"""
    global hand_detection_module
    if hand_detection_module is None:
        import hand_detection
        hand_detection_module = hand_detection

def initialize_calibration():
    """Initialize calibration settings"""
    global calibration_mode, manual_calibration_mode
    
    calibration_mode = False
    manual_calibration_mode = False
    config.calibration_mode = False
    config.manual_calibration_mode = False

def start_calibration():
    """Start the auto skin color calibration process"""
    global calibration_mode, calibration_rect, calibration_countdown, calibration_samples
    
    # Reset calibration variables
    calibration_mode = True
    config.calibration_mode = True
    calibration_samples = []
    
    # Create a rectangle in the center of the camera view for hand placement
    rect_width, rect_height = 200, 200
    rect_x = config.CAMERA_DISPLAY_RECT.left + (config.CAMERA_DISPLAY_RECT.width - rect_width) // 2
    rect_y = config.CAMERA_DISPLAY_RECT.top + (config.CAMERA_DISPLAY_RECT.height - rect_height) // 2
    calibration_rect = pygame.Rect(rect_x, rect_y, rect_width, rect_height)
    
    # Set countdown for 5 seconds
    calibration_countdown = 5 * 30  # 5 seconds at 30 FPS
    
    add_terminal_message("Automatic calibration started. Place your hand in the box.")

def process_calibration_frame(frame):
    """Process a frame during calibration mode"""
    global calibration_countdown, calibration_mode, calibration_samples
    
    # Make sure hand_detection module is imported
    _import_modules()
    
    # Extract the region of interest (where hand should be placed)
    roi_x = calibration_rect.x - config.CAMERA_DISPLAY_RECT.left
    roi_y = calibration_rect.y - config.CAMERA_DISPLAY_RECT.top
    roi_width = calibration_rect.width
    roi_height = calibration_rect.height
    
    # Ensure ROI stays within frame boundaries
    roi_x = max(0, min(roi_x, frame.shape[1] - 1))
    roi_y = max(0, min(roi_y, frame.shape[0] - 1))
    roi_width = min(roi_width, frame.shape[1] - roi_x)
    roi_height = min(roi_height, frame.shape[0] - roi_y)
    
    # Extract the ROI
    roi = frame[roi_y:roi_y+roi_height, roi_x:roi_x+roi_width]
    
    if roi.size > 0:  # Make sure ROI is not empty
        # Convert to HSV for skin color analysis
        hsv_roi = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV)
        
        # Add current sample to collection
        calibration_samples.append(hsv_roi)
    
    # Draw rectangle on frame to show where to place hand
    cv2.rectangle(frame, (roi_x, roi_y), (roi_x + roi_width, roi_y + roi_height), (0, 255, 0), 2)
    
    # Add text instructions and countdown
    seconds_left = calibration_countdown // 30 + 1
    
    # Fix text overlapping by calculating text position based on available space
    text = f"Place hand in box: {seconds_left}s"
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
    
    # Position text above the rectangle with enough margin
    text_x = roi_x + (roi_width - text_size[0]) // 2
    text_y = roi_y - 15  # Increased margin 
    
    # Add a dark background for better text visibility
    cv2.rectangle(frame, (text_x - 5, text_y - text_size[1] - 5), (text_x + text_size[0] + 5, text_y + 5), (0, 0, 0), -1)
    
    cv2.putText(frame, text, (text_x, text_y), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    # Decrease countdown
    calibration_countdown -= 1
    
    # If countdown is done, calculate skin color range
    if calibration_countdown <= 0:
        if len(calibration_samples) > 0:
            # Concatenate all samples
            all_samples = np.vstack([sample.reshape(-1, 3) for sample in calibration_samples])
            
            # Calculate min and max values for each channel with some buffer
            h_min = max(0, np.percentile(all_samples[:, 0], 5) - 5)
            h_max = min(180, np.percentile(all_samples[:, 0], 95) + 5)
            s_min = max(0, np.percentile(all_samples[:, 1], 5) - 40)
            s_max = min(255, np.percentile(all_samples[:, 1], 95) + 40)
            v_min = max(0, np.percentile(all_samples[:, 2], 5) - 40)
            v_max = min(255, np.percentile(all_samples[:, 2], 95) + 40)
            
            # Update global skin color range
            hand_detection_module.update_skin_range(h_min, h_max, s_min, s_max, v_min, v_max)
            
            # Log results
            add_terminal_message(f"Calibration complete! HSV range updated.")
        else:
            add_terminal_message("Calibration failed! No samples collected.")
        
        # Exit calibration mode
        calibration_mode = False
        config.calibration_mode = False
    
    return frame

def start_manual_calibration():
    """Start the manual skin color calibration process"""
    global manual_calibration_mode, manual_min_h, manual_max_h, manual_min_s, manual_max_s, manual_min_v, manual_max_v
    
    # Make sure hand_detection module is imported
    _import_modules()
    
    # Initialize slider values from current skin color range
    manual_min_h = hand_detection_module.lower_skin[0]
    manual_max_h = hand_detection_module.upper_skin[0]
    manual_min_s = hand_detection_module.lower_skin[1]
    manual_max_s = hand_detection_module.upper_skin[1]
    manual_min_v = hand_detection_module.lower_skin[2]
    manual_max_v = hand_detection_module.upper_skin[2]
    
    manual_calibration_mode = True
    config.manual_calibration_mode = True
    add_terminal_message("Manual calibration started. Adjust sliders to set skin color range.")

def process_manual_calibration_frame(frame):
    """Process a frame during manual calibration mode"""
    global manual_min_h, manual_max_h, manual_min_s, manual_max_s, manual_min_v, manual_max_v
    
    # Update the skin color range for preview
    temp_lower_skin = np.array([manual_min_h, manual_min_s, manual_min_v], dtype=np.uint8)
    temp_upper_skin = np.array([manual_max_h, manual_max_s, manual_max_v], dtype=np.uint8)
    
    # Convert to HSV for skin detection
    hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
    
    # Create mask for skin color
    mask = cv2.inRange(hsv, temp_lower_skin, temp_upper_skin)
    
    # Apply mask to create a visual preview of the detection
    preview = frame.copy()
    preview_masked = cv2.bitwise_and(preview, preview, mask=mask)
    
    # Add a semi-transparent overlay of the mask on the original image
    alpha = 0.5
    preview = cv2.addWeighted(preview_masked, alpha, preview, 1-alpha, 0)
    
    # Add text to show current values
    calibration_text = f"H: {manual_min_h}-{manual_max_h}, S: {manual_min_s}-{manual_max_s}, V: {manual_min_v}-{manual_max_v}"
    
    # Calculate text position to avoid overlapping
    text_size = cv2.getTextSize(calibration_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
    text_x = (frame.shape[1] - text_size[0]) // 2
    text_y = 30
    
    # Draw dark background for better visibility
    cv2.rectangle(preview, (text_x - 5, text_y - text_size[1] - 5), (text_x + text_size[0] + 5, text_y + 5), (0, 0, 0), -1)
    
    # Add text with current HSV values
    cv2.putText(preview, calibration_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    return preview

def draw_manual_calibration_controls(screen, calibration_area):
    """Draw sliders for manual calibration of skin color range"""
    global slider_active, manual_min_h, manual_max_h, manual_min_s, manual_max_s, manual_min_v, manual_max_v
    
    # Draw calibration panel background
    pygame.draw.rect(screen, config.LIGHT_GRAY, calibration_area)
    pygame.draw.rect(screen, config.BLACK, calibration_area, 1)
    
    slider_width = calibration_area.width - 80
    slider_spacing = 35
    slider_left = calibration_area.left + 40
    
    # Title
    font = pygame.font.SysFont('Arial', 16, bold=True)
    title = font.render("Manual Skin Color Calibration", True, config.BLACK)
    screen.blit(title, (calibration_area.centerx - title.get_width()//2, calibration_area.top + 15))
    
    # Instructions
    instructions_font = pygame.font.SysFont('Arial', 14)
    instructions = [
        "Adjust the sliders to set the HSV range",
        "for skin color detection.",
        "",
        "H: Hue - color tone (0-180)",
        "S: Saturation - color intensity (0-255)",
        "V: Value - brightness (0-255)",
        "",
        "The preview shows what will be detected."
    ]
    
    # Draw instructions
    for i, line in enumerate(instructions):
        text = instructions_font.render(line, True, config.BLACK)
        screen.blit(text, (slider_left, calibration_area.top + 45 + i * 20))
    
    # Starting Y position for sliders after instructions
    y_pos = calibration_area.top + 210
    
    # Draw Hue sliders
    h_min_slider, h_min_handle, h_max_handle = draw_slider_pair(screen, "Hue (H)", slider_left, y_pos, slider_width, 180, manual_min_h, manual_max_h, "min_h", "max_h")
    
    # Draw Saturation sliders
    y_pos += slider_spacing
    s_min_slider, s_min_handle, s_max_handle = draw_slider_pair(screen, "Saturation (S)", slider_left, y_pos, slider_width, 255, manual_min_s, manual_max_s, "min_s", "max_s")
    
    # Draw Value sliders
    y_pos += slider_spacing
    v_min_slider, v_min_handle, v_max_handle = draw_slider_pair(screen, "Value (V)", slider_left, y_pos, slider_width, 255, manual_min_v, manual_max_v, "min_v", "max_v")
    
    # Draw Apply button
    apply_button_rect = pygame.Rect(calibration_area.centerx + 10, calibration_area.bottom - 50, 80, 30)
    pygame.draw.rect(screen, config.GREEN, apply_button_rect)
    pygame.draw.rect(screen, config.BLACK, apply_button_rect, 1)
    apply_text = font.render("Apply", True, config.WHITE)
    screen.blit(apply_text, (apply_button_rect.centerx - apply_text.get_width()//2, apply_button_rect.centery - apply_text.get_height()//2))
    
    # Draw Cancel button
    cancel_button_rect = pygame.Rect(calibration_area.centerx - 90, calibration_area.bottom - 50, 80, 30)
    pygame.draw.rect(screen, config.RED, cancel_button_rect)
    pygame.draw.rect(screen, config.BLACK, cancel_button_rect, 1)
    cancel_text = font.render("Cancel", True, config.WHITE)
    screen.blit(cancel_text, (cancel_button_rect.centerx - cancel_text.get_width()//2, cancel_button_rect.centery - cancel_text.get_height()//2))
    
    # Draw current values in a box
    current_values_rect = pygame.Rect(calibration_area.left + 10, calibration_area.bottom - 110, calibration_area.width - 20, 50)
    pygame.draw.rect(screen, config.WHITE, current_values_rect)
    pygame.draw.rect(screen, config.BLACK, current_values_rect, 1)
    
    values_text = f"Current HSV Range:"
    values_text2 = f"H: {manual_min_h}-{manual_max_h}, S: {manual_min_s}-{manual_max_s}, V: {manual_min_v}-{manual_max_v}"
    
    values_label = instructions_font.render(values_text, True, config.BLACK)
    values_display = instructions_font.render(values_text2, True, config.BLUE)
    
    screen.blit(values_label, (current_values_rect.centerx - values_label.get_width()//2, current_values_rect.top + 10))
    screen.blit(values_display, (current_values_rect.centerx - values_display.get_width()//2, current_values_rect.top + 30))
    
    return apply_button_rect, cancel_button_rect, h_min_handle, h_max_handle, s_min_handle, s_max_handle, v_min_handle, v_max_handle, h_min_slider, s_min_slider, v_min_slider

def draw_slider_pair(screen, label, x, y, width, max_value, min_val, max_val, min_id, max_id):
    """Helper function to draw a pair of min/max sliders with labels"""
    font = pygame.font.SysFont('Arial', 14)
    
    # Draw label
    label_text = font.render(label, True, config.BLACK)
    screen.blit(label_text, (x - 40, y))
    
    # Draw min slider
    min_slider_rect = pygame.Rect(x, y, width, 10)
    pygame.draw.rect(screen, config.LIGHT_GRAY, min_slider_rect)
    pygame.draw.rect(screen, config.BLACK, min_slider_rect, 1)
    
    # Draw min handle
    min_pos = x + (min_val / max_value) * width
    min_handle_rect = pygame.Rect(min_pos - 5, y - 5, 10, 20)
    pygame.draw.rect(screen, config.BLUE, min_handle_rect)
    pygame.draw.rect(screen, config.BLACK, min_handle_rect, 1)
    
    # Draw min value text
    min_text = font.render(str(min_val), True, config.BLACK)
    screen.blit(min_text, (min_pos - min_text.get_width()//2, y + 15))
    
    # Draw max slider (reusing the same track)
    max_pos = x + (max_val / max_value) * width
    max_handle_rect = pygame.Rect(max_pos - 5, y - 5, 10, 20)
    pygame.draw.rect(screen, config.RED, max_handle_rect)
    pygame.draw.rect(screen, config.BLACK, max_handle_rect, 1)
    
    # Draw max value text
    max_text = font.render(str(max_val), True, config.BLACK)
    screen.blit(max_text, (max_pos - max_text.get_width()//2, y + 15))
    
    return min_slider_rect, min_handle_rect, max_handle_rect

def apply_manual_calibration():
    """Apply the manual calibration and update the skin color range"""
    global manual_calibration_mode, manual_min_h, manual_max_h, manual_min_s, manual_max_s, manual_min_v, manual_max_v
    
    # Make sure hand_detection module is imported
    _import_modules()
    
    # Update the skin color range
    hand_detection_module.update_skin_range(manual_min_h, manual_max_h, manual_min_s, manual_max_s, manual_min_v, manual_max_v)
    
    # Exit manual calibration mode
    manual_calibration_mode = False
    config.manual_calibration_mode = False
    add_terminal_message("Manual calibration applied!")

def cancel_manual_calibration():
    """Cancel the manual calibration without applying changes"""
    global manual_calibration_mode
    
    manual_calibration_mode = False
    config.manual_calibration_mode = False
    add_terminal_message("Manual calibration canceled")

def update_slider_value(slider_id, mouse_pos, slider_rect, max_value):
    """Update slider value based on mouse position"""
    global manual_min_h, manual_max_h, manual_min_s, manual_max_s, manual_min_v, manual_max_v
    
    # Calculate position ratio
    pos_ratio = max(0, min(1, (mouse_pos[0] - slider_rect.left) / slider_rect.width))
    new_value = int(pos_ratio * max_value)
    
    # Update appropriate slider value
    if slider_id == "min_h":
        manual_min_h = min(new_value, manual_max_h - 1)
    elif slider_id == "max_h":
        manual_max_h = max(new_value, manual_min_h + 1)
    elif slider_id == "min_s":
        manual_min_s = min(new_value, manual_max_s - 1)
    elif slider_id == "max_s":
        manual_max_s = max(new_value, manual_min_s + 1)
    elif slider_id == "min_v":
        manual_min_v = min(new_value, manual_max_v - 1)
    elif slider_id == "max_v":
        manual_max_v = max(new_value, manual_min_v + 1)