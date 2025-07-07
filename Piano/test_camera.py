#!/usr/bin/env python3
# Standalone script to test camera functionality

import cv2
import numpy as np
import time
import sys

def test_camera_with_display():
    """Test camera by displaying frames in a window"""
    print("Testing camera access and display...")
    
    # Try multiple camera indices
    for camera_index in range(3):
        print(f"Trying camera at index {camera_index}...")
        
        # Try to open the camera
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            print(f"  - Camera at index {camera_index} not available")
            continue
        
        print(f"  - Successfully opened camera at index {camera_index}")
        print(f"  - Camera properties:")
        print(f"    - Width: {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}")
        print(f"    - Height: {cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
        print(f"    - FPS: {cap.get(cv2.CAP_PROP_FPS)}")
        
        # Create a window
        window_name = f"Camera Test (Index {camera_index})"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        
        print("Displaying camera feed for 5 seconds...")
        print("Press 'q' to quit early, or any key to try next camera")
        
        start_time = time.time()
        frame_count = 0
        
        # Read and display frames for 5 seconds
        while time.time() - start_time < 5:
            ret, frame = cap.read()
            
            if not ret or frame is None:
                print("  - Failed to read frame from camera")
                break
            
            frame_count += 1
            
            # Display the frame
            cv2.imshow(window_name, frame)
            
            # Check for key press (wait 30ms)
            key = cv2.waitKey(30)
            if key == ord('q'):
                print("  - Test terminated by user")
                cap.release()
                cv2.destroyAllWindows()
                return
        
        print(f"  - Captured {frame_count} frames in ~5 seconds")
        
        # Release resources
        cap.release()
        cv2.destroyWindow(window_name)
        
        # Ask if user wants to continue testing
        if camera_index < 2:  # Not the last camera
            print("Continue testing with next camera? (y/n)")
            response = input().lower()
            if response != 'y':
                break
    
    print("Camera testing complete")

if __name__ == "__main__":
    try:
        test_camera_with_display()
    except Exception as e:
        print(f"ERROR during camera test: {e}")
    
    # Ensure OpenCV windows are closed
    cv2.destroyAllWindows()