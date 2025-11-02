import pygame
import sys
import time

from src.Lava_Aqua.core.game import GameLogic
from src.Lava_Aqua.entities.tile import TileGrid
from src.Lava_Aqua.core.constants import TILE_SIZE


def run_level(game_logic):
    """Run a single level using GameLogic.
    
    Args:
        game_logic: GameLogic instance
        
    Returns:
        str: 'win' if level completed, 'restart' if restarting, 'quit' to exit
    """
    # Create tile grid from game logic grid
    tile_grid = TileGrid(game_logic.grid)
    
    pygame.init()
    screen_width = tile_grid.get_width() * TILE_SIZE
    screen_height = tile_grid.get_height() * TILE_SIZE
    screen = pygame.display.set_mode((screen_width, screen_height))
    
    level_name = game_logic.get_level_name()
    level_num = game_logic.get_level_number()
    total_levels = game_logic.get_total_levels()
    
    pygame.display.set_caption(f"Lava & Aqua - Level {level_num}/{total_levels}: {level_name}")
    clock = pygame.time.Clock()
    
    start_time = time.time()
    running = True
    
    while running:
        # Calculate animation time
        animation_time = time.time() - start_time
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            
            elif event.type == pygame.KEYDOWN:
                dx = dy = 0
                
                # Movement keys
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    dx = -1
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    dx = 1
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    dy = -1
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    dy = 1
                
                # Move player if valid
                if dx != 0 or dy != 0:
                    game_logic.move_player((dx, dy))
                
                # Reset key
                elif event.key == pygame.K_r:
                    game_logic.reset_level()
                    # Recreate tile grid with fresh data
                    tile_grid = TileGrid(game_logic.grid)
                    print(f"Level reset! (Moves: {game_logic.moves})")
                    continue
                
                # Undo key
                elif event.key == pygame.K_u or event.key == pygame.K_z:
                    if game_logic.undo():
                        # Recreate tile grid after undo
                        tile_grid = TileGrid(game_logic.grid)
                        print(f"Undo! (Moves: {game_logic.moves})")
                
                # Escape to quit
                elif event.key == pygame.K_ESCAPE:
                    return 'quit'
        
        # Check for game over
        if game_logic.game_over:
            print("Dead! Press R to restart or ESC to quit.")
            
            # Draw final state
            screen.fill((0, 0, 0))
            tile_grid.draw(screen, 0, 0, animation_time)
            game_logic.lava.draw(screen, 0, 0, animation_time)
            game_logic.player.draw(screen, 0, 0)
            
            # Draw "GAME OVER" text
            font = pygame.font.Font(None, 74)
            text = font.render('GAME OVER', True, (255, 0, 0))
            text_rect = text.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
            screen.blit(text, text_rect)
            
            # Small instruction text
            small_font = pygame.font.Font(None, 36)
            instruction = small_font.render('Press R to restart | U to undo', True, (255, 255, 255))
            instr_rect = instruction.get_rect(center=(screen.get_width()//2, screen.get_height()//2 + 50))
            screen.blit(instruction, instr_rect)
            
            pygame.display.flip()
            
            # Wait for reset or quit
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return 'quit'
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            return 'restart'
                        elif event.key == pygame.K_u or event.key == pygame.K_z:
                            if game_logic.undo():
                                tile_grid = TileGrid(game_logic.grid)
                                waiting = False  # Continue playing
                        elif event.key == pygame.K_ESCAPE:
                            return 'quit'
        
        # Check for level complete
        if game_logic.level_complete:
            print(f"You win! Completed in {game_logic.moves} moves!")
            
            # Draw final state
            screen.fill((0, 0, 0))
            tile_grid.draw(screen, 0, 0, animation_time)
            game_logic.lava.draw(screen, 0, 0, animation_time)
            game_logic.player.draw(screen, 0, 0)
            
            # Draw "YOU WIN" text
            font = pygame.font.Font(None, 74)
            text = font.render('YOU WIN!', True, (0, 255, 0))
            text_rect = text.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
            screen.blit(text, text_rect)
            
            # Show moves
            small_font = pygame.font.Font(None, 36)
            moves_text = small_font.render(f'Moves: {game_logic.moves}', True, (255, 255, 255))
            moves_rect = moves_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2 + 50))
            screen.blit(moves_text, moves_rect)
            
            pygame.display.flip()
            
            # Wait before continuing
            pygame.time.wait(2000)
            return 'win'

        # Draw everything
        screen.fill((0, 0, 0))
        
        # Draw tiles first (background)
        tile_grid.draw(screen, 0, 0, animation_time)
        
        # Draw lava on top of tiles
        game_logic.lava.draw(screen, 0, 0, animation_time)
        
        # Draw player on top
        game_logic.player.draw(screen, 0, 0)
        
        # Draw UI info
        font = pygame.font.Font(None, 24)
        info_text = (f'Level {level_num}/{total_levels} | '
                    f'Moves: {game_logic.moves} | '
                    f'Lava: {game_logic.lava.count()} | '
                    f'R: Reset | U: Undo | WASD/Arrows: Move')
        text = font.render(info_text, True, (255, 255, 255))
        
        # Draw text background for readability
        text_bg = pygame.Surface((text.get_width() + 10, text.get_height() + 4))
        text_bg.set_alpha(180)
        text_bg.fill((0, 0, 0))
        screen.blit(text_bg, (5, 5))
        screen.blit(text, (10, 7))
        
        pygame.display.flip()
        clock.tick(60)
    
    return 'quit'


def main():
    """Main game loop."""
    print("🎮 Lava & Aqua")
    print("=" * 40)
    print("Controls:")
    print("  WASD or Arrow Keys - Move")
    print("  R - Reset level")
    print("  U/Z - Undo last move")
    print("  ESC - Quit")
    print("=" * 40)
    
    # Initialize game logic
    try:
        game_logic = GameLogic()
        total_levels = game_logic.get_total_levels()
        print(f"\n📦 Loaded {total_levels} levels")
    except Exception as e:
        print(f"❌ Error loading game: {e}")
        import traceback
        traceback.print_exc()
        return
    
    while not game_logic.is_last_level() or not game_logic.level_complete:
        current_level = game_logic.get_level_number()
        level_name = game_logic.get_level_name()
        
        try:
            print(f"\n🔥 Level {current_level}/{total_levels}: {level_name}")
            
            result = run_level(game_logic)
            
            if result == 'quit':
                break
            elif result == 'win':
                if game_logic.is_last_level():
                    print("\n" + "=" * 40)
                    print("🎉 CONGRATULATIONS!")
                    print("You beat all levels!")
                    print("=" * 40)
                    break
                else:
                    if not game_logic.next_level():
                        print("No more levels!")
                        break
            elif result == 'restart':
                game_logic.reset_level()
                print(f"💀 Restarting level {current_level}: {level_name}")
                
        except Exception as e:
            print(f"❌ Error running level: {e}")
            import traceback
            traceback.print_exc()
            break
    
    print("\nThanks for playing! 👋")
    pygame.quit()


if __name__ == '__main__':
    main()