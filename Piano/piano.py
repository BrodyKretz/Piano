#!/usr/bin/env python3
# piano.py - Handles piano display, interaction, and sounds

import os
import pygame
import config
from terminal import add_terminal_message

# Global piano variables
white_keys = []
black_keys = []
white_key_count = 0
white_notes = []
black_notes = []
piano_width = 0
piano_left = 0
piano_scroll = 0
max_piano_scroll = 0
sounds = {}

# Active keys tracking
active_white_keys = []
active_black_keys = []

# Piano overlay position
piano_overlay_left = None
piano_overlay_right = None

def initialize_piano():
    """Initialize piano keys and layout"""
    global white_keys, black_keys, white_key_count, white_notes, black_notes
    global piano_width, piano_left, piano_scroll, max_piano_scroll
    global active_white_keys, active_black_keys
    
    white_keys = []
    black_keys = []
    white_key_count = 0
    white_notes = []
    black_notes = []
    
    # Setup note names
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave_names = ['0', '1', '2', '3', '4', '5', '6', '7', '8']
    
    # Calculate the piano width and center position
    num_white_keys = sum(1 for i in range(config.NUM_KEYS) if config.KEY_PATTERN[(i + config.START_NOTE) % 12])
    piano_width = num_white_keys * config.WHITE_KEY_WIDTH
    piano_left = (config.WIDTH - piano_width) // 2 if (config.WIDTH - piano_width) > 0 else 0
    
    # Create the piano keys
    for i in range(config.NUM_KEYS):
        midi_num = i + config.START_NOTE
        note_idx = midi_num % 12
        octave = midi_num // 12 - 1
        
        note_name = note_names[note_idx]
        octave_name = octave_names[octave] if 0 <= octave < len(octave_names) else "?"
        full_note_name = f"{note_name}{octave_name}"
        
        if config.KEY_PATTERN[note_idx]:  # White key
            x = piano_left + white_key_count * config.WHITE_KEY_WIDTH
            key_rect = pygame.Rect(x, config.PIANO_TOP, config.WHITE_KEY_WIDTH, config.PIANO_HEIGHT)
            white_keys.append(key_rect)
            white_notes.append(full_note_name)
            white_key_count += 1
        else:  # Black key
            # Position black keys relative to white keys
            if note_idx in [1, 3]:  # C#, D#
                x = piano_left + (white_key_count - 1) * config.WHITE_KEY_WIDTH + config.WHITE_KEY_WIDTH * 0.75
            elif note_idx in [6, 8, 10]:  # F#, G#, A#
                x = piano_left + (white_key_count - 1) * config.WHITE_KEY_WIDTH + config.WHITE_KEY_WIDTH * 0.75
            else:
                continue
                
            key_rect = pygame.Rect(x, config.PIANO_TOP, config.BLACK_KEY_WIDTH, config.BLACK_KEY_HEIGHT)
            black_keys.append(key_rect)
            black_notes.append(full_note_name)
    
    # Initialize active key tracking
    active_white_keys = [False] * len(white_keys)
    active_black_keys = [False] * len(black_keys)
    
    # Set max piano scroll
    piano_scroll = 0
    max_piano_scroll = max(0, piano_width - config.WIDTH)
    
    add_terminal_message(f"Piano initialized with {len(white_keys)} white keys and {len(black_keys)} black keys")

def load_piano_sounds():
    """Load piano sound files from the piano-mp3 directory"""
    global sounds
    
    # Initialize default sounds with empty buffers
    for i in range(len(white_keys)):
        sounds[i] = pygame.mixer.Sound(buffer=bytearray(4000))
    for i in range(len(black_keys)):
        sounds[1000 + i] = pygame.mixer.Sound(buffer=bytearray(4000))
    
    try:
        # Path to piano sounds directory
        sound_dir = "piano-mp3"
        if not os.path.exists(sound_dir):
            os.makedirs(sound_dir)
            add_terminal_message(f"Created piano sounds directory: {sound_dir}")
        
        # Load sounds for white keys
        for i, note_name in enumerate(white_notes):
            try:
                note_file = os.path.join(sound_dir, f"{note_name}.mp3")
                if os.path.exists(note_file):
                    sounds[i] = pygame.mixer.Sound(note_file)
                    sounds[i].set_volume(0.8)  # Set volume to 80%
                    print(f"Loaded {note_file}")
                else:
                    print(f"Sound file not found: {note_file}")
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
                    print(f"Sound file not found: {note_file}")
                    # Fallback to empty buffer if file doesn't exist
                    sounds[1000 + i] = pygame.mixer.Sound(buffer=bytearray(4000))
            except Exception as e:
                print(f"Error loading sound for {note_name}: {e}")
                sounds[1000 + i] = pygame.mixer.Sound(buffer=bytearray(4000))
        
        add_terminal_message(f"Loaded piano sounds from {sound_dir}")
        return True
    except Exception as e:
        add_terminal_message(f"Error loading piano sounds: {e}")
        return False

def play_note(note_idx, is_black=False):
    """Play a note and show message in terminal"""
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
        
        # Print debug info
        debug_msg = f"Playing {note_name} (sound index {sound_idx})"
        print(debug_msg)
        
        # Add message to terminal
        add_terminal_message(debug_msg)
        return True
    except Exception as e:
        error_msg = f"Error playing note: {e}"
        print(error_msg)
        add_terminal_message(error_msg)
        return False

def draw_piano(screen):
    """Draw the piano keyboard on the screen"""
    # First draw white keys
    for i, key in enumerate(white_keys):
        # Adjust key position for scrolling
        adjusted_key = key.copy()
        adjusted_key.x -= piano_scroll
        
        # Only draw keys that are visible
        if adjusted_key.right > 0 and adjusted_key.left < config.WIDTH:
            if active_white_keys[i]:
                pygame.draw.rect(screen, config.GRAY, adjusted_key)
            else:
                pygame.draw.rect(screen, config.IVORY, adjusted_key)
            pygame.draw.rect(screen, config.BLACK, adjusted_key, 1)
            
            # Draw note name at bottom of key
            font = pygame.font.SysFont('Arial', 10)
            text = font.render(white_notes[i], True, config.BLACK)
            text_rect = text.get_rect(centerx=adjusted_key.centerx, bottom=adjusted_key.bottom - 5)
            screen.blit(text, text_rect)
    
    # Then draw black keys on top
    for i, key in enumerate(black_keys):
        # Adjust key position for scrolling
        adjusted_key = key.copy()
        adjusted_key.x -= piano_scroll
        
        # Only draw keys that are visible
        if adjusted_key.right > 0 and adjusted_key.left < config.WIDTH:
            if active_black_keys[i]:
                pygame.draw.rect(screen, config.GRAY, adjusted_key)
            else:
                pygame.draw.rect(screen, config.BLACK, adjusted_key)
    
    # Draw piano overlay if active
    overlay_module = None
    if config.piano_overlay_active and piano_overlay_left is not None and piano_overlay_right is not None:
        overlay_rect = pygame.Rect(
            piano_overlay_left - piano_scroll,  # Adjust for scrolling
            config.PIANO_TOP,
            piano_overlay_right - piano_overlay_left,
            config.PIANO_HEIGHT
        )
        
        # Only draw if visible
        if overlay_rect.right > 0 and overlay_rect.left < config.WIDTH:
            # Create a surface with per-pixel alpha
            overlay_surface = pygame.Surface((overlay_rect.width, overlay_rect.height), pygame.SRCALPHA)
            # Fill with semi-transparent red
            overlay_surface.fill((255, 0, 0, 64))  # RGBA, A=64 for transparency
            screen.blit(overlay_surface, overlay_rect)
            
            # Draw borders
            pygame.draw.rect(screen, (255, 0, 0), overlay_rect, 2)
    
    # Draw keyboard overlay letters if active
    if config.keyboard_overlay_active:
        draw_keyboard_overlay(screen)
    
    # Draw piano scroll indicator
    if max_piano_scroll > 0:
        scroll_bar_width = config.WIDTH * (config.WIDTH / piano_width)
        scroll_bar_x = (config.WIDTH - scroll_bar_width) * (piano_scroll / max_piano_scroll)
        scroll_bar_rect = pygame.Rect(scroll_bar_x, config.PIANO_TOP + config.PIANO_HEIGHT + 5, scroll_bar_width, 10)
        pygame.draw.rect(screen, (100, 150, 255), scroll_bar_rect)
        pygame.draw.rect(screen, config.BLACK, pygame.Rect(0, config.PIANO_TOP + config.PIANO_HEIGHT + 5, config.WIDTH, 10), 1)

    # Draw scrolling instruction
    scroll_text = "Use left/right arrow keys or mouse wheel to scroll piano"
    font = pygame.font.SysFont('Arial', 14)
    text = font.render(scroll_text, True, config.BLACK)
    screen.blit(text, (10, config.PIANO_TOP - 20))
    
    # Add keyboard instruction if keyboard mode is active
    if config.keyboard_overlay_active:
        kb_text = "Keyboard mode: Use A-S-D-F-G-H-J-K-L to play piano"
        kb_font = pygame.font.SysFont('Arial', 14)
        kb_render = kb_font.render(kb_text, True, config.BLUE)
        screen.blit(kb_render, (config.WIDTH - kb_render.get_width() - 10, config.PIANO_TOP - 20))

def check_piano_click(pos):
    """Check if a piano key was clicked and play the corresponding note"""
    # Only process if position is within piano area
    if config.PIANO_TOP <= pos[1] <= config.PIANO_TOP + config.PIANO_HEIGHT:
        # Check black keys first (they're on top)
        black_key_hit = False
        for i, key in enumerate(black_keys):
            # Adjust key position for scrolling
            adjusted_key = key.copy()
            adjusted_key.x -= piano_scroll
            
            if adjusted_key.collidepoint(pos):
                active_black_keys[i] = True
                play_note(i, True)
                black_key_hit = True
                break
        
        # If no black key was hit, check white keys
        if not black_key_hit:
            for i, key in enumerate(white_keys):
                # Adjust key position for scrolling
                adjusted_key = key.copy()
                adjusted_key.x -= piano_scroll
                
                if adjusted_key.collidepoint(pos):
                    active_white_keys[i] = True
                    play_note(i, False)
                    break
        
        return True
    return False

def reset_active_keys():
    """Reset all active piano keys"""
    global active_white_keys, active_black_keys
    
    active_white_keys = [False] * len(white_keys)
    active_black_keys = [False] * len(black_keys)

def update_piano_scroll(amount):
    """Update piano scroll position"""
    global piano_scroll
    
    piano_scroll = max(0, min(max_piano_scroll, piano_scroll + amount))

def set_piano_overlay(left, right):
    """Set the piano overlay position based on camera detection area"""
    global piano_overlay_left, piano_overlay_right
    
    print(f"Setting piano overlay position to {left} - {right}")
    piano_overlay_left = left
    piano_overlay_right = right
    config.piano_overlay_active = True

def get_piano_left():
    """Get the left edge of the piano"""
    return piano_left

def get_piano_width():
    """Get the width of the piano"""
    return piano_width

def get_visible_white_keys():
    """Get a list of indices for white keys that are currently visible"""
    visible_white_keys = []
    
    # Calculate visible area
    visible_start = piano_scroll
    visible_end = visible_start + config.WIDTH
    
    # Find which white keys are currently visible
    for i, key in enumerate(white_keys):
        if key.left <= visible_end and key.right >= visible_start:
            visible_white_keys.append(i)
    
    return visible_white_keys

def get_white_keys_in_overlay():
    """Get a list of white key indices that are within the piano overlay"""
    overlay_keys = []
    
    # If overlay is not active or positions are not set, return empty list
    if not config.piano_overlay_active or piano_overlay_left is None or piano_overlay_right is None:
        return get_visible_white_keys()  # Fall back to all visible keys
    
    # Find which white keys are within the overlay area
    for i, key in enumerate(white_keys):
        # Check if key overlaps with overlay
        if (key.left <= piano_overlay_right and key.right >= piano_overlay_left):
            overlay_keys.append(i)
    
    # If no keys are in overlay (shouldn't happen), fall back to visible keys
    if not overlay_keys:
        return get_visible_white_keys()
        
    return overlay_keys

def handle_keyboard_input(key_char):
    """Handle keyboard input and play the corresponding note"""
    global white_keys, black_keys, white_notes, black_notes
    global active_white_keys, active_black_keys
    
    # Define which keys respond to which keyboard characters
    keyboard_bindings = ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l']
    
    # Map each keyboard key to a piano key
    if key_char in keyboard_bindings:
        key_index = keyboard_bindings.index(key_char)
        
        # Check if overlay is active and use keys within overlay
        if config.piano_overlay_active and piano_overlay_left is not None and piano_overlay_right is not None:
            # Get keys within the overlay
            overlay_keys = get_white_keys_in_overlay()
            print(f"Overlay keys: {overlay_keys}")
            
            # If we don't have any overlay keys, return
            if not overlay_keys:
                return False
                
            # Distribute keyboard keys evenly across overlay keys
            num_overlay_keys = len(overlay_keys)
            
            # If we only have a few overlay keys
            if num_overlay_keys <= len(keyboard_bindings):
                # Map keyboard keys directly to overlay keys
                if key_index < num_overlay_keys:
                    piano_key_index = overlay_keys[key_index]
                else:
                    # Not enough overlay keys for this keyboard key
                    return False
            else:
                # We have more piano keys than keyboard keys, so evenly distribute
                # Calculate spacing to evenly distribute the keyboard keys
                spacing = (num_overlay_keys - 1) / (len(keyboard_bindings) - 1)
                piano_idx = int(round(key_index * spacing))
                
                # Ensure we don't go out of bounds
                piano_idx = min(piano_idx, len(overlay_keys) - 1)
                piano_key_index = overlay_keys[piano_idx]
        else:
            # No overlay, use all visible keys
            visible_white_keys = get_visible_white_keys()
            
            # If we don't have any visible keys, return
            if not visible_white_keys:
                return False
                
            # Distribute keyboard keys evenly across visible piano keys
            num_visible_keys = len(visible_white_keys)
            
            # If we only have a few visible keys
            if num_visible_keys <= len(keyboard_bindings):
                # Map keyboard keys directly to visible keys
                if key_index < num_visible_keys:
                    piano_key_index = visible_white_keys[key_index]
                else:
                    # Not enough visible keys for this keyboard key
                    return False
            else:
                # We have more piano keys than keyboard keys, so evenly distribute
                # Calculate spacing to evenly distribute the keyboard keys
                spacing = (num_visible_keys - 1) / (len(keyboard_bindings) - 1)
                piano_idx = int(round(key_index * spacing))
                
                # Ensure we don't go out of bounds
                piano_idx = min(piano_idx, len(visible_white_keys) - 1)
                piano_key_index = visible_white_keys[piano_idx]
        
        # Update active keys and play note
        active_white_keys[piano_key_index] = True
        play_note(piano_key_index, False)
        
        # Debug output
        print(f"Keyboard key {key_char} mapped to piano key {piano_key_index} ({white_notes[piano_key_index]})")
        return True
    
    return False

def release_keyboard_key(key_char):
    """Handle keyboard key release"""
    global active_white_keys, active_black_keys
    
    # Define which keys respond to which keyboard characters
    keyboard_bindings = ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l']
    
    if key_char in keyboard_bindings:
        key_index = keyboard_bindings.index(key_char)
        
        # Check if overlay is active and use keys within overlay
        if config.piano_overlay_active and piano_overlay_left is not None and piano_overlay_right is not None:
            # Get keys within the overlay
            overlay_keys = get_white_keys_in_overlay()
            
            # If we don't have any overlay keys, return
            if not overlay_keys:
                return
                
            # Distribute keyboard keys evenly across overlay keys
            num_overlay_keys = len(overlay_keys)
            
            # If we only have a few overlay keys
            if num_overlay_keys <= len(keyboard_bindings):
                # Map keyboard keys directly to overlay keys
                if key_index < num_overlay_keys:
                    piano_key_index = overlay_keys[key_index]
                    active_white_keys[piano_key_index] = False
            else:
                # We have more piano keys than keyboard keys, so evenly distribute
                # Calculate spacing to evenly distribute the keyboard keys
                spacing = (num_overlay_keys - 1) / (len(keyboard_bindings) - 1)
                piano_idx = int(round(key_index * spacing))
                
                # Ensure we don't go out of bounds
                piano_idx = min(piano_idx, len(overlay_keys) - 1)
                piano_key_index = overlay_keys[piano_idx]
                active_white_keys[piano_key_index] = False
        else:
            # No overlay, use all visible keys
            visible_white_keys = get_visible_white_keys()
            
            # If we don't have any visible keys, return
            if not visible_white_keys:
                return
                
            # Distribute keyboard keys evenly across visible piano keys
            num_visible_keys = len(visible_white_keys)
            
            # If we only have a few visible keys
            if num_visible_keys <= len(keyboard_bindings):
                # Map keyboard keys directly to visible keys
                if key_index < num_visible_keys:
                    piano_key_index = visible_white_keys[key_index]
                    active_white_keys[piano_key_index] = False
            else:
                # We have more piano keys than keyboard keys, so evenly distribute
                # Calculate spacing to evenly distribute the keyboard keys
                spacing = (num_visible_keys - 1) / (len(keyboard_bindings) - 1)
                piano_idx = int(round(key_index * spacing))
                
                # Ensure we don't go out of bounds
                piano_idx = min(piano_idx, len(visible_white_keys) - 1)
                piano_key_index = visible_white_keys[piano_idx]
                active_white_keys[piano_key_index] = False

def draw_keyboard_overlay(screen):
    """Draw letters on piano keys that are mapped to keyboard keys"""
    if not config.keyboard_overlay_active:
        return
        
    # Define which keys respond to which keyboard characters
    keyboard_bindings = ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l']
    
    # Check if piano overlay is active and get appropriate keys
    if config.piano_overlay_active and piano_overlay_left is not None and piano_overlay_right is not None:
        # Get keys within the overlay
        target_keys = get_white_keys_in_overlay()
    else:
        # No overlay, use all visible keys
        target_keys = get_visible_white_keys()
    
    # If we don't have any target keys, return
    if not target_keys:
        return
        
    # Map keyboard keys to target piano keys
    mapped_keys = []
    num_target_keys = len(target_keys)
    
    # If we only have a few target keys
    if num_target_keys <= len(keyboard_bindings):
        # Map keyboard keys directly to target keys
        for i, key_index in enumerate(target_keys):
            if i < len(keyboard_bindings):
                mapped_keys.append((i, key_index, keyboard_bindings[i]))
    else:
        # We have more piano keys than keyboard keys, so evenly distribute
        for i, kb_key in enumerate(keyboard_bindings):
            # Calculate spacing to evenly distribute the keyboard keys
            spacing = (num_target_keys - 1) / (len(keyboard_bindings) - 1)
            piano_idx = int(round(i * spacing))
            
            # Ensure we don't go out of bounds
            piano_idx = min(piano_idx, len(target_keys) - 1)
            piano_key_index = target_keys[piano_idx]
            mapped_keys.append((i, piano_key_index, kb_key))
    
    # Draw keyboard letters on mapped piano keys
    font = pygame.font.SysFont('Arial', 16, bold=True)
    
    for kb_index, key_index, key_char in mapped_keys:
        # Get the key rectangle
        key = white_keys[key_index]
        
        # Create adjusted key rectangle accounting for scroll
        adjusted_key = key.copy()
        adjusted_key.x -= piano_scroll
        
        # Only draw if key is visible
        if adjusted_key.right <= 0 or adjusted_key.left >= config.WIDTH:
            continue
        
        # Draw letter in a small circle
        letter = key_char.upper()
        text = font.render(letter, True, config.BLACK)
        
        # Create circle for the letter
        circle_center = (adjusted_key.centerx, adjusted_key.top + 30)
        circle_radius = 15
        
        # Draw circle background
        pygame.draw.circle(screen, config.BLUE, circle_center, circle_radius)
        pygame.draw.circle(screen, config.BLACK, circle_center, circle_radius, 1)  # Border
        
        # Draw letter
        text_rect = text.get_rect(center=circle_center)
        screen.blit(text, text_rect)