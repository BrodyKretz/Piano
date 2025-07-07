# piano_app.py - Part 2
# Main application file for the Piano with Camera program

                # Draw text
                font = pygame.font.SysFont('Arial', 18)
                text = font.render(f"Place hand in box: {calibration_countdown//30 + 1}s", True, (0, 255, 0))
                text_rect = text.get_rect(centerx=calibration_rect.centerx, bottom=calibration_rect.top - 10)
                screen.blit(text, text_rect)
        else:
            # Draw placeholder text when camera is not active
            font = pygame.font.SysFont('Arial', 20)
            text_str = "Click 'Begin' to start recording" if camera is not None else "Camera not available"
            text = font.render(text_str, True, BLACK)
            text_rect = text.get_rect(center=CAMERA_DISPLAY_RECT.center)
            screen.blit(text, text_rect)
        
        # Draw camera overlay if active and not in calibration mode
        if overlay_active and not calibration_mode:
            # Draw vertical lines
            pygame.draw.line(screen, RED, (line1_x, line_y_top), (line1_x, line_y_bottom), line_width)
            pygame.draw.line(screen, RED, (line2_x, line_y_top), (line2_x, line_y_bottom), line_width)
            
            # Draw horizontal connecting lines
            pygame.draw.line(screen, RED, (line1_x, line_y_top), (line2_x, line_y_top), line_width)
            pygame.draw.line(screen, RED, (line1_x, line_y_bottom), (line2_x, line_y_bottom), line_width)
            
            # Draw handles for easier manipulation
            pygame.draw.rect(screen, YELLOW, line1_top_handle)
            pygame.draw.rect(screen, YELLOW, line1_bottom_handle)
            pygame.draw.rect(screen, YELLOW, line2_top_handle)
            pygame.draw.rect(screen, YELLOW, line2_bottom_handle)
            pygame.draw.rect(screen, YELLOW, middle_top_handle)
            pygame.draw.rect(screen, YELLOW, middle_bottom_handle)
            
            # Display distance information
            distance_text = f"Distance: {line2_x - line1_x}px | Height: {line_y_bottom - line_y_top}px"
            font = pygame.font.SysFont('Arial', 14)
            text = font.render(distance_text, True, BLACK)
            screen.blit(text, (CAMERA_DISPLAY_RECT.centerx - text.get_width() // 2, CAMERA_DISPLAY_RECT.bottom + 5))
        
        # Draw slider area background
        pygame.draw.rect(screen, LIGHT_GRAY, pygame.Rect(0, SLIDER_AREA_TOP, WIDTH, SLIDER_AREA_HEIGHT))
        
        # Draw piano overlay slider if overlay is active
        if piano_overlay_active:
            # Draw slider track
            pygame.draw.rect(screen, GRAY, piano_overlay_slider_rect)
            pygame.draw.rect(screen, BLACK, piano_overlay_slider_rect, 1)
            
            # Calculate handle position
            handle_x = piano_overlay_slider_rect.left + piano_overlay_slider_value * piano_overlay_slider_rect.width - 10
            piano_overlay_slider_handle_rect.topleft = (handle_x, piano_overlay_slider_rect.top - 5)
            
            # Draw slider handle
            pygame.draw.rect(screen, RED, piano_overlay_slider_handle_rect)
            pygame.draw.rect(screen, BLACK, piano_overlay_slider_handle_rect, 1)
            
            # Draw slider label
            slider_label = "Camera Overlay Position:"
            font = pygame.font.SysFont('Arial', 14)
            text = font.render(slider_label, True, BLACK)
            screen.blit(text, (piano_overlay_slider_rect.left - 20, piano_overlay_slider_rect.top - 25))
        
        # Draw keyboard overlay slider if active
        if keyboard_overlay_active:
            # Draw slider track
            pygame.draw.rect(screen, GRAY, keyboard_overlay_slider_rect)
            pygame.draw.rect(screen, BLACK, keyboard_overlay_slider_rect, 1)
            
            # Calculate handle position
            handle_x = keyboard_overlay_slider_rect.left + keyboard_overlay_slider_value * keyboard_overlay_slider_rect.width - 10
            keyboard_slider_handle_rect = pygame.Rect(handle_x, keyboard_overlay_slider_rect.top - 5, 20, 25)
            
            # Draw slider handle
            pygame.draw.rect(screen, BLUE, keyboard_slider_handle_rect)
            pygame.draw.rect(screen, BLACK, keyboard_slider_handle_rect, 1)
            
            # Draw slider label
            slider_label = "Keyboard Overlay Position:"
            font = pygame.font.SysFont('Arial', 14)
            text = font.render(slider_label, True, BLACK)
            screen.blit(text, (keyboard_overlay_slider_rect.left - 20, keyboard_overlay_slider_rect.top - 25))
        
        # Draw piano area background
        pygame.draw.rect(screen, LIGHT_GRAY, pygame.Rect(0, PIANO_TOP, WIDTH, PIANO_HEIGHT))
        
        # Draw scrolling instruction
        scroll_text = "Use left/right arrow keys or mouse wheel to scroll piano"
        font = pygame.font.SysFont('Arial', 14)
        text = font.render(scroll_text, True, BLACK)
        screen.blit(text, (10, PIANO_TOP - 20))
        
        # Draw piano keys
        # First white keys, then black keys on top
        for i, key in enumerate(white_keys):
            # Adjust key position for scrolling
            adjusted_key = key.copy()
            adjusted_key.x -= piano_scroll
            
            # Only draw keys that are visible
            if adjusted_key.right > 0 and adjusted_key.left < WIDTH:
                if active_white_keys[i]:
                    pygame.draw.rect(screen, GRAY, adjusted_key)
                else:
                    pygame.draw.rect(screen, IVORY, adjusted_key)
                pygame.draw.rect(screen, BLACK, adjusted_key, 1)
                
                # Draw note name at bottom of key
                font = pygame.font.SysFont('Arial', 10)
                text = font.render(white_notes[i], True, BLACK)
                text_rect = text.get_rect(centerx=adjusted_key.centerx, bottom=adjusted_key.bottom - 5)
                screen.blit(text, text_rect)
        
        # Draw black keys on top
        for i, key in enumerate(black_keys):
            # Adjust key position for scrolling
            adjusted_key = key.copy()
            adjusted_key.x -= piano_scroll
            
            # Only draw keys that are visible
            if adjusted_key.right > 0 and adjusted_key.left < WIDTH:
                if active_black_keys[i]:
                    pygame.draw.rect(screen, GRAY, adjusted_key)
                else:
                    pygame.draw.rect(screen, BLACK, adjusted_key)
        
        # Draw piano overlay if active
        if piano_overlay_active:
            # Draw a semi-transparent red rectangle over the piano
            overlay_rect = pygame.Rect(
                piano_overlay_left - piano_scroll,  # Adjust for scrolling
                PIANO_TOP,
                piano_overlay_right - piano_overlay_left,
                PIANO_HEIGHT
            )
            
            # Only draw if visible
            if overlay_rect.right > 0 and overlay_rect.left < WIDTH:
                # Create a surface with per-pixel alpha
                overlay_surface = pygame.Surface((overlay_rect.width, overlay_rect.height), pygame.SRCALPHA)
                # Fill with semi-transparent red
                overlay_surface.fill((255, 0, 0, 64))  # RGBA, A=64 for transparency
                screen.blit(overlay_surface, overlay_rect)
                
                # Draw borders
                pygame.draw.rect(screen, RED, overlay_rect, 2)
        
        # Draw keyboard overlay if active
        if keyboard_overlay_active:
            # Draw a semi-transparent blue rectangle over the piano
            overlay_rect = pygame.Rect(
                keyboard_overlay_left - piano_scroll,  # Adjust for scrolling
                PIANO_TOP,
                keyboard_overlay_width,
                PIANO_HEIGHT
            )
            
            # Only draw if visible
            if overlay_rect.right > 0 and overlay_rect.left < WIDTH:
                # Create a surface with per-pixel alpha
                overlay_surface = pygame.Surface((overlay_rect.width, overlay_rect.height), pygame.SRCALPHA)
                # Fill with semi-transparent blue
                overlay_surface.fill((100, 150, 255, 64))  # RGBA blue with transparency
                screen.blit(overlay_surface, overlay_rect)
                
                # Draw borders
                pygame.draw.rect(screen, BLUE, overlay_rect, 2)
                
                # Get the white keys that are within the overlay
                key_indices = get_white_key_indices_in_range(keyboard_overlay_left, keyboard_overlay_width)
                
                # Draw keyboard bindings on the keys
                for i, key_char in enumerate(keyboard_bindings):
                    # Only proceed if we have enough keys to bind
                    if i < len(key_indices) and i < len(keyboard_bindings):
                        # Get the actual piano key this corresponds to
                        piano_key_idx = key_indices[i]
                        key = white_keys[piano_key_idx]
                        
                        # Adjust for scrolling
                        key_x = key.x - piano_scroll
                        
                        # Only draw if visible
                        if key_x + WHITE_KEY_WIDTH > 0 and key_x < WIDTH:
                            # Highlight active keys
                            if active_keyboard_keys[i]:
                                key_rect = pygame.Rect(key_x, PIANO_TOP, WHITE_KEY_WIDTH, PIANO_HEIGHT)
                                # Create a surface with per-pixel alpha
                                key_surface = pygame.Surface((key_rect.width, key_rect.height), pygame.SRCALPHA)
                                # Fill with semi-transparent dark blue for active keys
                                key_surface.fill((70, 120, 220, 128))  # RGBA dark blue with transparency
                                screen.blit(key_surface, key_rect)
                            
                            # Draw the key character
                            font = pygame.font.SysFont('Arial', 20, bold=True)
                            text = font.render(key_char.upper(), True, BLACK)
                            text_rect = text.get_rect(centerx=key_x + WHITE_KEY_WIDTH//2, centery=PIANO_TOP + PIANO_HEIGHT//2)
                            screen.blit(text, text_rect)
        
        # Draw terminal area
        pygame.draw.rect(screen, LIGHT_GRAY, terminal_rect)
        pygame.draw.rect(screen, BLACK, terminal_rect, 2)
        
        # Draw terminal title
        title_text = terminal_font.render("Terminal Output:", True, BLACK)
        screen.blit(title_text, (10, TERMINAL_TOP + 10))
        
        # Draw terminal messages
        for i, message in enumerate(terminal_messages):
            text = terminal_font.render(message, True, BLACK)
            screen.blit(text, (10, TERMINAL_TOP + 40 + i * 20))
        
        # Draw piano scroll indicator
        if max_piano_scroll > 0:
            scroll_bar_width = WIDTH * (WIDTH / piano_width)
            scroll_bar_x = (WIDTH - scroll_bar_width) * (piano_scroll / max_piano_scroll)
            scroll_bar_rect = pygame.Rect(scroll_bar_x, PIANO_TOP + PIANO_HEIGHT + 5, scroll_bar_width, 10)
            pygame.draw.rect(screen, BLUE, scroll_bar_rect)
            pygame.draw.rect(screen, BLACK, pygame.Rect(0, PIANO_TOP + PIANO_HEIGHT + 5, WIDTH, 10), 1)
        
        pygame.display.flip()
        clock.tick(60)  # 60 FPS
    
    # Clean up
    if camera_active:
        stop_recording()

# Run the main function if this is the main script
if __name__ == "__main__":
    main()
    pygame.quit()
    sys.exit()