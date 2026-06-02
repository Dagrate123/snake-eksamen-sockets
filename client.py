import socket
import json
import struct
import pygame
import threading
import random

game_state = {}

def recv_exact(sock, length):
    data = b""
    while len(data) < length:
        packet = sock.recv(length - len(data))
        if not packet:
            return None
        data += packet
    return data


def receive():
    global game_state

    while True:
        try:
            header = recv_exact(Client, 4)
            if not header:
                break

            length = struct.unpack('!I', header)[0]
            data = recv_exact(Client, length)

            game_state = json.loads(data.decode())

            print("STATE:", game_state)

        except Exception as e:
            print("recv error:", e)
            break


pygame.init()

Client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
Client.connect(("127.0.0.1", 5555))

threading.Thread(target=receive, daemon=True).start()


screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                msg = {"command": "move", "dir": "LEFT"}
            elif event.key == pygame.K_RIGHT:
                msg = {"command": "move", "dir": "RIGHT"}
            elif event.key == pygame.K_UP:
                msg = {"command": "move", "dir": "UP"}
            elif event.key == pygame.K_DOWN:
                msg = {"command": "move", "dir": "DOWN"}
            else:
                continue

            data = json.dumps(msg).encode()
            header = struct.pack("!I", len(data))
            Client.sendall(header + data)

    screen.fill((255, 255, 255))

    for pid, p in game_state.items():
        pygame.draw.rect(
            screen,
            (0, 255, 0),
            pygame.Rect(p["x"], p["y"], 20, 20)
        )

    pygame.display.flip()
    clock.tick(10)