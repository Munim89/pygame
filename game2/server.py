import pickle
from game import game

server = "192.168.0.102"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(2)
print("Waiting for connection, Server has started")

connected = set()
games = {}
id_count = 0

def threaded_client(conn, p, game_id):
    global id_count
    conn.send(str.encode(str(p)))

    reply = ""
    while True:
        try:
            data = conn.recv(4096).decode()

            if game_id in games:
                game = games[game_id]

                if not data:
                    break
                else:
                    if data == "reset":
                        game.reset()
                    elif data != "get":
                        game.play(p, data)

                    conn.sendall(pickle.dumps(game))
            else:
                break
        except:
            break

    print("Lost Connection")
    try:
        del games[game_id]
        print("Closing Game:", game_id)
    except:
        pass
    id_count -= 1
    conn.close()

while True:
    conn, addr = s.accept()
    print("Connected to", addr)
    id_count += 1
    game_id = (id_count - 1)//2
    if game_id % 2 == 1:
        # So the game id is now a new game
        games[game_id]  = game(game_id)
        print("Creating a new game")
    else:
        # The game launches
        games[game_id].ready = True
        p = 1

    start_new_thread(threaded_client, (conn, p, game_id))
