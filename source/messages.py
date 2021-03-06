import socket
def send_message(event,client):
    client.sendall(bytes(event,"utf-8"))

def parse_message(message,game_data):
    message = message.decode("utf-8")
    if "move " in message:
        message = message.replace("move ","")
        if "y" in message:
            message = message.replace("y ","")
            player_id = int(message.split(" ")[0])
            val = int(message.split(" ")[1])
            game_data["players"][player_id]["y"]+=val
        else:
            player_id = int(message.split(" ")[0])
            val = int(message.split(" ")[1])
            game_data["players"][player_id]["x"]+=val
    if "shoot " in message:
        message = message.replace("shoot ","")
        player_id = int(message.split(" ")[0])
        val = (message.split(" ")[1])
        x = val.split(",")[0]
        y = val.split(",")[1]
        game_data["players"][player_id]["bullets"][len(game_data["players"][player_id]["bullets"])+1] = \
            [game_data["players"][player_id]["x"],game_data["players"][player_id]["y"],(x,y)]
    return game_data