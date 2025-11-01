import pygame
import sys
import time

from src.Lava_Aqua.entities.player import Player
from src.Lava_Aqua.entities.lava import Lava
from src.Lava_Aqua.entities.tile import TileGrid, TileType
from src.Lava_Aqua.core.constants import TILE_SIZE


def load_level(filename):
    """Load level from text file."""
    with open(filename, 'r') as f:
        lines = [line.rstrip('\n') for line in f]
    width = max(len(line) for line in lines)
    grid = []
    for line in lines:
        row = list(line) + [' '] * (width - len(line))
        grid.append(row)
    return grid


def find_entities(grid_data):
    """Find player start and lava positions in grid data."""
    start = None
    lava_positions = []
    
    # Create a copy to modify
    grid = [row[:] for row in grid_data]
    
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            if ch == 'P':
                start = (x, y)
                grid[y][x] = ' '  # Replace with empty
            elif ch == 'L':
                lava_positions.append((x, y))
                grid[y][x] = ' '  # Replace with empty
    
    return start, lava_positions, grid


def can_move(player, dx, dy, tile_grid):
    """Check if player can move to new position."""
    x, y = player.get_position()
    nx, ny = x + dx, y + dy
    
    # Check if new position is walkable
    return tile_grid.is_walkable(nx, ny)


def run_level(level_file):
    """Run a single level."""
    # Load level data
    grid_data = load_level(level_file)
    start, lava_positions, clean_grid = find_entities(grid_data)
    
    # Store initial state for reset
    initial_start = start
    initial_lava = lava_positions.copy()
    
    # Create entities
    tile_grid = TileGrid(clean_grid)
    player = Player(start)
    lava = Lava(lava_positions)
    
    pygame.init()
    screen_width = tile_grid.get_width() * TILE_SIZE
    screen_height = tile_grid.get_height() * TILE_SIZE
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Lava & Aqua")
    clock = pygame.time.Clock()
    
    start_time = time.time()
    running = True
    
    while running:
        # Calculate animation time
        animation_time = time.time() - start_time
        
        moved = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.KEYDOWN:
                dx = dy = 0
                
                # Movement keys
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    dx = -1
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    dx = +1
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    dy = -1
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    dy = +1
                
                # Move player if valid
                if dx != 0 or dy != 0:
                    if can_move(player, dx, dy, tile_grid):
                        x, y = player.get_position()
                        player.set_position((x + dx, y + dy))
                        moved = True
                
                # Reset key
                elif event.key == pygame.K_r:
                    # Reset level
                    player.set_position(initial_start)
                    lava.reset(initial_lava)
                    print("Level reset!")
                    continue
        
        # Update lava flow after player moves
        if moved:
            # Convert tile grid to char grid for lava update
            char_grid = tile_grid.to_char_grid()
            lava.update(char_grid)
        
        # Check death (player on lava)
        player_pos = player.get_position()
        if lava.is_at(player_pos):
            print("Dead! Press R to restart or close window.")
            
            # Draw final state
            screen.fill((0, 0, 0))
            tile_grid.draw(screen, 0, 0, animation_time)
            lava.draw(screen, 0, 0, animation_time)
            player.draw(screen, 0, 0)
            
            # Draw "GAME OVER" text
            font = pygame.font.Font(None, 74)
            text = font.render('GAME OVER', True, (255, 0, 0))
            text_rect = text.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
            screen.blit(text, text_rect)
            
            # Small instruction text
            small_font = pygame.font.Font(None, 36)
            instruction = small_font.render('Press R to restart', True, (255, 255, 255))
            instr_rect = instruction.get_rect(center=(screen.get_width()//2, screen.get_height()//2 + 50))
            screen.blit(instruction, instr_rect)
            
            pygame.display.flip()
            
            # Wait for reset or quit
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            return False  # Restart level
                        elif event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()
        
        # Check win (player on exit)
        x, y = player_pos
        tile_type = tile_grid.get_tile_type(x, y)
        if tile_type == TileType.EXIT:
            print("You win!")
            
            # Draw final state
            screen.fill((0, 0, 0))
            tile_grid.draw(screen, 0, 0, animation_time)
            lava.draw(screen, 0, 0, animation_time)
            player.draw(screen, 0, 0)
            
            # Draw "YOU WIN" text
            font = pygame.font.Font(None, 74)
            text = font.render('YOU WIN!', True, (0, 255, 0))
            text_rect = text.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
            screen.blit(text, text_rect)
            
            pygame.display.flip()
            
            # Wait before continuing
            pygame.time.wait(2000)
            return True

        # Draw everything
        screen.fill((0, 0, 0))
        
        # Draw tiles first (background)
        tile_grid.draw(screen, 0, 0, animation_time)
        
        # Draw lava on top of tiles
        lava.draw(screen, 0, 0, animation_time)
        
        # Draw player on top
        player.draw(screen, 0, 0)
        
        # Draw UI info
        font = pygame.font.Font(None, 24)
        info_text = f'Lava tiles: {lava.count()} | R: Reset | WASD/Arrows: Move'
        text = font.render(info_text, True, (255, 255, 255))
        
        # Draw text background for readability
        text_bg = pygame.Surface((text.get_width() + 10, text.get_height() + 4))
        text_bg.set_alpha(180)
        text_bg.fill((0, 0, 0))
        screen.blit(text_bg, (5, 5))
        screen.blit(text, (10, 7))
        
        pygame.display.flip()
        clock.tick(60)
    
    return False


def main():
    """Main game loop."""
    level_files = ['level1.txt', 'level2.txt']
    current_level = 0
    
    print("🎮 Lava & Aqua - Terminal Edition")
    print("=" * 40)
    print("Controls:")
    print("  WASD or Arrow Keys - Move")
    print("  R - Reset level")
    print("  ESC - Quit")
    print("=" * 40)
    
    while current_level < len(level_files):
        print(f"\n🔥 Starting Level {current_level + 1}...")
        
        try:
            won = run_level(level_files[current_level])
            
            if won:
                current_level += 1
                if current_level >= len(level_files):
                    print("\n" + "=" * 40)
                    print("🎉 CONGRATULATIONS!")
                    print("You beat all levels!")
                    print("=" * 40)
                    break
            else:
                print(f"💀 Restarting level {current_level + 1}...")
        except FileNotFoundError:
            print(f"❌ Error: Could not find {level_files[current_level]}")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            break
    
    print("\nThanks for playing! 👋")


if __name__ == '__main__':
    main()