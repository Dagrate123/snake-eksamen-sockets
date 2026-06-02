import socket
import threading
import struct
import json
import time

Clients = [] #array der alle klienter blir lagt til 
Players = {}

def recv_exact(conn, length):
    data = b""
    while len(data) < length:
        packet = conn.recv(length - len(data))
        if not packet:
            return None
        data += packet
    return data

def handle_clients(conn, addr): #når klienten stopper å sende info så disconnecter klienten
    print("client connected", addr)
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
            print("RAW DATA:", message)
            if message["command"] == "move":
                direction = message["dir"]
                Players[conn]["dir"] = direction
            if not message:
                break
        except:
            break

    print("client disconnected")
    del Players[conn]
    Clients.remove(conn)
    conn.close()

def get_state():
    return {
        str(id(conn)): data
        for conn, data in Players.items()
    }

def broadcast():
    state = json.dumps(get_state()).encode()
    header = struct.pack("!I", len(state))

    for c in Clients:
        try:
            c.sendall(header + state)
        except:
            pass

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 5555))
server.listen()

print("server running")

while True:
    conn, addr = server.accept()
    Clients.append(conn)
    Players[conn] = {
        "x": 5,
        "y": 5,
        "dir": "RIGHT",
        "Alive": True
    }
    threading.Thread(target=handle_clients, args=(conn, addr)).start()

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

        broadcast()
        time.sleep(0.2)
threading.Thread(target=game_loop, daemon=True).start()