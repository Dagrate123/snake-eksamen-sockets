import socket
import json
import struct
import pygame
import random
import threading

game_state = {}

def receive():
    global game_state

    while True:
        try:
            header = Client.recv(4)
            if not header:
                break

            length = struct.unpack('!I', header)[0]
            data = client.recv(length)

            game_state = json.loads(data.decode())

            print("STATE:", game_state) 

        except:
            break 

pygame.init()

Client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
Client.connect(("127.0.0.1", 5555))
threading.Thread(target=receive, daemon=True).start()

data = {"user_id": 1337, "command": "auth", "token": "abcde123"}

data_bytes = json.dumps(data).encode('utf-8')

header = struct.pack('!I', len(data_bytes))

Client.sendall(header + data_bytes)
print("data sent")

screen_width = 800
screen_height = 600

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Snake Game")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.image = pygame.Surface((20, 20))
        self.image.fill((0, 255, 0))

        self.rect = self.image.get_rect()
        self.rect.center = (screen_width // 2, screen_height // 2)

        self.speed = 20
        self.dx = self.speed
        self.dy = 0

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy


class Apple(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.image = pygame.Surface((20, 20))
        self.image.fill((255, 0, 0))

        self.rect = self.image.get_rect()
        self.randomize_position()

    def randomize_position(self):
        self.rect.x = random.randint(0, screen_width - 20)
        self.rect.y = random.randint(0, screen_height - 20)


player = Player()
apple = Apple()

all_sprites = pygame.sprite.Group()
all_sprites.add(player, apple)

snake_body = []
score = 0

running = True

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_LEFT and player.dx == 0:
                player.dx = -player.speed
                player.dy = 0
                data = {"command": "move", "dir": "LEFT"}
                data_bytes = json.dumps(data).encode('utf-8')
                header = struct.pack('!I', len(data_bytes))
                Client.sendall(header + data_bytes)
                print("data sent")

            elif event.key == pygame.K_RIGHT and player.dx == 0:
                player.dx = player.speed
                player.dy = 0
                data = {"command": "move", "dir": "RIGHT"}
                data_bytes = json.dumps(data).encode('utf-8')
                header = struct.pack('!I', len(data_bytes))
                Client.sendall(header + data_bytes)
                print("data sent")

            elif event.key == pygame.K_UP and player.dy == 0:
                player.dx = 0
                player.dy = -player.speed
                data = {"command": "move", "dir": "UP"}
                data_bytes = json.dumps(data).encode('utf-8')
                header = struct.pack('!I', len(data_bytes))
                Client.sendall(header + data_bytes)
                print("data sent")


            elif event.key == pygame.K_DOWN and player.dy == 0:
                player.dx = 0
                player.dy = player.speed
                data = {"command": "move", "dir": "DOWN"}
                data_bytes = json.dumps(data).encode('utf-8')
                header = struct.pack('!I', len(data_bytes))
                Client.sendall(header + data_bytes)
                print("data sent")


    if player.rect.colliderect(apple.rect):
        apple.randomize_position()
        snake_body.append(player.rect.copy())
        score += 1

    for i in range(len(snake_body) - 1, 0, -1):
        snake_body[i].x = snake_body[i - 1].x
        snake_body[i].y = snake_body[i - 1].y

    if len(snake_body) > 0:
        snake_body[0].x = player.rect.x
        snake_body[0].y = player.rect.y

    player.update()

    if (
        player.rect.x < 0 or
        player.rect.x >= screen_width or
        player.rect.y < 0 or
        player.rect.y >= screen_height
    ):
        running = False

    screen.fill((255, 255, 255))

    all_sprites.draw(screen)

    for segment in snake_body:
        pygame.draw.rect(screen, (0, 200, 0), segment)

    screen.blit(font.render(f"Score: {score}", True, (0, 0, 0)), (10, 10))

    pygame.display.flip()
    clock.tick(10)

pygame.quit()
Client.close()