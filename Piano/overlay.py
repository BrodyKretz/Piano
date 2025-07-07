#!/usr/bin/env python3
# overlay.py - Handles the camera detection overlay and piano mapping

import pygame
import numpy as np
import config
from terminal import add_terminal_message

# Overlay variables
overlay_active = False
line1_x = None
line2_x = None
line_y_top = None
line_y_bottom = None
line_width = 3
handle_size = 10
dragging_line1 = False
dragging_line2 = False
dragging_both = False
dragging_top = False
dragging_bottom = False
drag_start_pos = None
saved_line_positions = {}

# Handles for overlay adjustment
line1_top_handle = None
line1_bottom_handle = None
line2_top_handle = None
line2_bottom_handle = None
middle_top_handle = None
middle_bottom_handle = None

# Piano overlay variables
piano_overlay_slider_rect = None
piano_overlay_slider_handle_rect = None
piano_overlay_slider_value = 0.5
dragging_slider = False
piano_overlay_left = None
piano_overlay_right = None

# Import dependencies only when needed
piano_module = None

def _import_modules():
    """Import dependent modules only when needed"""
    global piano_module
    if piano_module is None:
        import piano
        piano_module = piano

def initialize_overlay():
    """Initialize the overlay with default positions"""
    global line1_x, line2_x, line_y_top, line_y_bottom
    global line1_top_handle, line1_bottom_handle, line2_top_handle, line2_bottom_handle
    global middle_top_handle, middle_bottom_handle
    global piano_overlay_slider_rect, piano_overlay_slider_handle_rect
    
    # Default positions
    if config.CAMERA_DISPLAY_RECT is not None:
        line1_x = config.CAMERA_DISPLAY_RECT.left + config.CAMERA_DISPLAY_RECT.width * 0.3
        line2_x = config.CAMERA_DISPLAY_RECT.left + config.CAMERA_DISPLAY_RECT.width * 0.7
        line_y_top = config.CAMERA_DISPLAY_RECT.top + config.CAMERA_DISPLAY_RECT.height * 0.25
        line_y_bottom = config.CAMERA_DISPLAY_RECT.top + config.CAMERA_DISPLAY_RECT.height * 0.75
        
        # Initialize handles
        update_handle_positions()
    
        # Initialize slider
        piano_overlay_slider_rect = pygame.Rect(50, config.CAMERA_DISPLAY_RECT.bottom + 10, 
                                              config.CAMERA_DISPLAY_RECT.width, 15)
        piano_overlay_slider_handle_rect = pygame.Rect(0, 0, 20, 25)
        
        # Save initial positions
        save_positions()

def is_active():
    """Check if overlay is active"""
    return overlay_active

def toggle():
    """Toggle the overlay on/off"""
    global overlay_active
    
    if overlay_active:
        overlay_active = False
        config.overlay_active = False
        config.piano_overlay_active = False
        save_positions()
        add_terminal_message("Overlay deactivated")
    else:
        overlay_active = True
        config.overlay_active = True
        update_handle_positions()
        calculate_piano_overlay()
        add_terminal_message("Overlay activated - adjust the lines to define detection area")

def save_positions():
    """Save current line positions"""
    global saved_line_positions
    
    saved_line_positions = {
        'line1_x': line1_x,
        'line2_x': line2_x,
        'line_y_top': line_y_top,
        'line_y_bottom': line_y_bottom
    }

def update_handle_positions():
    """Update handle positions based on line positions"""
    global line1_top_handle, line1_bottom_handle, line2_top_handle, line2_bottom_handle
    global middle_top_handle, middle_bottom_handle
    
    line1_top_handle = pygame.Rect(line1_x - handle_size//2, line_y_top - handle_size//2, handle_size, handle_size)
    line1_bottom_handle = pygame.Rect(line1_x - handle_size//2, line_y_bottom - handle_size//2, handle_size, handle_size)
    line2_top_handle = pygame.Rect(line2_x - handle_size//2, line_y_top - handle_size//2, handle_size, handle_size)
    line2_bottom_handle = pygame.Rect(line2_x - handle_size//2, line_y_bottom - handle_size//2, handle_size, handle_size)
    middle_top_handle = pygame.Rect((line1_x + line2_x)//2 - handle_size//2, line_y_top - handle_size//2, handle_size, handle_size)
    middle_bottom_handle = pygame.Rect((line1_x + line2_x)//2 - handle_size//2, line_y_bottom - handle_size//2, handle_size, handle_size)

def calculate_piano_overlay():
    """Calculate the piano overlay based on camera overlay"""
    global piano_overlay_left, piano_overlay_right
    
    _import_modules()
    
    # Get the width of the camera overlay
    camera_overlay_width = line2_x - line1_x
    
    # Get piano dimensions
    piano_left = piano_module.get_piano_left()
    piano_width = piano_module.get_piano_width()
    
    # Calculate position based on slider value
    available_width = piano_width - camera_overlay_width
    position = piano_left + available_width * piano_overlay_slider_value
    
    # Set piano overlay position
    piano_overlay_left = position
    piano_overlay_right = position + camera_overlay_width
    config.piano_overlay_active = True

def update_piano_overlay_from_slider():
    """Update piano overlay position based on slider value"""
    if not overlay_active:
        return
    
    calculate_piano_overlay()

def get_piano_overlay_positions():
    """Get the positions of the piano overlay"""
    return piano_overlay_left, piano_overlay_right

def handle_mouse_down(pos):
    """Handle mouse button down events for overlay interaction"""
    global dragging_line1, dragging_line2, dragging_both, dragging_top, dragging_bottom
    global drag_start_pos, dragging_slider
    
    if not overlay_active:
        return False
    
    # Check if piano slider is being dragged
    if piano_overlay_slider_rect.collidepoint(pos):
        dragging_slider = True
        # Update slider position based on mouse position
        piano_overlay_slider_value = (pos[0] - piano_overlay_slider_rect.left) / piano_overlay_slider_rect.width
        piano_overlay_slider_value = max(0, min(1, piano_overlay_slider_value))
        # Update piano overlay position
        update_piano_overlay_from_slider()
        return True
    
    # Check if any handle is being dragged
    if line1_top_handle.collidepoint(pos):
        dragging_line1 = True
        dragging_top = True
        drag_start_pos = pos
        return True
    elif line1_bottom_handle.collidepoint(pos):
        dragging_line1 = True
        dragging_bottom = True
        drag_start_pos = pos
        return True
    elif line2_top_handle.collidepoint(pos):
        dragging_line2 = True
        dragging_top = True
        drag_start_pos = pos
        return True
    elif line2_bottom_handle.collidepoint(pos):
        dragging_line2 = True
        dragging_bottom = True
        drag_start_pos = pos
        return True
    elif middle_top_handle.collidepoint(pos):
        dragging_both = True
        dragging_top = True
        drag_start_pos = pos
        return True
    elif middle_bottom_handle.collidepoint(pos):
        dragging_both = True
        dragging_bottom = True
        drag_start_pos = pos
        return True
    elif config.CAMERA_DISPLAY_RECT.collidepoint(pos):
        if abs(pos[0] - line1_x) < 10 and line_y_top <= pos[1] <= line_y_bottom:
            dragging_line1 = True
            drag_start_pos = pos
            return True
        elif abs(pos[0] - line2_x) < 10 and line_y_top <= pos[1] <= line_y_bottom:
            dragging_line2 = True
            drag_start_pos = pos
            return True
        elif line1_x < pos[0] < line2_x and line_y_top <= pos[1] <= line_y_bottom:
            dragging_both = True
            drag_start_pos = pos
            return True
    
    return False

def handle_mouse_motion(pos):
    """Handle mouse motion events for overlay interaction"""
    global line1_x, line2_x, line_y_top, line_y_bottom, drag_start_pos
    global piano_overlay_slider_value
    
    if not overlay_active or drag_start_pos is None:
        return
    
    if dragging_slider:
        # Update slider position based on mouse position
        piano_overlay_slider_value = (pos[0] - piano_overlay_slider_rect.left) / piano_overlay_slider_rect.width
        piano_overlay_slider_value = max(0, min(1, piano_overlay_slider_value))
        # Update piano overlay position
        update_piano_overlay_from_slider()
    
    elif dragging_line1 and not dragging_top and not dragging_bottom:
        # Dragging line1 horizontally
        dx = pos[0] - drag_start_pos[0]
        line1_x = max(config.CAMERA_DISPLAY_RECT.left, min(line1_x + dx, line2_x - 10))
        drag_start_pos = pos
        update_handle_positions()
        calculate_piano_overlay()
    
    elif dragging_line2 and not dragging_top and not dragging_bottom:
        # Dragging line2 horizontally
        dx = pos[0] - drag_start_pos[0]
        line2_x = min(config.CAMERA_DISPLAY_RECT.right, max(line2_x + dx, line1_x + 10))
        drag_start_pos = pos
        update_handle_positions()
        calculate_piano_overlay()
    
    elif dragging_both and not dragging_top and not dragging_bottom:
        # Dragging both lines horizontally
        dx = pos[0] - drag_start_pos[0]
        if line1_x + dx >= config.CAMERA_DISPLAY_RECT.left and line2_x + dx <= config.CAMERA_DISPLAY_RECT.right:
            line1_x += dx
            line2_x += dx
            drag_start_pos = pos
            update_handle_positions()
            calculate_piano_overlay()
    
    elif dragging_line1 and dragging_top:
        # Moving the top handle of line1
        dx = pos[0] - drag_start_pos[0]
        dy = pos[1] - drag_start_pos[1]
        line1_x = max(config.CAMERA_DISPLAY_RECT.left, min(line1_x + dx, line2_x - 10))
        line_y_top = max(config.CAMERA_DISPLAY_RECT.top, min(line_y_top + dy, line_y_bottom - 10))
        drag_start_pos = pos
        update_handle_positions()
        calculate_piano_overlay()
    
    elif dragging_line1 and dragging_bottom:
        # Moving the bottom handle of line1
        dx = pos[0] - drag_start_pos[0]
        dy = pos[1] - drag_start_pos[1]
        line1_x = max(config.CAMERA_DISPLAY_RECT.left, min(line1_x + dx, line2_x - 10))
        line_y_bottom = min(config.CAMERA_DISPLAY_RECT.bottom, max(line_y_bottom + dy, line_y_top + 10))
        drag_start_pos = pos
        update_handle_positions()
        calculate_piano_overlay()
    
    elif dragging_line2 and dragging_top:
        # Moving the top handle of line2
        dx = pos[0] - drag_start_pos[0]
        dy = pos[1] - drag_start_pos[1]
        line2_x = min(config.CAMERA_DISPLAY_RECT.right, max(line2_x + dx, line1_x + 10))
        line_y_top = max(config.CAMERA_DISPLAY_RECT.top, min(line_y_top + dy, line_y_bottom - 10))
        drag_start_pos = pos
        update_handle_positions()
        calculate_piano_overlay()
    
    elif dragging_line2 and dragging_bottom:
        # Moving the bottom handle of line2
        dx = pos[0] - drag_start_pos[0]
        dy = pos[1] - drag_start_pos[1]
        line2_x = min(config.CAMERA_DISPLAY_RECT.right, max(line2_x + dx, line1_x + 10))
        line_y_bottom = min(config.CAMERA_DISPLAY_RECT.bottom, max(line_y_bottom + dy, line_y_top + 10))
        drag_start_pos = pos
        update_handle_positions()
        calculate_piano_overlay()
    
    elif dragging_both and dragging_top:
        # Moving both top handles
        dy = pos[1] - drag_start_pos[1]
        line_y_top = max(config.CAMERA_DISPLAY_RECT.top, min(line_y_top + dy, line_y_bottom - 10))
        drag_start_pos = pos
        update_handle_positions()
    
    elif dragging_both and dragging_bottom:
        # Moving both bottom handles
        dy = pos[1] - drag_start_pos[1]
        line_y_bottom = min(config.CAMERA_DISPLAY_RECT.bottom, max(line_y_bottom + dy, line_y_top + 10))
        drag_start_pos = pos
        update_handle_positions()

def handle_mouse_up():
    """Handle mouse button up events for overlay interaction"""
    global dragging_line1, dragging_line2, dragging_both, dragging_top, dragging_bottom
    global drag_start_pos, dragging_slider
    
    # Reset all dragging states
    dragging_line1 = False
    dragging_line2 = False
    dragging_both = False
    dragging_top = False
    dragging_bottom = False
    dragging_slider = False
    drag_start_pos = None

def draw(screen):
    """Draw overlay on the screen"""
    if not overlay_active:
        return
    
    # Draw vertical lines
    pygame.draw.line(screen, config.RED, (line1_x, line_y_top), (line1_x, line_y_bottom), line_width)
    pygame.draw.line(screen, config.RED, (line2_x, line_y_top), (line2_x, line_y_bottom), line_width)
    
    # Draw horizontal connecting lines
    pygame.draw.line(screen, config.RED, (line1_x, line_y_top), (line2_x, line_y_top), line_width)
    pygame.draw.line(screen, config.RED, (line1_x, line_y_bottom), (line2_x, line_y_bottom), line_width)
    
    # Draw handles for easier manipulation
    pygame.draw.rect(screen, config.YELLOW, line1_top_handle)
    pygame.draw.rect(screen, config.YELLOW, line1_bottom_handle)
    pygame.draw.rect(screen, config.YELLOW, line2_top_handle)
    pygame.draw.rect(screen, config.YELLOW, line2_bottom_handle)
    pygame.draw.rect(screen, config.YELLOW, middle_top_handle)
    pygame.draw.rect(screen, config.YELLOW, middle_bottom_handle)
    
    # Draw distance information
    distance_text = f"Area: {line2_x - line1_x}px × {line_y_bottom - line_y_top}px"
    font = pygame.font.SysFont('Arial', 14)
    text = font.render(distance_text, True, config.BLACK)
    screen.blit(text, (config.CAMERA_DISPLAY_RECT.centerx - text.get_width() // 2, config.CAMERA_DISPLAY_RECT.bottom + 5))
    
    # Draw piano overlay slider
    slider_area = pygame.Rect(config.CAMERA_DISPLAY_RECT.left, config.CAMERA_DISPLAY_RECT.bottom + 30, config.CAMERA_DISPLAY_RECT.width, 40)
    pygame.draw.rect(screen, config.LIGHT_GRAY, slider_area)
    
    # Draw slider track
    pygame.draw.rect(screen, (128, 128, 128), piano_overlay_slider_rect)
    pygame.draw.rect(screen, config.BLACK, piano_overlay_slider_rect, 1)
    
    # Calculate handle position
    handle_x = piano_overlay_slider_rect.left + piano_overlay_slider_value * piano_overlay_slider_rect.width - 10
    piano_overlay_slider_handle_rect.topleft = (handle_x, piano_overlay_slider_rect.top - 5)
    
    # Draw slider handle
    pygame.draw.rect(screen, config.RED, piano_overlay_slider_handle_rect)
    pygame.draw.rect(screen, config.BLACK, piano_overlay_slider_handle_rect, 1)
    
    # Draw slider label
    slider_label = "Piano Overlay Position:"
    text = font.render(slider_label, True, config.BLACK)
    screen.blit(text, (piano_overlay_slider_rect.left, piano_overlay_slider_rect.top - 20))

def draw_status(screen, status_area):
    """Draw overlay status in the side panel"""
    # Draw current overlay settings
    status_font = pygame.font.SysFont('Arial', 14)
    
    title = pygame.font.SysFont('Arial', 16, bold=True)
    title_text = title.render("Detection Overlay", True, config.BLACK)
    screen.blit(title_text, (status_area.centerx - title_text.get_width()//2, status_area.top + 15))
    
    settings_text = f"Area: {line2_x - line1_x}px × {line_y_bottom - line_y_top}px"
    settings = status_font.render(settings_text, True, config.BLUE)
    screen.blit(settings, (status_area.left + 20, status_area.top + 50))
    
    # Draw adjustment instructions
    instructions = [
        "Move the vertical lines to define",
        "the area to detect fingertips.",
        "",
        "Drag the yellow handles:",
        "- Corner handles adjust both",
        "  position and size",
        "- Middle handles adjust the",
        "  height only",
        "",
        "Use the slider to change the",
        "position on the piano keys."
    ]
    
    for i, line in enumerate(instructions):
        text = status_font.render(line, True, config.BLACK)
        screen.blit(text, (status_area.left + 20, status_area.top + 80 + i * 20))