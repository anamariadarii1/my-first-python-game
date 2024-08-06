import pygame
import random
import sys
import time

# Initialize Pygame
pygame.init()
myVector = pygame.math.Vector2

# Window dimensions and other constants
HEIGHT = 440
WIDTH = 400
ACC = 0.5  # Acceleration
FRIC = -0.12  # Friction
FPS = 60  # Frames per second

# Create a Clock object to control the frame rate
FramePerSec = pygame.time.Clock()
displaySurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platformer")
background = pygame.image.load("background.png")
background = pygame.transform.scale(background, (860, 480))

# Player class defines the player character
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.transform.scale(pygame.image.load("player.png"), (40, 40))
        self.rect = self.surf.get_rect(center=(10, 420))

        self.pos = myVector((10, 385))
        self.vel = myVector(0, 0)
        self.acc = myVector(0, 0)

        self.jumping = False
        self.score = 0

    # The move function controls the player's movement
    def move(self):
        self.acc = myVector(0, 0.5)  # Gravity

        # Check for key presses
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_LEFT]:
            self.acc.x = -ACC
        if pressed_keys[pygame.K_RIGHT]:
            self.acc.x = ACC

        # Apply friction
        self.acc.x += self.vel.x * FRIC

        # Equations of motion
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        # Wrap around the screen
        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH

        self.rect.midbottom = self.pos

    # The update function checks for collisions with platforms
    def update(self):
        hits = pygame.sprite.spritecollide(P1, platforms, False)
        if hits and P1.vel.y > 0:
            self.pos.y = hits[0].rect.top + 1
            self.vel.y = 0
            self.jumping = False

    # The jump function allows the player to jump if on a platform
    def jump(self):
        hits = pygame.sprite.spritecollide(P1, platforms, False)
        if hits and not self.jumping:
            self.jumping = True
            self.vel.y = -15

    # The cancel_jump function stops the jump if the space bar is released early
    def cancel_jump(self):
        if self.jumping:
            if self.vel.y < -3:
                self.vel.y = -3

# Platform class defines the platforms
class Platform(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # Load and scale the platform image
        self.surf = pygame.transform.scale(pygame.image.load("platform.png"), (random.randint(50, 120), 18))
        self.rect = self.surf.get_rect(center=(random.randint(0, WIDTH - 10),
                                               random.randint(0, HEIGHT - 10)))
        self.speed = random.randint(-1, 1)
        self.moving = True

    # The move function moves the platform and the player if they are on it
    def move(self):
        hits = self.rect.colliderect(P1.rect)
        if self.moving:
            self.rect.move_ip(self.speed, 0)
            if hits:
                P1.pos += (self.speed, 0)
            if self.speed > 0 and self.rect.left > WIDTH:
                self.rect.right = 0
            if self.speed < 0 and self.rect.left < 0:
                self.rect.left = WIDTH

    # The generateCoin function generates a coin on stationary platforms
    def generateCoin(self):
        if self.speed == 0:
            coins.add(Coin((self.rect.centerx, self.rect.centery - 30)))

# Coin class defines the coins
class Coin(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()

        # Load and scale the coin image
        self.image = pygame.transform.scale(pygame.image.load("coin.png"), (20, 20))
        self.rect = self.image.get_rect()

        self.rect.topleft = pos

    # The update function checks for collisions with the player and increases the score
    def update(self):
        if self.rect.colliderect(P1.rect):
            P1.score += 5
            self.kill()

# Function to generate new platforms
def platform_generator():
    while len(platforms) < 7:
        width = random.randrange(50, 100)
        p = Platform()
        c = True
        while c:
            p = Platform()
            p.rect.center = (random.randrange(0, WIDTH - width), random.randrange(-50, 0))
            c = check(p, platforms)
        p.generateCoin()
        platforms.add(p)
        all_sprites.add(p)

# Function to check for platform collisions
def check(platform, groupies):
    if pygame.sprite.spritecollideany(platform, groupies):
        return True
    else:
        for new_plat in groupies:
            if new_plat == platform:
                continue
            # Ensure platforms are not too close to each other
            if (abs(platform.rect.top - new_plat.rect.bottom) < 40)\
                    and (abs(platform.rect.bottom - new_plat.rect.top) < 40):
                return True

# Initialize the first platform and player
PT1 = Platform()
PT1.surf = pygame.Surface((WIDTH, 20))
PT1.surf.fill((255, 0, 0))
PT1.rect = PT1.surf.get_rect(center=(WIDTH / 2, HEIGHT - 10))
PT1.moving = False
P1 = Player()

# Create groups for sprites, coins, and platforms
all_sprites = pygame.sprite.Group()
all_sprites.add(PT1)
all_sprites.add(P1)
coins = pygame.sprite.Group()

platforms = pygame.sprite.Group()
platforms.add(PT1)

# Generate initial platforms
for x in range(random.randint(5, 6)):
    C = True
    pl = Platform()
    while C:
        pl = Platform()
        C = check(pl, platforms)
    pl.generateCoin()
    platforms.add(pl)
    all_sprites.add(pl)

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                P1.jump()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                P1.cancel_jump()

    # Blit the background image
    displaySurface.blit(background, (-50, 0))

    # Display the score
    f = pygame.font.SysFont("Verdana", 20)
    g = f.render(str(P1.score), True, (0, 0, 0))
    displaySurface.blit(g, (WIDTH / 2, 10))

    # Check if the player has fallen off the screen
    if P1.rect.top > HEIGHT:
        for entity in all_sprites:
            entity.kill()
            time.sleep(1)
            displaySurface.fill((255, 0, 0))
            pygame.display.update()
            time.sleep(1)
            pygame.quit()
            sys.exit()

    # Scroll the screen up if the player reaches the top third
    if P1.rect.top <= HEIGHT / 3:
        P1.pos.y += abs(P1.vel.y)
        for plat in platforms:
            plat.rect.y += abs(P1.vel.y)
            if plat.rect.top >= HEIGHT:
                P1.score += 1
                plat.kill()
        for coin in coins:
            coin.rect.y += abs(P1.vel.y)
            if coin.rect.top >= HEIGHT:
                coin.kill()

    # Update and draw all sprites
    P1.update()
    platform_generator()
    for entity in all_sprites:
        displaySurface.blit(entity.surf, entity.rect)
        entity.move()

    # Update and draw all coins
    for coin in coins:
        displaySurface.blit(coin.image, coin.rect)
        coin.update()

    # Update the display and tick the clock
    pygame.display.update()
    FramePerSec.tick(FPS)
