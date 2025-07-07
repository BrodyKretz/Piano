#!/usr/bin/env python3
# hand_detection.py - Handles hand detection and fingertip tracking

import cv2
import numpy as np
import urllib.request
from terminal import add_terminal_message

# Global variables for hand detection
hand_cascade = None
lower_skin = np.array([0, 20, 70], dtype=np.uint8)
upper_skin = np.array([20, 255, 255], dtype=np.uint8)

def download_hand_cascade():
    """Download the hand cascade XML if needed"""
    url = "https://raw.githubusercontent.com/Balaje/OpenCV/master/haarcascades/hand.xml"
    local_file = "hand.xml"
    try:
        # Check if file already exists
        try:
            with open(local_file, 'r') as f:
                pass
            add_terminal_message(f"Using existing {local_file}")
            return local_file
        except FileNotFoundError:
            # Download the file
            add_terminal_message(f"Downloading hand cascade XML...")
            urllib.request.urlretrieve(url, local_file)
            add_terminal_message(f"Downloaded {local_file}")
            return local_file
    except Exception as e:
        add_terminal_message(f"Error downloading hand cascade: {e}")
        return None

def initialize_hand_detector():
    """Initialize the hand detector with cascade classifier"""
    global hand_cascade
    
    cascade_file = download_hand_cascade()
    if cascade_file:
        hand_cascade = cv2.CascadeClassifier(cascade_file)
        add_terminal_message("Hand detector initialized")
        return hand_cascade
    return None

def detect_fingertips(frame):
    """Detect fingertips in the camera frame"""
    global hand_cascade, lower_skin, upper_skin
    
    # If hand detector not initialized, try to initialize
    if hand_cascade is None:
        hand_cascade = initialize_hand_detector()
        if hand_cascade is None:
            return frame, []
    
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

def update_skin_range(min_h, max_h, min_s, max_s, min_v, max_v):
    """Update the skin color range for detection"""
    global lower_skin, upper_skin
    
    lower_skin = np.array([min_h, min_s, min_v], dtype=np.uint8)
    upper_skin = np.array([max_h, max_s, max_v], dtype=np.uint8)
    
    add_terminal_message(f"Skin range updated: H:{min_h}-{max_h}, S:{min_s}-{max_s}, V:{min_v}-{max_v}")