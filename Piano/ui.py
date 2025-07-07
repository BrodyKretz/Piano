#!/usr/bin/env python3
# ui.py - Handles user interface elements and event handling

import pygame
import sys
import config
from terminal import add_terminal_message, get_terminal
from camera import camera_surface, start_camera_thread, stop_camera

# Import these modules only when needed to avoid circular imports
piano_module = None 
overlay_module = None
calibration_module = None

# Keyboard overlay settings
keyboard_bindings = ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l']
active_keyboard_keys = [False] * len(keyboard_bindings)

# Mouse tracking
dragging_slider = False
dragging_keyboard_slider = False
dragging_keyboard_overlay = False
drag_start_pos = None

def _import_modules():
    """Import dependent modules only when needed (to avoid circular imports)"""
    global piano_module, overlay_module, calibration_module
    
    if piano_module is None:
        import piano
        piano_module = piano
    
    if overlay_module is None:
        import overlay
        overlay_module = overlay
        
    if calibration_module is None:
        import calibration
        calibration_module = calibration

def initialize_ui():
    """Initialize the UI components"""
    _import_modules()

def draw_ui(screen):
    """Draw all UI components"""
    # Make sure dependent modules are imported
    _import_modules()
    
    # Draw button area background
    pygame.draw.rect(screen, config.LIGHT_GRAY, pygame.Rect(0, 0, config.WIDTH, config.BUTTON_AREA_HEIGHT))
    
    # Draw buttons
    for button in config.buttons:
        if button["active"]:
            pygame.draw.rect(screen, button["active_color"], button["rect"])
        else:
            pygame.draw.rect(screen, button["color"], button["rect"])
        pygame.draw.rect(screen, config.BLACK, button["rect"], 2)  # Border
        
        # Draw button text
        font = pygame.font.SysFont('Arial', 16)
        text = font.render(button["label"], True, config.WHITE)
        text_rect = text.get_rect(center=button["rect"].center)
        screen.blit(text, text_rect)
    
    # Draw camera area background
    pygame.draw.rect(screen, config.LIGHT_GRAY, 
                    pygame.Rect(0, config.BUTTON_AREA_HEIGHT, 
                               config.WIDTH, config.CAMERA_DISPLAY_RECT.height + 40))
    
    # Draw camera frame
    pygame.draw.rect(screen, config.BLACK, config.CAMERA_DISPLAY_RECT, 2)
    
    # Display camera feed if active
    if config.recording and camera_surface is not None:
        try:
            # Check if camera_surface is valid
            if camera_surface.get_width() > 0 and camera_surface.get_height() > 0:
                # Scale and display the camera feed
                scaled_surface = pygame.transform.scale(camera_surface, 
                                               (config.CAMERA_DISPLAY_RECT.width, config.CAMERA_DISPLAY_RECT.height))
                screen.blit(scaled_surface, config.CAMERA_DISPLAY_RECT)
                
                # Draw overlay if active
                if overlay_module and overlay_module.is_active():
                    overlay_module.draw(screen)
            else:
                # Surface exists but has invalid dimensions
                font = pygame.font.SysFont('Arial', 20)
                text = font.render("Camera initializing...", True, config.BLACK)
                text_rect = text.get_rect(center=config.CAMERA_DISPLAY_RECT.center)
                screen.blit(text, text_rect)
                
        except Exception as e:
            print(f"Error displaying camera: {e}")
            # Draw error text
            font = pygame.font.SysFont('Arial', 20)
            text = font.render(f"Display Error: {str(e)[:30]}", True, config.RED)
            screen.blit(text, (config.CAMERA_DISPLAY_RECT.centerx - text.get_width()//2, 
                              config.CAMERA_DISPLAY_RECT.centery))
    else:
        # Draw placeholder text when camera is not active
        font = pygame.font.SysFont('Arial', 20)
        if not config.recording:
            text_str = "Click 'Begin' to start recording"
        else:
            text_str = "Camera initializing..."
        
        text = font.render(text_str, True, config.BLACK)
        text_rect = text.get_rect(center=config.CAMERA_DISPLAY_RECT.center)
        screen.blit(text, text_rect)
        
        # Draw calibration controls if needed
        if config.calibration_mode:
            # Draw status panel on the side
            status_area = pygame.Rect(config.CALIBRATION_AREA_LEFT, config.CALIBRATION_AREA_TOP, 
                                     config.CALIBRATION_AREA_WIDTH, config.CALIBRATION_AREA_HEIGHT)
            pygame.draw.rect(screen, config.LIGHT_GRAY, status_area)
            pygame.draw.rect(screen, config.BLACK, status_area, 1)
            
            # Title
            font = pygame.font.SysFont('Arial', 16, bold=True)
            title = font.render("Automatic Calibration", True, config.BLACK)
            screen.blit(title, (status_area.centerx - title.get_width()//2, status_area.top + 15))
            
            # Status and instructions
            status_font = pygame.font.SysFont('Arial', 14)
            instructions = [
                "Place your hand in the green box",
                "on the camera view.",
                "",
                "Hold still until the countdown",
                "completes.",
                "",
                "The system will automatically",
                "detect your skin color."
            ]
            
            for i, line in enumerate(instructions):
                text = status_font.render(line, True, config.BLACK)
                screen.blit(text, (status_area.left + 20, status_area.top + 50 + i * 20))
        
        # Draw manual calibration controls if needed
        elif config.manual_calibration_mode:
            calibration_area = pygame.Rect(config.CALIBRATION_AREA_LEFT, config.CALIBRATION_AREA_TOP, 
                                         config.CALIBRATION_AREA_WIDTH, config.CALIBRATION_AREA_HEIGHT)
            apply_button, cancel_button, h_min_handle, h_max_handle, s_min_handle, \
            s_max_handle, v_min_handle, v_max_handle, h_slider, s_slider, v_slider = \
                calibration_module.draw_manual_calibration_controls(screen, calibration_area)
            
            # Handle slider dragging
            if calibration_module.slider_active and pygame.mouse.get_pressed()[0]:
                mouse_pos = pygame.mouse.get_pos()
                
                if calibration_module.slider_active == "min_h":
                    calibration_module.update_slider_value("min_h", mouse_pos, h_slider, 180)
                elif calibration_module.slider_active == "max_h":
                    calibration_module.update_slider_value("max_h", mouse_pos, h_slider, 180)
                elif calibration_module.slider_active == "min_s":
                    calibration_module.update_slider_value("min_s", mouse_pos, s_slider, 255)
                elif calibration_module.slider_active == "max_s":
                    calibration_module.update_slider_value("max_s", mouse_pos, s_slider, 255)
                elif calibration_module.slider_active == "min_v":
                    calibration_module.update_slider_value("min_v", mouse_pos, v_slider, 255)
                elif calibration_module.slider_active == "max_v":
                    calibration_module.update_slider_value("max_v", mouse_pos, v_slider, 255)
            
            # Check for button clicks
            mouse_pos = pygame.mouse.get_pos()
            if pygame.mouse.get_pressed()[0]:
                if apply_button.collidepoint(mouse_pos):
                    calibration_module.apply_manual_calibration()
                elif cancel_button.collidepoint(mouse_pos):
                    calibration_module.cancel_manual_calibration()
        
        # Draw status panel in normal mode
        elif not config.calibration_mode and not config.manual_calibration_mode:
            # Draw status panel on the right side
            status_area = pygame.Rect(config.CALIBRATION_AREA_LEFT, config.CALIBRATION_AREA_TOP, 
                                     config.CALIBRATION_AREA_WIDTH, config.CALIBRATION_AREA_HEIGHT)
            pygame.draw.rect(screen, config.LIGHT_GRAY, status_area)
            pygame.draw.rect(screen, config.BLACK, status_area, 1)
            
            # Title
            font = pygame.font.SysFont('Arial', 16, bold=True)
            title = font.render("Hand Detection Status", True, config.BLACK)
            screen.blit(title, (status_area.centerx - title.get_width()//2, status_area.top + 15))
            
            # Display overlay status if active
            if overlay_module.is_active():
                overlay_module.draw_status(screen, status_area)
            else:
                # Tips and instructions
                status_font = pygame.font.SysFont('Arial', 14)
                instructions = [
                    "Tips for better detection:",
                    "- Make sure your hand is well lit",
                    "- Avoid complex backgrounds",
                    "- Use calibration if detection",
                    "  is not working well",
                    "",
                    "Use 'Auto Calibrate' for automatic",
                    "skin color detection.",
                    "",
                    "Use 'Manual Calibrate' for fine",
                    "control over detection settings."
                ]
                
                for i, line in enumerate(instructions):
                    text = status_font.render(line, True, config.BLACK)
                    screen.blit(text, (status_area.left + 20, status_area.top + 50 + i * 20))
    
    # Draw piano
    piano_module.draw_piano(screen)
    
    # Draw terminal
    terminal = get_terminal()
    terminal.draw(screen)

def handle_events(screen):
    """Handle pygame events and return whether the application should continue running"""
    global drag_start_pos
    
    _import_modules()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # Clean up and quit
            if config.recording:
                stop_camera()
            return False
        
        elif event.type == pygame.KEYDOWN:
            # Arrow keys to scroll piano
            if event.key == pygame.K_LEFT:
                piano_module.update_piano_scroll(-50)  # Scroll left
            elif event.key == pygame.K_RIGHT:
                piano_module.update_piano_scroll(50)   # Scroll right
            
            # Keyboard overlay key handling
            elif config.keyboard_overlay_active:
                try:
                    key_char = chr(event.key).lower()
                    piano_module.handle_keyboard_input(key_char)
                except:
                    pass  # Handle non-character keys
        
        # Handle key up events for keyboard overlay
        elif event.type == pygame.KEYUP:
            if config.keyboard_overlay_active:
                try:
                    key_char = chr(event.key).lower()
                    piano_module.release_keyboard_key(key_char)
                except:
                    pass
        
        # Mouse button down
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_pos = pygame.mouse.get_pos()
                
                # Check if any button was clicked
                button_clicked = False
                for button in config.buttons:
                    if button["rect"].collidepoint(mouse_pos):
                        button_clicked = True
                        button["active"] = True
                        if button["label"] == "Begin":
                            if not config.recording:
                                config.recording = start_camera_thread()
                            else:
                                stop_camera()
                                config.recording = False
                        elif button["label"] == "Add/Remove Overlay":
                            overlay_module.toggle()
                        elif button["label"] == "Keyboard Mode":
                            config.keyboard_overlay_active = not config.keyboard_overlay_active
                            if config.keyboard_overlay_active:
                                add_terminal_message("Keyboard overlay activated")
                            else:
                                add_terminal_message("Keyboard overlay deactivated")
                        elif button["label"] == "Auto Calibrate":
                            if config.recording:  # Only allow calibration if camera is running
                                calibration_module.start_calibration()
                            else:
                                add_terminal_message("Please start camera first!")
                        elif button["label"] == "Manual Calibrate":
                            if config.recording:  # Only allow calibration if camera is running
                                calibration_module.start_manual_calibration()
                            else:
                                add_terminal_message("Please start camera first!")
                        elif button["label"] == "Quit Program":
                            add_terminal_message("Quitting program...")
                            # Show message briefly before quitting
                            pygame.display.flip()
                            pygame.time.delay(500)
                            # Stop camera if active
                            if config.recording:
                                stop_camera()
                                config.recording = False
                            return False
                        break
                
                if button_clicked:
                    continue
                
                # Check if overlay is being manipulated
                if overlay_module.is_active() and overlay_module.handle_mouse_down(mouse_pos):
                    continue
                
                # Check for manual calibration sliders
                if config.manual_calibration_mode:
                    # The slider logic is handled in draw_ui now
                    drag_start_pos = mouse_pos
                    continue
                
                # Check piano keys
                if piano_module.check_piano_click(mouse_pos):
                    continue
                
                # Check if terminal was clicked for scrolling
                terminal = get_terminal()
                if terminal.rect.collidepoint(mouse_pos):
                    continue
            
            # Handle mouse wheel for scrolling
            elif event.button == 4:  # Scroll up
                # Check if mouse is over terminal for terminal scrolling
                mouse_pos = pygame.mouse.get_pos()
                terminal = get_terminal()
                if terminal.rect.collidepoint(mouse_pos):
                    terminal.scroll_up()
                else:
                    piano_module.update_piano_scroll(-30)  # Scroll piano left
            
            elif event.button == 5:  # Scroll down
                # Check if mouse is over terminal for terminal scrolling
                mouse_pos = pygame.mouse.get_pos()
                terminal = get_terminal()
                if terminal.rect.collidepoint(mouse_pos):
                    terminal.scroll_down()
                else:
                    piano_module.update_piano_scroll(30)   # Scroll piano right
        
        # Mouse motion
        elif event.type == pygame.MOUSEMOTION:
            if overlay_module.is_active():
                overlay_module.handle_mouse_motion(pygame.mouse.get_pos())
        
        # Mouse button up
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                # Reset button states
                for button in config.buttons:
                    button["active"] = False
                
                # Reset active piano keys
                piano_module.reset_active_keys()
                
                # Reset overlay dragging
                if overlay_module.is_active():
                    overlay_module.handle_mouse_up()
                
                # Reset slider dragging
                if calibration_module is not None:
                    calibration_module.slider_active = None
                drag_start_pos = None
    
    return True

def toggle_keyboard_overlay():
    """Toggle the keyboard overlay on/off"""
    config.keyboard_overlay_active = not config.keyboard_overlay_active
    
    if config.keyboard_overlay_active:
        add_terminal_message("Keyboard overlay activated")
    else:
        add_terminal_message("Keyboard overlay deactivated")