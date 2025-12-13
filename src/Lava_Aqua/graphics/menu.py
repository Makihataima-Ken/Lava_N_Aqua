import pygame
import math
import random
from typing import List
from src.Lava_Aqua.core.constants import Color

class Menu:
    def __init__(self, screen, title: str, options: List[str]):
        self.screen = screen
        self.title = title
        self.options = options
        self.selected = 0
        self.hover_animation = [0] * len(options)
        
        # Fonts
        self.font = pygame.font.Font(None, 52)
        self.option_font = pygame.font.Font(None, 32)
        self.subtitle_font = pygame.font.Font(None, 22)
        
        # Calculate grid layout
        self.cols = min(5, len(options))
        self.rows = (len(options) + self.cols - 1) // self.cols

    def _draw_background(self):
        """Draw solid dark background"""
        self.screen.fill(Color.BLACK)

    def _draw_title(self):
        """Draw title"""
        title_surf = self.font.render(self.title, True, Color.WHITE)
        title_rect = title_surf.get_rect(center=(400, 50))
        self.screen.blit(title_surf, title_rect)
        
        # Subtitle
        subtitle = "Navigate with Arrow Keys • Select with Enter"
        subtitle_surf = self.subtitle_font.render(subtitle, True, (140, 140, 140))
        subtitle_rect = subtitle_surf.get_rect(center=(400, 90))
        self.screen.blit(subtitle_surf, subtitle_rect)

    def _draw_box(self, index: int, option: str, x: int, y: int, width: int, height: int):
        """Draw individual box with hollow border on hover"""
        is_selected = index == self.selected
        
        # Smooth hover animation
        target_hover = 1.0 if is_selected else 0.0
        self.hover_animation[index] += (target_hover - self.hover_animation[index]) * 0.2
        hover = self.hover_animation[index]
        
        # Box background (solid grey)
        pygame.draw.rect(self.screen, Color.DARK_GRAY , (x, y, width, height))
        
        # Hollow border when hovering
        if hover > 0.01:
            # Alternate between red and blue based on position
            if index % 2 == 0:
                glow_color = tuple(int(Color.RED[i] * hover) for i in range(3))
            else:
                glow_color = tuple(int(Color.BLUE[i] * hover) for i in range(3))
            
            border_width = int(3 * hover) + 1
            pygame.draw.rect(self.screen, glow_color, (x, y, width, height), border_width)
        else:
            # Subtle border when not selected
            pygame.draw.rect(self.screen, (60, 60, 60), (x, y, width, height), 1)
        
        # Text
        text_surf = self.option_font.render(option, True, Color.WHITE)
        text_rect = text_surf.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(text_surf, text_rect)

    def _draw_boxes(self):
        """Draw all boxes in a grid layout"""
        # Calculate dimensions to fit screen
        padding = 50
        spacing = 15
        available_width = 800 - (2 * padding)
        available_height = 600 - 140 - padding
        
        # Calculate box dimensions
        box_width = (available_width - (self.cols - 1) * spacing) // self.cols
        box_height = (available_height - (self.rows - 1) * spacing) // self.rows
        
        # Ensure minimum size
        box_width = max(box_width, 100)
        box_height = max(box_height, 60)
        
        # Center the grid
        total_width = self.cols * box_width + (self.cols - 1) * spacing
        total_height = self.rows * box_height + (self.rows - 1) * spacing
        start_x = (800 - total_width) // 2
        start_y = 140
        
        # Draw each box
        for i, option in enumerate(self.options):
            col = i % self.cols
            row = i // self.cols
            x = start_x + col * (box_width + spacing)
            y = start_y + row * (box_height + spacing)
            self._draw_box(i, option, x, y, 130, 90)

    def draw(self):
        """Main draw method"""
        self._draw_background()
        self._draw_title()
        self._draw_boxes()
        pygame.display.flip()

    def run(self) -> int:
        """Returns index of selected option"""
        clock = pygame.time.Clock()
        
        while True:
            self.draw()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        new_selected = self.selected - self.cols
                        if new_selected >= 0:
                            self.selected = new_selected
                    elif event.key == pygame.K_DOWN:
                        new_selected = self.selected + self.cols
                        if new_selected < len(self.options):
                            self.selected = new_selected
                    elif event.key == pygame.K_LEFT:
                        if self.selected % self.cols > 0:
                            self.selected -= 1
                    elif event.key == pygame.K_RIGHT:
                        if self.selected % self.cols < self.cols - 1 and self.selected + 1 < len(self.options):
                            self.selected += 1
                    elif event.key == pygame.K_RETURN:
                        return self.selected
            
            clock.tick(60)