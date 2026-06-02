import socket
import threading
import struct
import json
import time

Clients = []
Players = {}
ConnToID = {}

def recv_exact(conn, length):
    data = b""
    while len(data) < length:
        packet = conn.recv(length - len(data))
        if not packet:
            return None
        data += packet
    return data


def handle_clients(conn, addr):
    print("client connected", addr)

    player_id = str(addr)
    ConnToID[conn] = player_id

    Players[player_id] = {
        "x": 100,
        "y": 100,
        "dir": "RIGHT",
        "Alive": True
    }

    while True:
        try:
            header = recv_exact(conn, 4)
            if not header:
                break

            length = struct.unpack("!I", header)[0]
            raw = recv_exact(conn, length)
            if raw is None:
                break

            message = json.loads(raw.decode())

            if message["command"] == "move":
                Players[player_id]["dir"] = message["dir"]

        except:
            break

    print("client disconnected")
    Clients.remove(conn)
    del Players[player_id]
    conn.close()


def game_loop():
    while True:
        for player in Players.values():
            if player["dir"] == "UP":
                player["y"] -= 20
            elif player["dir"] == "DOWN":
                player["y"] += 20
            elif player["dir"] == "LEFT":
                player["x"] -= 20
            elif player["dir"] == "RIGHT":
                player["x"] += 20

        state = json.dumps(Players).encode()
        header = struct.pack("!I", len(state))

        for c in Clients:
            try:
                c.sendall(header + state)
            except:
                pass

        time.sleep(0.2)


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 5555))
server.listen()

print("server running")

threading.Thread(target=game_loop, daemon=True).start()

while True:
    conn, addr = server.accept()
    Clients.append(conn)
    threading.Thread(target=handle_clients, args=(conn, addr)).start()