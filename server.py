import socket
import threading
import struct
import json
import time
import random

Clients = []
Players = {}
ConnToID = {}

APPLE = { #randomizer apple spawn poinnt 
    "x": random.randint(0, 39) * 20,
    "y": random.randint(0, 29) * 20
}


def recv_exact(conn, length): #recieve korrekt mengde data 
    data = b""
    while len(data) < length:
        packet = conn.recv(length - len(data))
        if not packet:
            return None
        data += packet
    return data


def spawn_apple():
    return {
        "x": random.randint(0, 39) * 20,
        "y": random.randint(0, 29) * 20
    }


def handle_clients(conn, addr):
    print("client connected", addr)

    player_id = str(addr)
    ConnToID[conn] = player_id

    Players[player_id] = { #spawnposition 
        "x": 100,
        "y": 100,
        "dir": "RIGHT",
        "Alive": True,
        "body": []
    }

    while True: #reciever dataen om hvilken vei hver player skal bevege seg og hvis spilleren stopper å sende data til loopen så disconnecter spilleren
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
    global APPLE

    while True:
        for player_id, player in Players.items():
            old_x, old_y = player["x"], player["y"]

            if player["dir"] == "UP":
                player["y"] -= 20
            elif player["dir"] == "DOWN":
                player["y"] += 20
            elif player["dir"] == "LEFT":
                player["x"] -= 20
            elif player["dir"] == "RIGHT":
                player["x"] += 20

            body = player["body"]
            body.insert(0, {"x": old_x, "y": old_y})

            ate = False
            if player["x"] == APPLE["x"] and player["y"] == APPLE["y"]:
                print(f"spiller {player_id} har spist eple")
                APPLE = spawn_apple()
                ate = True


            if not ate:
                body.pop()

            for other_id, other in Players.items():
                if other_id == player_id:
                    continue

            for segment in other["body"]:
                if player["x"] == segment["x"] and player["y"] == segment["y"]:
                    print(f"spiller {player_id} traff spiller {other_id}'s kropp")
                    break

            if player["x"] >= 800 or player["x"] <= 0:
                print("death")
            if player["y"] >= 600 or player["y"] <= 0:
                print("death")

        state = {
            "players": Players,
            "apple": APPLE
        }

        data = json.dumps(state).encode()
        header = struct.pack("!I", len(data))

        for c in Clients:
            try:
                c.sendall(header + data)
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
    threading.Thread(target=handle_clients, args=(conn, addr), daemon=True).start()