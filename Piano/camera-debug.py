#!/usr/bin/env python3
# Simple script to test if the camera is accessible

import cv2
import time

def test_camera():
    print("Testing camera access...")
    
    # Try to open the camera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("ERROR: Could not open camera!")
        return False
    
    print("Camera opened successfully!")
    
    # Try to read a frame
    ret, frame = cap.read()
    if not ret:
        print("ERROR: Could not read frame from camera!")
        cap.release()
        return False
    
    print("Successfully read a frame from camera!")
    print(f"Frame dimensions: {frame.shape}")
    
    # Release the camera
    cap.release()
    print("Camera released")
    
    return True

if __name__ == "__main__":
    test_camera()