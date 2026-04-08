import pygame
import random
import sys

# --- Configuration ---
GRID_SIZE = 10
CELL_SIZE = 60
MARGIN = 2
WINDOW_SIZE = GRID_SIZE * (CELL_SIZE + MARGIN) + MARGIN
FPS = 60

# Colors (Dark Theme)
COLOR_BG = (10, 10, 15)
COLOR_GRID = (30, 30, 40)
COLOR_AGENT = (96, 165, 250)      # Blue
COLOR_DELIVERY = (245, 158, 11)   # Amber
COLOR_OBSTACLE = (239, 68, 68)    # Red
COLOR_COMPLETED = (16, 185, 129)  # Emerald
COLOR_TEXT = (244, 244, 245)

class DeliveryGame:
    def __init__(self):
        self.level = "easy"
        self.reset()

    def reset(self):
        self.agent_pos = [0, 0]
        self.deliveries = []
        self.completed = []
        self.obstacles = []
        self.steps = 0
        self.total_reward = 0
        self.last_reward = 0
        
        occupied = set()
        occupied.add((0, 0))

        # Level counts
        counts = {
            "easy": {"d": 2, "o": 3},
            "medium": {"d": 5, "o": 8},
            "hard": {"d": 8, "o": 15}
        }
        c = counts[self.level]

        # Generate Obstacles
        while len(self.obstacles) < c["o"]:
            pos = (random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1))
            if pos not in occupied:
                self.obstacles.append(list(pos))
                occupied.add(pos)

        # Generate Deliveries
        while len(self.deliveries) < c["d"]:
            pos = (random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1))
            if pos not in occupied:
                self.deliveries.append(list(pos))
                occupied.add(pos)

    def recover_deliveries(self):
        self.total_reward += 20  # Wave bonus
        counts = {"easy": 2, "medium": 5, "hard": 8}
        count = counts[self.level]
        
        occupied = set()
        occupied.add(tuple(self.agent_pos))
        for o in self.obstacles: occupied.add(tuple(o))
        
        while len(self.deliveries) < count:
            pos = (random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1))
            if pos not in occupied:
                self.deliveries.append(list(pos))
                occupied.add(pos)

    def move(self, dx, dy):
        new_x = max(0, min(GRID_SIZE - 1, self.agent_pos[0] + dx))
        new_y = max(0, min(GRID_SIZE - 1, self.agent_pos[1] + dy))
        
        self.agent_pos = [new_x, new_y]
        self.steps += 1
        self.last_reward = -1
        
        # Check collision
        if self.agent_pos in self.obstacles:
            self.reset()
            return

        self.total_reward += self.last_reward

    def deliver(self):
        self.steps += 1
        if self.agent_pos in self.deliveries:
            self.deliveries.remove(self.agent_pos)
            self.completed.append(list(self.agent_pos))
            self.last_reward = 10
            
            if not self.deliveries:
                self.recover_deliveries()
        else:
            self.last_reward = -5
            
        self.total_reward += self.last_reward

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + 100))
    pygame.display.set_caption("Delivery Dash RL - Desktop")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 16, bold=True)
    
    game = DeliveryGame()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:    game.move(0, -1)
                if event.key == pygame.K_DOWN:  game.move(0, 1)
                if event.key == pygame.K_LEFT:  game.move(-1, 0)
                if event.key == pygame.K_RIGHT: game.move(1, 0)
                if event.key == pygame.K_SPACE: game.deliver()
                if event.key == pygame.K_r:     game.reset()
                
                # Level switching
                if event.key == pygame.K_1: game.level = "easy"; game.reset()
                if event.key == pygame.K_2: game.level = "medium"; game.reset()
                if event.key == pygame.K_3: game.level = "hard"; game.reset()

        # Draw Background
        screen.fill(COLOR_BG)

        # Draw Grid
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                rect = pygame.Rect(
                    MARGIN + col * (CELL_SIZE + MARGIN),
                    MARGIN + row * (CELL_SIZE + MARGIN),
                    CELL_SIZE,
                    CELL_SIZE
                )
                pygame.draw.rect(screen, COLOR_GRID, rect)
                
                # Draw Entities
                pos = [col, row]
                if pos == game.agent_pos:
                    pygame.draw.rect(screen, COLOR_AGENT, rect.inflate(-10, -10), border_radius=8)
                elif pos in game.deliveries:
                    pygame.draw.circle(screen, COLOR_DELIVERY, rect.center, CELL_SIZE // 3)
                elif pos in game.obstacles:
                    # Draw a triangle for obstacles
                    pts = [
                        (rect.centerx, rect.top + 10),
                        (rect.left + 10, rect.bottom - 10),
                        (rect.right - 10, rect.bottom - 10)
                    ]
                    pygame.draw.polygon(screen, COLOR_OBSTACLE, pts)
                elif pos in game.completed:
                    pygame.draw.rect(screen, (COLOR_COMPLETED[0], COLOR_COMPLETED[1], COLOR_COMPLETED[2], 50), rect.inflate(-20, -20), 2)

        # Draw Dashboard
        dash_y = WINDOW_SIZE + 10
        stats = [
            f"REWARD: {game.total_reward}",
            f"STEPS: {game.steps}",
            f"LEVEL: {game.level.upper()} (1-3 to change)",
            f"LAST: {game.last_reward}"
        ]
        
        for i, text in enumerate(stats):
            surf = font.render(text, True, COLOR_TEXT)
            screen.blit(surf, (20, dash_y + i * 20))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
