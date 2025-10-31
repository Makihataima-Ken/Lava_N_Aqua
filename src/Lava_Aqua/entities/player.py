class Player:
    def __init__(self, x,y):
        self.x = x
        self.y = y
    def move(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy
        
        if grid[new_y][new_x] != '#':  # not wall
            self.x = new_x
            self.y = new_y
        