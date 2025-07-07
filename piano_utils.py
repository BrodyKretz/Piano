# piano_utils.py
# Utility functions for the Piano with Camera program

import os
import pygame
import cv2
import numpy as np
import urllib.request
from threading import Thread
import time

# This file contains all the utility functions for the Piano with Camera program
# It is imported by piano_app.py

def download_hand_cascade():
    """Download the hand detection cascade classifier file if not available locally"""
    url = "https://raw.githubusercontent.com/Balaje/OpenCV/master/haarcascades/hand.xml"
    local_file = "hand.xml"
    try:
        # Check if file already exists
        try:
            with open(local_file, 'r') as f:
                pass
            print(f"Using existing {local_file}")
            return local_file
        except FileNotFoundError:
            # Download the file
            urllib.request.urlretrieve(url, local_file)
            print(f"Downloaded {local_file}")
            return local_file
    except Exception as e:
        print(f"Error downloading hand cascade: {e}")
        return None

def initialize_hand_detector():
    """Initialize the hand detector using OpenCV's cascade classifier"""
    cascade_file = download_hand_cascade()
    if cascade_file:
        hand_cascade = cv2.CascadeClassifier(cascade_file)
        return hand_cascade
    return None

def start_calibration():
    """Start the skin color calibration process"""
    global calibration_mode, calibration_rect, calibration_countdown, calibration_samples
    
    # Reset calibration variables
    calibration_mode = True
    calibration_samples = []
    
    # Create a rectangle in the center of the camera view for hand placement
    rect_width, rect_height = 200, 200
    rect_x = CAMERA_DISPLAY_RECT.left + (CAMERA_DISPLAY_RECT.width - rect_width) // 2
    rect_y = CAMERA_DISPLAY_RECT.top + (CAMERA_DISPLAY_RECT.height - rect_height) // 2
    calibration_rect = pygame.Rect(rect_x, rect_y, rect_width, rect_height)
    
    # Set countdown for 5 seconds
    calibration_countdown = 5 * 30  # 5 seconds at 30 FPS
    
    terminal_messages.append("Calibration started. Place your hand in the box.")
    if len(terminal_messages) > max_messages:
        terminal_messages.pop(0)

def process_calibration_frame(frame):
    """Process a frame during calibration mode"""
    global calibration_countdown, calibration_mode, calibration_samples, lower_skin, upper_skin
    
    # Extract the region of interest (where hand should be placed)
    roi_x = calibration_rect.x - CAMERA_DISPLAY_RECT.left
    roi_y = calibration_rect.y - CAMERA_DISPLAY_RECT.top
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
    cv2.putText(frame, f"Place hand in box: {seconds_left}s", (roi_x, roi_y - 10), 
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
            lower_skin = np.array([h_min, s_min, v_min], dtype=np.uint8)
            upper_skin = np.array([h_max, s_max, v_max], dtype=np.uint8)
            
            # Log results
            terminal_messages.append(f"Calibration complete! HSV range: {lower_skin} to {upper_skin}")
            if len(terminal_messages) > max_messages:
                terminal_messages.pop(0)
        else:
            terminal_messages.append("Calibration failed! No samples collected.")
            if len(terminal_messages) > max_messages:
                terminal_messages.pop(0)
        
        # Exit calibration mode
        calibration_mode = False
    
    return frame

def detect_fingertips(frame):
    """Detect fingertips in the given frame using the calibrated skin color range"""
    global lower_skin, upper_skin, hand_cascade
    
    # Convert to grayscale for Haar cascade
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Detect hands using Haar cascade
    hands = hand_cascade.detectMultiScale(gray, 1.3, 5)
    
    fingertips = []
    
    for (x, y, w, h) in hands:
        # Draw rectangle around detected hand
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Extract hand region for contour analysis
        hand_region = frame[y:y+h, x:x+w]
        
        # Convert to HSV for better skin detection
        hsv = cv2.cvtColor(hand_region, cv2.COLOR_RGB2HSV)
        
        # Create mask for skin color using calibrated values
        mask = cv2.inRange(hsv, lower_skin, upper_skin)
        
        # Apply morphological operations to clean up the mask
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=2)
        mask = cv2.erode(mask, kernel, iterations=2)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Find largest contour (assume it's the hand)
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Create convex hull around hand
            hull = cv2.convexHull(largest_contour)
            
            # Find convexity defects
            hull_indices = cv2.convexHull(largest_contour, returnPoints=False)
            
            try:
                defects = cv2.convexityDefects(largest_contour, hull_indices)
                
                if defects is not None:
                    # Find fingertips using convexity defects
                    for i in range(defects.shape[0]):
                        s, e, f, d = defects[i, 0]
                        start = tuple(largest_contour[s][0])
                        end = tuple(largest_contour[e][0])
                        far = tuple(largest_contour[f][0])
                        
                        # Calculate distance between points
                        a = np.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
                        b = np.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
                        c = np.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
                        
                        # Calculate angle
                        angle = np.arccos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 180 / np.pi
                        
                        # Fingertips typically have angles less than 90 degrees
                        if angle <= 90:
                            # Add fingertip to the list (relative to full frame)
                            fingertips.append((x + end[0], y + end[1]))
                            
                            # Draw a green square around the fingertip
                            square_size = 10
                            pt1 = (x + end[0] - square_size // 2, y + end[1] - square_size // 2)
                            pt2 = (x + end[0] + square_size // 2, y + end[1] + square_size // 2)
                            cv2.rectangle(frame, pt1, pt2, (0, 255, 0), 2)
            except:
                # Sometimes convexityDefects can fail if the contour is too simple
                pass
            
            # Also mark the extreme points as potential fingertips
            # (helps catch extended single fingers)
            extLeft = tuple(largest_contour[largest_contour[:, :, 0].argmin()][0])
            extRight = tuple(largest_contour[largest_contour[:, :, 0].argmax()][0])
            extTop = tuple(largest_contour[largest_contour[:, :, 1].argmin()][0])
            
            # Add extreme top point as potential fingertip
            fingertips.append((x + extTop[0], y + extTop[1]))
            
            # Draw green square around it
            square_size = 10
            pt1 = (x + extTop[0] - square_size // 2, y + extTop[1] - square_size // 2)
            pt2 = (x + extTop[0] + square_size // 2, y + extTop[1] + square_size // 2)
            cv2.rectangle(frame, pt1, pt2, (0, 255, 0), 2)
    
    return frame, fingertips

def camera_thread_function():
    """Thread function for camera processing"""
    global camera_active, camera_frame, camera_surface, camera, hand_cascade, calibration_mode
    
    # Initialize hand detector if not already done
    if hand_cascade is None:
        hand_cascade = initialize_hand_detector()
    
    try:
        while camera_active:
            ret, frame = camera.read()
            if not ret:
                break
            
            # Convert frame from BGR to RGB (for pygame display)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Resize frame to fit our display area
            frame = cv2.resize(frame, (CAMERA_DISPLAY_RECT.width, CAMERA_DISPLAY_RECT.height))
            
            # Process frame based on current mode
            if calibration_mode:
                # We're in calibration mode
                frame = process_calibration_frame(frame)
            elif hand_cascade is not None:
                # Regular hand detection mode
                frame, fingertips = detect_fingertips(frame)
            
            # Create a pygame surface
            camera_frame = frame
            camera_surface = pygame.surfarray.make_surface(np.rot90(frame))
            
            time.sleep(0.03)  # ~30 FPS
    
    except Exception as e:
        print(f"Camera thread error: {str(e)}")
    finally:
        if camera is not None:
            camera.release()

def toggle_keyboard_overlay():
    """Toggle the keyboard overlay on/off"""
    global keyboard_overlay_active, keyboard_overlay_width, keyboard_overlay_left, keyboard_overlay_right, keyboard_overlay_slider_value
    
    if keyboard_overlay_active:
        terminal_messages.append("Keyboard overlay removed")
    else:
        # Calculate width based on 11 white keys
        keyboard_overlay_width = 11 * WHITE_KEY_WIDTH
        
        # Position overlay in the middle of the piano by default
        keyboard_overlay_left = piano_left + (piano_width - keyboard_overlay_width) // 2
        keyboard_overlay_right = keyboard_overlay_left + keyboard_overlay_width
        
        # Calculate initial slider value based on position
        available_width = piano_width - keyboard_overlay_width
        if available_width > 0:
            keyboard_overlay_slider_value = (keyboard_overlay_left - piano_left) / available_width
        else:
            keyboard_overlay_slider_value = 0.5
        
        terminal_messages.append("Keyboard overlay added - Use A-S-D-F-G-H-J-K-L to play")
    
    keyboard_overlay_active = not keyboard_overlay_active
    
    if len(terminal_messages) > max_messages:
        terminal_messages.pop(0)

def get_piano_key_at_position(x_position):
    """Get the index of a white piano key at the given x position"""
    for i, key in enumerate(white_keys):
        if key.left <= x_position < key.right:
            return i
    return None

def get_white_key_indices_in_range(left_x, width):
    """Get the indices of white keys within a given range"""
    key_indices = []
    for i, key in enumerate(white_keys):
        if left_x <= key.left < left_x + width or left_x < key.right <= left_x + width:
            key_indices.append(i)
        elif key.left <= left_x and key.right >= left_x + width:
            # The key completely contains the range
            key_indices.append(i)
    return key_indices

def update_keyboard_overlay_from_slider():
    """Update the keyboard overlay position based on slider value"""
    global keyboard_overlay_left, keyboard_overlay_right
    
    # Calculate the available piano width for positioning
    available_width = piano_width - keyboard_overlay_width
    
    # Calculate position based on slider value
    position = piano_left + available_width * keyboard_overlay_slider_value
    
    # Set overlay position
    keyboard_overlay_left = position
    keyboard_overlay_right = position + keyboard_overlay_width

def update_piano_overlay_from_slider():
    """Update the piano overlay position based on slider value"""
    global piano_overlay_left, piano_overlay_right
    
    # Get the width of the camera overlay
    camera_overlay_width = line2_x - line1_x
    
    # Calculate the available piano width to position the overlay
    available_width = piano_width - camera_overlay_width
    
    # Calculate position based on slider value
    position = piano_left + available_width * piano_overlay_slider_value
    
    # Set overlay position
    piano_overlay_left = position
    piano_overlay_right = position + camera_overlay_width

def initialize_camera():
    """Initialize the camera"""
    global camera
    try:
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            terminal_messages.append("Error: Could not open camera")
            if len(terminal_messages) > max_messages:
                terminal_messages.pop(0)
            return False
        return True
    except Exception as e:
        terminal_messages.append(f"Camera error: {str(e)}")
        if len(terminal_messages) > max_messages:
            terminal_messages.pop(0)
        return False

def start_recording():
    """Start camera recording"""
    global camera_active, recording
    
    if initialize_camera():
        camera_active = True
        recording = True
        terminal_messages.append("Recording started...")
        if len(terminal_messages) > max_messages:
            terminal_messages.pop(0)
        
        # Start camera thread
        camera_thread = Thread(target=camera_thread_function)
        camera_thread.daemon = True
        camera_thread.start()
        return True
    return False

def stop_recording():
    """Stop camera recording"""
    global camera_active, recording, camera
    
    camera_active = False
    recording = False
    terminal_messages.append("Recording stopped")
    if len(terminal_messages) > max_messages:
        terminal_messages.pop(0)
    
    if camera is not None:
        camera.release()
        camera = None

def toggle_overlay():
    """Toggle the camera overlay on/off"""
    global overlay_active, piano_overlay_active, saved_line_positions, piano_overlay_left, piano_overlay_right
    
    if overlay_active:
        # Save current line positions before removing overlay
        saved_line_positions = {
            'line1_x': line1_x,
            'line2_x': line2_x,
            'line_y_top': line_y_top,
            'line_y_bottom': line_y_bottom
        }
        terminal_messages.append("Overlay removed and positions saved")
    else:
        terminal_messages.append("Overlay added - lines can be moved")
        # Update handle positions
        update_handle_positions()
        
        # Initialize piano overlay position based on camera overlay
        calculate_piano_overlay_position()
    
    overlay_active = not overlay_active
    piano_overlay_active = overlay_active  # Sync piano overlay with camera overlay
    
    if len(terminal_messages) > max_messages:
        terminal_messages.pop(0)

def update_handle_positions():
    """Update the positions of the overlay handles"""
    global line1_top_handle, line1_bottom_handle, line2_top_handle, line2_bottom_handle, middle_top_handle, middle_bottom_handle
    
    # Update handle positions
    line1_top_handle = pygame.Rect(line1_x - handle_size//2, line_y_top - handle_size//2, handle_size, handle_size)
    line1_bottom_handle = pygame.Rect(line1_x - handle_size//2, line_y_bottom - handle_size//2, handle_size, handle_size)
    line2_top_handle = pygame.Rect(line2_x - handle_size//2, line_y_top - handle_size//2, handle_size, handle_size)
    line2_bottom_handle = pygame.Rect(line2_x - handle_size//2, line_y_bottom - handle_size//2, handle_size, handle_size)
    middle_top_handle = pygame.Rect((line1_x + line2_x)//2 - handle_size//2, line_y_top - handle_size//2, handle_size, handle_size)
    middle_bottom_handle = pygame.Rect((line1_x + line2_x)//2 - handle_size//2, line_y_bottom - handle_size//2, handle_size, handle_size)

def calculate_piano_overlay_position():
    """Calculate the position of the piano overlay based on camera overlay"""
    global piano_overlay_left, piano_overlay_right
    
    # Get the width of the camera overlay
    camera_overlay_width = line2_x - line1_x
    
    # Calculate position based on slider value
    available_width = piano_width - camera_overlay_width
    position = piano_left + available_width * piano_overlay_slider_value
    
    # Set overlay position
    piano_overlay_left = position
    piano_overlay_right = position + camera_overlay_width

def play_note(note_idx, is_black=False):
    """Play a piano note and show message in terminal"""
    try:
        if is_black:
            note_name = black_notes[note_idx]
        else:
            note_name = white_notes[note_idx]
        
        # Get the sound object
        sound_idx = 1000 + note_idx if is_black else note_idx
        sound = sounds[sound_idx]
        
        # Stop any previous playback of this note
        sound.stop()
        
        # Set volume explicitly and play
        sound.set_volume(1.0)  # Maximum volume
        sound.play()
        
        # Print debug info to terminal and console
        debug_msg = f"Playing {note_name} (sound index {sound_idx})"
        print(debug_msg)
        
        # Add message to terminal
        terminal_messages.append(debug_msg)
        if len(terminal_messages) > max_messages:
            terminal_messages.pop(0)
    except Exception as e:
        error_msg = f"Error playing note: {e}"
        print(error_msg)
        terminal_messages.append(error_msg)
        if len(terminal_messages) > max_messages:
            terminal_messages.pop(0)

def initialize_piano_sounds():
    """Load piano sound files from the piano-mp3 directory"""
    global sounds
    
    try:
        # Path to piano sounds directory
        sound_dir = "piano-mp3"
        
        # Load sounds for white keys
        for i, note_name in enumerate(white_notes):
            try:
                note_file = os.path.join(sound_dir, f"{note_name}.mp3")
                if os.path.exists(note_file):
                    sounds[i] = pygame.mixer.Sound(note_file)
                    sounds[i].set_volume(0.8)  # Set volume to 80%
                    print(f"Loaded {note_file}")
                else:
                    print(f"Warning: Sound file not found: {note_file}")
                    # Fallback to empty buffer if file doesn't exist
                    sounds[i] = pygame.mixer.Sound(buffer=bytearray(4000))
            except Exception as e:
                print(f"Error loading sound for {note_name}: {e}")
                sounds[i] = pygame.mixer.Sound(buffer=bytearray(4000))
        
        # Load sounds for black keys
        for i, note_name in enumerate(black_notes):
            try:
                note_file = os.path.join(sound_dir, f"{note_name}.mp3")
                if os.path.exists(note_file):
                    sounds[1000 + i] = pygame.mixer.Sound(note_file)
                    sounds[1000 + i].set_volume(0.8)  # Set volume to 80%
                    print(f"Loaded {note_file}")
                else:
                    print(f"Warning: Sound file not found: {note_file}")
                    # Fallback to empty buffer if file doesn't exist
                    sounds[1000 + i] = pygame.mixer.Sound(buffer=bytearray(4000))
            except Exception as e:
                print(f"Error loading sound for {note_name}: {e}")
                sounds[1000 + i] = pygame.mixer.Sound(buffer=bytearray(4000))
        
        print(f"Loaded {len(sounds)} piano sounds")
        return True
    except Exception as e:
        print(f"Error initializing piano sounds: {e}")
        return False