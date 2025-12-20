import pygame
from typing import List, Callable, Tuple

class MenuItem:
    """Represents a single item in the menu."""
    def __init__(self, text: str, on_select: Callable[[], None], description: str = ""):
        self.text = text
        self.on_select = on_select
        self.description = description

class Menu:
    """A reusable, scalable, and animated menu for Pygame."""
    def __init__(self, screen, title: str, items: List[MenuItem], config: dict = None):
        self.screen = screen
        self.title = title
        self.items = items
        self.selected_index = 0
        self.config = self._get_default_config()
        if config:
            self.config.update(config)
        
        # Animations
        self.hover_animations = [0.0] * len(items)
        
        # Fonts
        self.font_title = pygame.font.Font(None, self.config['font_size_title'])
        self.font_item = pygame.font.Font(None, self.config['font_size_item'])
        self.font_subtitle = pygame.font.Font(None, self.config['font_size_subtitle'])

        self._calculate_layout()

    def _get_default_config(self) -> dict:
        """Provides a default configuration for the menu's appearance."""
        return {
            'font_size_title': 74,
            'font_size_item': 42,
            'font_size_subtitle': 22,
            'color_bg': (10, 10, 20),
            'color_title': (255, 255, 255),
            'color_item': (200, 200, 220),
            'color_selected': (255, 100, 100),
            'color_border': (50, 50, 80),
            'padding': 50,
            'item_spacing': 20,
            'max_cols': 4,
        }

    def _calculate_layout(self):
        """Calculates the grid layout for the menu items."""
        self.cols = min(self.config['max_cols'], len(self.items))
        self.rows = (len(self.items) + self.cols - 1) // self.cols

    def _draw_background(self):
        self.screen.fill(self.config['color_bg'])

    def _draw_title(self):
        """Renders the main title and subtitle."""
        # Title
        title_surf = self.font_title.render(self.title, True, self.config['color_title'])
        title_rect = title_surf.get_rect(center=(self.screen.get_width() / 2, 80))
        self.screen.blit(title_surf, title_rect)
        
        # Subtitle
        subtitle_text = "Navigate with Arrow Keys • Select with Enter"
        subtitle_surf = self.font_subtitle.render(subtitle_text, True, self.config['color_item'])
        subtitle_rect = subtitle_surf.get_rect(center=(self.screen.get_width() / 2, 130))
        self.screen.blit(subtitle_surf, subtitle_rect)

    def _draw_items(self):
        """Draws all menu items in a grid."""
        padding = self.config['padding']
        spacing = self.config['item_spacing']
        
        start_y = 200
        available_width = self.screen.get_width() - 2 * padding
        
        box_width = (available_width - (self.cols - 1) * spacing) / self.cols
        box_height = 80
        
        start_x = padding

        for i, item in enumerate(self.items):
            col = i % self.cols
            row = i // self.cols
            
            x = start_x + col * (box_width + spacing)
            y = start_y + row * (box_height + spacing)
            
            self._draw_item(i, item, x, y, box_width, box_height)

    def _draw_item(self, index: int, item: MenuItem, x: int, y: int, width: int, height: int):
        """Draws a single menu item with animations."""
        is_selected = index == self.selected_index
        
        # Animation interpolation
        target_anim = 1.0 if is_selected else 0.0
        self.hover_animations[index] += (target_anim - self.hover_animations[index]) * 0.2
        anim = self.hover_animations[index]
        
        # Box
        rect = pygame.Rect(x, y, width, height)
        border_color = tuple(int(self.config['color_border'][i] + (self.config['color_selected'][i] - self.config['color_border'][i]) * anim) for i in range(3))
        pygame.draw.rect(self.screen, self.config['color_bg'], rect)
        pygame.draw.rect(self.screen, border_color, rect, int(2 + anim * 3))
        
        # Text
        text_color = tuple(int(self.config['color_item'][i] + (self.config['color_title'][i] - self.config['color_item'][i]) * anim) for i in range(3))
        text_surf = self.font_item.render(item.text, True, text_color)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)
        
    def draw(self):
        """Main drawing method, called every frame."""
        self._draw_background()
        self._draw_title()
        self._draw_items()
        pygame.display.flip()

    def run(self):
        """Runs the menu loop and handles events."""
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected_index = (self.selected_index - self.cols) % len(self.items)
                    elif event.key == pygame.K_DOWN:
                        self.selected_index = (self.selected_index + self.cols) % len(self.items)
                    elif event.key == pygame.K_LEFT:
                        self.selected_index = (self.selected_index - 1) % len(self.items)
                    elif event.key == pygame.K_RIGHT:
                        self.selected_index = (self.selected_index + 1) % len(self.items)
                    elif event.key == pygame.K_RETURN:
                        selected_item = self.items[self.selected_index]
                        selected_item.on_select() # Execute the callback
                        return # Exit the menu

            self.draw()
            clock.tick(60)

