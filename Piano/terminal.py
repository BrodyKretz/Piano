#!/usr/bin/env python3
# terminal.py - Handles terminal output for the application

import pygame
import config

# Global terminal instance
terminal = None

class Terminal:
    """Terminal class for displaying messages and logs"""
    def __init__(self, rect, max_messages=15):
        self.rect = rect
        self.messages = []
        self.max_messages = max_messages
        self.font = pygame.font.SysFont('Courier', 16)
        self.title_font = pygame.font.SysFont('Courier', 18, bold=True)
        self.scroll_offset = 0
        self.max_scroll = 0
    
    def add_message(self, message):
        """Add a message to the terminal"""
        self.messages.append(message)
        if len(self.messages) > self.max_messages + self.scroll_offset:
            self.scroll_offset += 1
        self.max_scroll = max(0, len(self.messages) - self.max_messages)
    
    def scroll_up(self):
        """Scroll terminal up to see older messages"""
        self.scroll_offset = max(0, self.scroll_offset - 1)
    
    def scroll_down(self):
        """Scroll terminal down to see newer messages"""
        self.scroll_offset = min(self.max_scroll, self.scroll_offset + 1)
    
    def draw(self, screen):
        """Draw the terminal to the screen"""
        # Draw terminal background
        pygame.draw.rect(screen, config.LIGHT_GRAY, self.rect)
        pygame.draw.rect(screen, config.BLACK, self.rect, 2)
        
        # Draw terminal title
        title_text = self.title_font.render("Terminal Output:", True, config.BLACK)
        screen.blit(title_text, (self.rect.left + 10, self.rect.top + 10))
        
        # Draw scroll indicators if needed
        if self.scroll_offset > 0:
            up_arrow = "↑ More messages above"
            arrow_text = self.font.render(up_arrow, True, config.BLUE)
            screen.blit(arrow_text, (self.rect.right - arrow_text.get_width() - 10, self.rect.top + 10))
        
        if self.scroll_offset < self.max_scroll:
            down_arrow = "↓ More messages below"
            arrow_text = self.font.render(down_arrow, True, config.BLUE)
            screen.blit(arrow_text, (self.rect.right - arrow_text.get_width() - 10, self.rect.bottom - 30))
        
        # Draw terminal messages
        display_start = self.scroll_offset
        display_end = min(len(self.messages), display_start + self.max_messages)
        
        for i, message in enumerate(self.messages[display_start:display_end]):
            text = self.font.render(message, True, config.BLACK)
            # Use text wrapping if message is too long
            if text.get_width() > self.rect.width - 20:
                words = message.split()
                lines = []
                current_line = []
                
                for word in words:
                    test_line = ' '.join(current_line + [word])
                    test_text = self.font.render(test_line, True, config.BLACK)
                    
                    if test_text.get_width() <= self.rect.width - 20:
                        current_line.append(word)
                    else:
                        if current_line:
                            lines.append(' '.join(current_line))
                            current_line = [word]
                        else:
                            # Word is too long, truncate it
                            lines.append(word[:20] + "...")
                
                if current_line:
                    lines.append(' '.join(current_line))
                
                for j, line in enumerate(lines):
                    line_text = self.font.render(line, True, config.BLACK)
                    screen.blit(line_text, (self.rect.left + 10, self.rect.top + 40 + (i + j) * 20))
                
                i += len(lines) - 1  # Adjust for multiple lines
            else:
                screen.blit(text, (self.rect.left + 10, self.rect.top + 40 + i * 20))

def initialize_terminal():
    """Initialize the terminal"""
    global terminal
    # Create terminal only after pygame is initialized
    terminal_rect = pygame.Rect(config.TERMINAL_LEFT, config.TERMINAL_TOP, 
                              config.TERMINAL_WIDTH, config.TERMINAL_HEIGHT)
    terminal = Terminal(terminal_rect)
    return terminal

def add_terminal_message(message):
    """Add a message to the terminal"""
    if terminal is not None:
        terminal.add_message(message)
    print(f"Terminal: {message}")  # Also output to console for debugging

def get_terminal():
    """Get the terminal instance"""
    return terminal