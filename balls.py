import pygame
import numpy as np
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 1200
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Gravity Simulation")

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
dark_grey = (40, 50, 45)
green = (30, 250, 70)
red = (250, 40, 50)

# Create objects
objects = []
indicator = 0

# Kick speed
charge_time = 0

# Define a class for objects
class Ball:
    def __init__(self, x, y, radius, color, mass):
        self.name = 'ball'
        self.x = x
        self.y = y
        self.center = (self.x, self.y)
        self.radius = radius
        self.color = color
        self.mass = mass
        self.coll_coeff = (1-self.mass*0.05)
        self.vel_x = 0
        self.vel_y = 0


    def apply_gravity(self):
        # Earth's gravity: constant acceleration downward
        gravity_acceleration = 0.1
        self.vel_y += gravity_acceleration


    def apply_friction(self):
        friction_coefficient = 0.999  # Adjust the value to control friction strength
        self.vel_x *= friction_coefficient


    def kick(self, speed, direction):
        if direction == 'up':
            self.vel_y -= speed
        elif direction == 'left':
            self.vel_x -= speed
        elif direction == 'right':
            self.vel_x += speed
        else:
            self.vel_y += speed


    def check_collision_with_walls(self):
        # Collision with left wall
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vel_x = -self.vel_x * (1-self.mass*0.05)  # Reverse horizontal velocity with bounce effect

        # Collision with right wall
        if self.x + self.radius > screen_width:
            self.x = screen_width - self.radius
            self.vel_x = -self.vel_x * (1-self.mass*0.05)  # Reverse horizontal velocity with bounce effect

    
    def check_collision_with_ground(self):
        # Update position and velocity based on collision with the "earth surface"
        if screen_height + 2*self.radius >= self.y + self.radius >= screen_height:
            self.y = screen_height - self.radius
            self.vel_y = -self.vel_y * self.coll_coeff  # Reverse velocity with some loss due to collision
            # self.coll_coeff = self.coll_coeff - 0.02 if self.coll_coeff > 0.02 else 0


    def update(self, floor_val: bool=True):
        self.apply_gravity()
        self.check_collision_with_walls()
        self.apply_friction()
        if floor_val is True:
            self.check_collision_with_ground()
        self.x += self.vel_x
        self.y += self.vel_y

        self.center = self.x, self.y


    def draw(self):
        try:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        except OverflowError:
            None
        except TypeError:
            None


    def check_collision(self, other):
        # Calculate distance between object centers
        dx = self.x - other.x
        dy = self.y - other.y
        distance = dist(self.center, other.center)

        if other.name == 'ball':
            # Collision occurs if distance is smaller than sum of radii
            if distance < self.radius + other.radius:
                # Simple resolution: Adjust position
                overlap = (self.radius + other.radius) - distance + 1
                angle = np.arctan2(dy, dx)
                self.vel_x +=  overlap * np.cos(angle) / (2*self.mass) 
                self.vel_y +=  overlap * np.sin(angle) / (2*self.mass)
                other.vel_x -= overlap * np.cos(angle) / (2*other.mass)
                other.vel_y -= overlap * np.sin(angle) / (2*other.mass)
                

class Platform:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.vel_x = 0

    def update(self):
        self.x += self.vel_x
        self.x = max(0, min(self.x, screen_width - self.width))

    
    def check_collision(self, other):

        left_corner, right_corner = (self.x, self.y), (self.x + self.width, self.y)
        
        # Check collision with left and right sides of the platform
        if other.name == 'ball':
            left_dist = dist(left_corner, other.center)
            right_dist = dist(right_corner, other.center)
            ball_dist = min(left_dist, right_dist)
            if self.y <= other.y + other.radius <= self.y + self.height and self.x <= other.x <= self.x + self.width:
                other.y = self.y - other.radius
                other.vel_y = -other.vel_y * (1 - other.mass * 0.05)
            if ball_dist < other.radius:
                dx = left_corner[0] - other.x if self.x > other.x else right_corner[0] - other.x
                dy = self.y - other.y
                overlap = other.radius - ball_dist + 1
                angle = np.arctan2(dy, dx)
                other.vel_x -= overlap * np.cos(angle) / (2*other.mass)
                other.vel_y -= overlap * np.sin(angle) / (2*other.mass)


    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))


def dist(x, y):
    return np.sqrt((y[0] - x[0])**2 + (y[1] - x[1])**2 )


# Create a line (drawn by the user) as an object
def create_ball(start_pos, end_pos):
    r = dist(start_pos, end_pos)
    mass = r/15
    obj = Ball(start_pos[0], start_pos[1], r, black, mass)
    obj.x_velocity = (end_pos[0] - start_pos[0]) / 10  # Adjust velocity based on user's drawing speed
    obj.y_velocity = 0  # No initial vertical velocity for the drawn line
    objects.append(obj)


# Mouse drawing variables
drawing = False
floor = True
# Create the platform
platform = Platform(screen_width // 2 - 50, screen_height - 20, 100, 10, red)

# Game loop
clock = pygame.time.Clock()
FPS = 60
def game_loop():
    global drawing, indicator, objects, floor
    
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                drawing = True
                line_start = event.pos
            if event.type == pygame.MOUSEBUTTONUP:
                if drawing:
                    drawing = False
                    create_ball(line_start, event.pos)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    floor = not floor
                if event.key == pygame.K_a:
                    platform.vel_x = -10
                if event.key == pygame.K_d:
                    platform.vel_x = 10
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN or event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    charge_time = pygame.time.get_ticks()
                if event.key == pygame.K_SPACE:
                    curr_ball = objects[indicator] if objects else None
                    if curr_ball is not None:
                        curr_ball.color = black
                    indicator += 1

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a or event.key == pygame.K_d:
                    platform.vel_x = 0
                if event.key == pygame.K_DOWN or event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT or event.key == pygame.K_UP:
                    ball = objects[indicator % len(objects)] if objects else None
                    charge = (pygame.time.get_ticks() - charge_time)/FPS
                    direction = pygame.key.name(event.key)
                    if ball is not None:
                        ball.kick(charge, direction)
                    charge_time = 0

        # Clear the screen
        screen.fill(white)

        # Draw the line being drawn by the user
        if drawing:
            pygame.draw.line(screen, black, line_start, pygame.mouse.get_pos(), 2)

        # Update and draw platform
        platform.update()
        platform.draw()
        
        # Update and draw objects
        for obj in objects:
            obj.update(floor_val=floor)
            platform.check_collision(obj)  # Check collision with platform
            for other_obj in objects:
                if obj != other_obj:
                    obj.check_collision(other_obj)

            # Check if a ball has fallen below the ground
            if obj.name == 'ball' and obj.y > screen_height + obj.radius:
                # Remove the ball from the list of objects
                objects.remove(obj)

            obj.draw()
        
        indicator = indicator % len(objects) if objects else 0
        chosen_ball = objects[indicator] if objects else None
        if chosen_ball is not None:
            chosen_ball.color = green
            chosen_ball.draw()


        pygame.display.flip()
        clock.tick(FPS)  # Cap the frame rate
    
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    game_loop()