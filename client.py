import socket
import json
import struct
import pygame
import threading

game_state = { #dictionarys som sender game_state til serveren
    "players": {},
    "apple": None
}


def recv_exact(sock, length): #receive riktig mengde data 
    data = b""
    while len(data) < length:
        packet = sock.recv(length - len(data))
        if not packet:
            return None
        data += packet
    return data


def receive(): #unpacker dataen 
    global game_state

    while True:
        try:
            header = recv_exact(Client, 4)
            if not header:
                break

            length = struct.unpack('!I', header)[0]
            data = recv_exact(Client, length)

            game_state = json.loads(data.decode())

        except Exception as e:
            print("recv error:", e)
            break


pygame.init()

Client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #vi bruker ipv4 sockets og tcp sockets
Client.connect(("192.168.20.74", 5555))

threading.Thread(target=receive, daemon=True).start()

screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

        if event.type == pygame.KEYDOWN: #endrer retning basert på hvilken key og pakker dataen til serveren
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

    players = game_state.get("players", {})
    apple = game_state.get("apple", None)

    for pid, p in players.items():
        pygame.draw.rect(
            screen,
            (0, 255, 0),
            pygame.Rect(p["x"], p["y"], 20, 20)
        )

    if apple:
        pygame.draw.rect(
            screen,
            (255, 0, 0),
            pygame.Rect(apple["x"], apple["y"], 20, 20)
        )

    pygame.display.flip()
    clock.tick(10)