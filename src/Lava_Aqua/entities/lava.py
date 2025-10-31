class Lava:
    def __init__(self, start_positions):
        self.positions = start_positions  # List of (x, y) tuples
        
    def update(self, grid):
        # example: spread to adjacent floor tiles each move of player
        new_positions = set(self.positions)
        for (x, y) in self.positions:
            for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                nx, ny = x+dx, y+dy
                if (0 <= ny < len(grid) and 0 <= nx < len(grid[0])):
                    if grid[ny][nx] == ' ' or grid[ny][nx] == '.':
                        new_positions.add((nx, ny))
        self.positions = new_positions