dragging_line2 = True
                            dragging_bottom = True
                            drag_start_pos = mouse_pos
                            continue
                        elif middle_top_handle.collidepoint(mouse_pos):
                            dragging_both = True
                            dragging_top = True
                            drag_start_pos = mouse_pos
                            continue
                        elif middle_bottom_handle.collidepoint(mouse_pos):
                            dragging_both = True
                            dragging_bottom = True
                            drag_start_pos = mouse_pos
                            continue
                        elif CAMERA_DISPLAY_RECT.collidepoint(mouse_pos):
                            if abs(mouse_pos[0] - line1_x) < 10 and line_y_top <= mouse_pos[1] <= line_y_bottom:
                                dragging_line1 = True
                                drag_start_pos = mouse_pos
                                continue
                            elif abs(mouse_pos[0] - line2_x) < 10 and line_y_top <= mouse_pos[1] <= line_y_bottom:
                                dragging_line2 = True
                                drag_start_pos = mouse_pos
                                continue
                            elif line1_x < mouse_pos[0] < line2_x and line_y_top <= mouse_pos[1] <= line_y_bottom:
                                dragging_both = True
                                drag_start_pos = mouse_pos
                                continue
                    
                    # Check piano keys
                    if not (dragging_line1 or dragging_line2 or dragging_both or dragging_piano_overlay or dragging_slider or dragging_keyboard_overlay or dragging_keyboard_slider):
                        # Check if mouse is in piano area
                        if PIANO_TOP <= mouse_pos[1] <= PIANO_TOP + PIANO_HEIGHT:
                            # Check black keys first (they're on top)
                            black_key_hit = False
                            for i, key in enumerate(black_keys):
                                # Adjust key position for scrolling
                                adjusted_key = key.copy()
                                adjusted_key.x -= piano_scroll
                                
                                if adjusted_key.collidepoint(mouse_pos):
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
                                    
                                    if adjusted_key.collidepoint(mouse_pos):
                                        active_white_keys[i] = True
                                        play_note(i, False)
                                        break
                
                # Wheel scroll for piano
                elif event.button == 4:  # Scroll up
                    piano_scroll = max(0, piano_scroll - 30)
                    if piano_overlay_active:
                        calculate_piano_overlay_position()
                    if keyboard_overlay_active:
                        update_keyboard_overlay_from_slider()
                elif event.button == 5:  # Scroll down
                    piano_scroll = min(max_piano_scroll, piano_scroll + 30)
                    if piano_overlay_active:
                        calculate_piano_overlay_position()
                    if keyboard_overlay_active:
                        update_keyboard_overlay_from_slider()
            
            # Mouse motion
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                
                # Handle dragging the keyboard overlay
                if dragging_keyboard_overlay:
                    dx = mouse_pos[0] - drag_start_pos[0]
                    new_left = keyboard_overlay_left + dx
                    
                    # Make sure the overlay stays within the piano bounds
                    if new_left >= piano_left and new_left + keyboard_overlay_width <= piano_left + piano_width:
                        keyboard_overlay_left = new_left
                        keyboard_overlay_right = keyboard_overlay_left + keyboard_overlay_width
                        
                        # Update slider value
                        available_width = piano_width - keyboard_overlay_width
                        if available_width > 0:
                            keyboard_overlay_slider_value = (keyboard_overlay_left - piano_left) / available_width
                        
                        drag_start_pos = mouse_pos
                
                # Handle dragging the keyboard slider
                elif dragging_keyboard_slider:
                    keyboard_overlay_slider_value = (mouse_pos[0] - keyboard_overlay_slider_rect.left) / keyboard_overlay_slider_rect.width
                    keyboard_overlay_slider_value = max(0, min(1, keyboard_overlay_slider_value))
                    # Update keyboard overlay position
                    update_keyboard_overlay_from_slider()
                
                # Handle dragging the piano slider
                elif dragging_slider:
                    # Fixed slider dragging issue
                    piano_overlay_slider_value = (mouse_pos[0] - piano_overlay_slider_rect.left) / piano_overlay_slider_rect.width
                    piano_overlay_slider_value = max(0, min(1, piano_overlay_slider_value))
                    # Update piano overlay position
                    update_piano_overlay_from_slider()
                
                # Handle dragging the camera overlay
                elif overlay_active:
                    if dragging_line1 and not dragging_top and not dragging_bottom:
                        # Dragging line1 horizontally
                        dx = mouse_pos[0] - drag_start_pos[0]
                        line1_x = max(CAMERA_DISPLAY_RECT.left, min(line1_x + dx, line2_x - 10))
                        drag_start_pos = mouse_pos
                        update_handle_positions()
                        calculate_piano_overlay_position()  # Update piano overlay when camera overlay changes
                    
                    elif dragging_line2 and not dragging_top and not dragging_bottom:
                        # Dragging line2 horizontally
                        dx = mouse_pos[0] - drag_start_pos[0]
                        line2_x = min(CAMERA_DISPLAY_RECT.right, max(line2_x + dx, line1_x + 10))
                        drag_start_pos = mouse_pos
                        update_handle_positions()
                        calculate_piano_overlay_position()  # Update piano overlay when camera overlay changes
                    
                    elif dragging_both and not dragging_top and not dragging_bottom:
                        # Dragging both lines horizontally
                        dx = mouse_pos[0] - drag_start_pos[0]
                        if line1_x + dx >= CAMERA_DISPLAY_RECT.left and line2_x + dx <= CAMERA_DISPLAY_RECT.right:
                            line1_x += dx
                            line2_x += dx
                            drag_start_pos = mouse_pos
                            update_handle_positions()
                            calculate_piano_overlay_position()  # Update piano overlay when camera overlay changes
                    
                    elif dragging_line1 and dragging_top:
                        # Moving the top handle of line1
                        dx = mouse_pos[0] - drag_start_pos[0]
                        dy = mouse_pos[1] - drag_start_pos[1]
                        line1_x = max(CAMERA_DISPLAY_RECT.left, min(line1_x + dx, line2_x - 10))
                        line_y_top = max(CAMERA_DISPLAY_RECT.top, min(line_y_top + dy, line_y_bottom - 10))
                        drag_start_pos = mouse_pos
                        update_handle_positions()
                        calculate_piano_overlay_position()  # Update piano overlay when camera overlay changes
                    
                    elif dragging_line1 and dragging_bottom:
                        # Moving the bottom handle of line1
                        dx = mouse_pos[0] - drag_start_pos[0]
                        dy = mouse_pos[1] - drag_start_pos[1]
                        line1_x = max(CAMERA_DISPLAY_RECT.left, min(line1_x + dx, line2_x - 10))
                        line_y_bottom = min(CAMERA_DISPLAY_RECT.bottom, max(line_y_bottom + dy, line_y_top + 10))
                        drag_start_pos = mouse_pos
                        update_handle_positions()
                        calculate_piano_overlay_position()  # Update piano overlay when camera overlay changes
                    
                    elif dragging_line2 and dragging_top:
                        # Moving the top handle of line2
                        dx = mouse_pos[0] - drag_start_pos[0]
                        dy = mouse_pos[1] - drag_start_pos[1]
                        line2_x = min(CAMERA_DISPLAY_RECT.right, max(line2_x + dx, line1_x + 10))
                        line_y_top = max(CAMERA_DISPLAY_RECT.top, min(line_y_top + dy, line_y_bottom - 10))
                        drag_start_pos = mouse_pos
                        update_handle_positions()
                        calculate_piano_overlay_position()  # Update piano overlay when camera overlay changes
                    
                    elif dragging_line2 and dragging_bottom:
                        # Moving the bottom handle of line2
                        dx = mouse_pos[0] - drag_start_pos[0]
                        dy = mouse_pos[1] - drag_start_pos[1]
                        line2_x = min(CAMERA_DISPLAY_RECT.right, max(line2_x + dx, line1_x + 10))
                        line_y_bottom = min(CAMERA_DISPLAY_RECT.bottom, max(line_y_bottom + dy, line_y_top + 10))
                        drag_start_pos = mouse_pos
                        update_handle_positions()
                        calculate_piano_overlay_position()  # Update piano overlay when camera overlay changes
                    
                    elif dragging_both and dragging_top:
                        # Moving both top handles
                        dy = mouse_pos[1] - drag_start_pos[1]
                        line_y_top = max(CAMERA_DISPLAY_RECT.top, min(line_y_top + dy, line_y_bottom - 10))
                        drag_start_pos = mouse_pos
                        update_handle_positions()
                    
                    elif dragging_both and dragging_bottom:
                        # Moving both bottom handles
                        dy = mouse_pos[1] - drag_start_pos[1]
                        line_y_bottom = min(CAMERA_DISPLAY_RECT.bottom, max(line_y_bottom + dy, line_y_top + 10))
                        drag_start_pos = mouse_pos
                        update_handle_positions()
            
            # Mouse button up
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    # Reset button states
                    for button in buttons:
                        button["active"] = False
                    
                    # Reset piano key states
                    active_white_keys = [False] * len(white_keys)
                    active_black_keys = [False] * len(black_keys)
                    
                    # Reset all dragging states
                    dragging_slider = False
                    dragging_keyboard_slider = False
                    dragging_line1 = False
                    dragging_line2 = False
                    dragging_both = False
                    dragging_top = False
                    dragging_bottom = False
                    dragging_piano_overlay = False
                    dragging_keyboard_overlay = False
                    drag_start_pos = None
        
        # Draw button area background
        pygame.draw.rect(screen, LIGHT_GRAY, pygame.Rect(0, 0, WIDTH, BUTTON_AREA_HEIGHT))
        
        # Draw buttons
        for button in buttons:
            if button["active"]:
                pygame.draw.rect(screen, button["active_color"], button["rect"])
            else:
                pygame.draw.rect(screen, button["color"], button["rect"])
            pygame.draw.rect(screen, BLACK, button["rect"], 2)  # Border
            
            # Draw button text
            font = pygame.font.SysFont('Arial', 16)
            text = font.render(button["label"], True, WHITE)
            text_rect = text.get_rect(center=button["rect"].center)
            screen.blit(text, text_rect)
        
        # Draw camera area background
        pygame.draw.rect(screen, LIGHT_GRAY, 
                        pygame.Rect(0, BUTTON_AREA_HEIGHT, WIDTH, CAMERA_AREA_HEIGHT + 40))
        
        # Draw camera frame
        pygame.draw.rect(screen, BLACK, CAMERA_DISPLAY_RECT, 2)
        
        # Display camera feed if active
        if recording and camera_surface is not None:
            screen.blit(camera_surface, CAMERA_DISPLAY_RECT)
        else:
            # Draw placeholder text when camera is not active
            font = pygame.font.SysFont('Arial', 20)
            text_str = "Click 'Begin' to start recording" if camera is None or not recording else "Camera initializing..."
            text = font.render(text_str, True, BLACK)
            text_rect = text.get_rect(center=CAMERA_DISPLAY_RECT.center)
            screen.blit(text, text_rect)
        
        # Draw camera overlay if active
        if overlay_active:
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
    pygame.quit()
    sys.exit()


# Run the main function if this is the main script
if __name__ == "__main__":
    main()