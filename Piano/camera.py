#!/usr/bin/env python3
# camera.py - Handles camera initialization and operations

import cv2
import time
import numpy as np
import pygame
from threading import Thread
import config
from terminal import add_terminal_message

# Global camera objects
camera = None
camera_frame = None
camera_surface = None

# Import these modules only when needed to avoid circular imports
hand_detection_module = None
calibration_module = None

def _import_modules():
    """Import dependent modules when needed (to avoid circular imports)"""
    global hand_detection_module, calibration_module
    if hand_detection_module is None:
        import hand_detection
        hand_detection_module = hand_detection
    if calibration_module is None:
        import calibration
        calibration_module = calibration

def initialize_camera():
    """Initialize the camera device - This doesn't get called until Begin button is clicked"""
    global camera
    
    # Try specific camera indices in order of preference
    # iPhone is often detected at higher indices like 2 or above, so try those first
    camera_indices = [1, 2, 3, 0]  # Try 1, 2, 3 first (external cameras), then 0 (built-in)
    
    try:
        for camera_index in camera_indices:
            print(f"Attempting to open camera at index {camera_index}...")
            
            # Try to open camera at this index
            camera = cv2.VideoCapture(camera_index)
            
            if not camera.isOpened():
                print(f"Could not open camera at index {camera_index}")
                # Release and try next index
                try:
                    camera.release()
                except:
                    pass
                continue
            
            # Successfully opened - check if we can get a frame
            ret, test_frame = camera.read()
            if not ret or test_frame is None:
                print(f"WARNING: Camera at index {camera_index} opened but could not read frame")
                try:
                    camera.release()
                except:
                    pass
                continue
            
            # Successfully read a frame - use this camera
            print(f"Camera opened successfully at index {camera_index}!")
            print(f"Camera properties:")
            print(f" - Width: {camera.get(cv2.CAP_PROP_FRAME_WIDTH)}")
            print(f" - Height: {camera.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
            print(f" - FPS: {camera.get(cv2.CAP_PROP_FPS)}")
            print(f"Successfully read test frame: {test_frame.shape}")
            
            # If we find a camera that's not the built-in webcam (likely the iPhone), prefer it
            if camera_index != 0:
                add_terminal_message(f"External camera detected at index {camera_index}")
                return True
            
            # Otherwise use the built-in camera
            add_terminal_message(f"Using built-in camera (no external camera found)")
            return True
            
        # If we get here, no camera worked
        add_terminal_message("Error: Could not initialize any camera")
        return False
        
    except Exception as e:
        print(f"Camera initialization error: {str(e)}")
        add_terminal_message(f"Camera error: {str(e)}")
        return False

def camera_thread_function():
    """Thread function for capturing and processing camera frames"""
    global camera_active, camera_frame, camera_surface, camera
    
    # Import dependent modules
    _import_modules()
    
    frame_count = 0
    error_count = 0
    
    try:
        print("Camera thread started")
        add_terminal_message("Camera thread started")
        
        while config.camera_active:
            if camera is None:
                print("ERROR: Camera is None in thread!")
                add_terminal_message("Camera error: Device disconnected")
                break
                
            # Capture frame
            ret, frame = camera.read()
            
            if not ret or frame is None:
                error_count += 1
                print(f"Error capturing frame ({error_count} errors)")
                
                if error_count > 5:
                    print("Too many frame errors - sleeping")
                    time.sleep(1.0)
                else:
                    time.sleep(0.1)
                continue
            
            # Successfully got a frame - flip it horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            frame_count += 1
            
            if frame_count % 30 == 0:  # Log every 30 frames
                print(f"Processed {frame_count} frames")
            
            error_count = 0  # Reset error counter on success
            
            # Convert frame from BGR to RGB (for pygame display)
            try:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            except Exception as e:
                print(f"Error in color conversion: {e}")
                continue
            
            # Resize frame to fit display area
            try:
                frame = cv2.resize(frame, (config.CAMERA_DISPLAY_RECT.width, config.CAMERA_DISPLAY_RECT.height))
            except Exception as e:
                print(f"Error in resize: {e}")
                continue
            
            # Process frame based on current mode
            try:
                if config.calibration_mode:
                    # Auto calibration mode
                    frame = calibration_module.process_calibration_frame(frame)
                elif config.manual_calibration_mode:
                    # Manual calibration mode
                    frame = calibration_module.process_manual_calibration_frame(frame)
                else:
                    # Regular hand detection mode
                    frame, fingertips = hand_detection_module.detect_fingertips(frame)
            except Exception as e:
                print(f"Error in frame processing: {e}")
                # Continue with unprocessed frame
                pass
            
            # Store the frame for reference
            camera_frame = frame
            
            # Very important: Use the exact method from your original code
            # Create a pygame surface from the processed frame
            try:
                # Debug the frame shape
                print(f"Frame shape before processing: {frame.shape}")
                
                # This approach worked in your original code - use transpose instead of rot90
                # to avoid any shape issues
                frame_rgb = frame.copy()  # Ensure we have a fresh copy
                camera_surface = pygame.surfarray.make_surface(frame_rgb.transpose(1, 0, 2))
                
                # Debug successful surface creation
                if camera_surface:
                    print(f"Successfully created surface: {camera_surface.get_size()}")
                
            except Exception as e:
                print(f"Error creating pygame surface with transpose: {e}")
                
                # Try alternate methods if the first fails
                try:
                    print("Trying alternative surface creation method...")
                    # Try direct conversion
                    camera_surface = pygame.image.frombuffer(
                        frame.tobytes(), (frame.shape[1], frame.shape[0]), 'RGB')
                    print(f"Created surface using frombuffer: {camera_surface.get_size()}")
                except Exception as e2:
                    print(f"All surface creation methods failed: {e}, {e2}")
                    continue
            
            # Check if camera_surface was successfully created
            if camera_surface is None:
                print("Warning: Failed to create camera surface")
                
            time.sleep(0.03)  # ~30 FPS
    
    except Exception as e:
        print(f"Camera thread error: {str(e)}")
        add_terminal_message(f"Camera thread error: {str(e)}")
    finally:
        print("Camera thread ending")
        if camera is not None:
            camera.release()
            camera = None

# These variables help ensure the camera is initialized properly
camera_initialized = False
camera_starting = False

def start_camera_thread():
    """Start the camera capture thread - This gets called when Begin button is clicked"""
    global camera, camera_initialized, camera_starting
    
    # Prevent multiple simultaneous initialization attempts
    if camera_starting:
        add_terminal_message("Camera already starting...")
        return False
        
    # If camera is already running, stop it first
    if camera_initialized:
        stop_camera()
        return False
        
    camera_starting = True
    
    # Make sure camera is closed if already open
    if camera is not None:
        try:
            camera.release()
        except:
            pass
        camera = None
    
    # Initialize new camera
    if initialize_camera():
        config.camera_active = True
        config.recording = True
        camera_initialized = True
        add_terminal_message("Camera started...")
        
        # Start camera thread
        camera_thread = Thread(target=camera_thread_function)
        camera_thread.daemon = True
        camera_thread.start()
        camera_starting = False
        return True
    else:
        add_terminal_message("Failed to start camera!")
        camera_starting = False
        return False

def stop_camera():
    """Stop the camera and release resources"""
    global camera, camera_initialized
    
    config.camera_active = False
    config.recording = False
    camera_initialized = False
    add_terminal_message("Camera stopped")
    
    if camera is not None:
        camera.release()
        camera = None