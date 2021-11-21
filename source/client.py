# imports
import socket
import pygame
import threading
import json
import messages

WIDTH = 1000
HEIGHT = 700

#constants
WIDTH = 1000
HEIGHT = 700

#setup connection with server
server_address=("localhost", 6789)
max_size=10000
client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(server_address)
#data=client.recv(max_size)

# game variables
game_state = 1
gamedata_string = str(client.recv(max_size), "utf-8")
game_data = json.loads(gamedata_string)
print(game_data)

# setup window
pygame.init()
window = pygame.display.set_mode((WIDTH,HEIGHT))
clock = pygame.time.Clock()

#NOTE: change title later
pygame.display.set_caption("Collaboration Game")

player_id = int(client.recv(28).decode())

players = [pygame.transform.scale(pygame.image.load(game_data["players"][0]["image"]),(75,75)),
            pygame.transform.scale(pygame.image.load(game_data["players"][1]["image"]),(75,75))]

bg_img = pygame.transform.scale(pygame.image.load('assets/backgrounds/bg1.png'),(WIDTH,HEIGHT))

def display_bg():
    window.fill((0,0,0))
    window.blit(bg_img,(0,0))
    return 1

player1_animation = "idle"
player2_animation = "idle"
player1_animation_state = 0
player2_animation_state = 0
player1_animation_direction = 1
player2_animation_direction = 1
animation_counter = 0

def display_players():
    if player1_animation == "idle":
        offset = 0
    p1 = pygame.Surface((75, 75))
    p1.set_colorkey((0,0,0))
    p1.blit(players[1], (0, 0), ((player2_animation_state + offset) * 75, 0, 75, 75))
    p0 = pygame.Surface((75, 75))
    p0.set_colorkey((0,0,0))
    p0.blit(players[0], (0, 0), ((player1_animation_state + offset) * 75, 0, 75, 75))
    if player_id == 0:
        window.blit(p1,(int(game_data["players"][1]["x"]),int(game_data["players"][1]["y"])))
        window.blit(p0,(int(game_data["players"][0]["x"]),int(game_data["players"][0]["y"])))
    else:
        window.blit(p0,(int(game_data["players"][0]["x"]),int(game_data["players"][0]["y"])))
        window.blit(p1,(int(game_data["players"][1]["x"]),int(game_data["players"][1]["y"])))

def listen_to_server(client):
    global game_data
    global game_state
    while game_state:
        msg = client.recv(max_size)
        if(str(msg,"utf-8") == "quit"):
            print("quit")
            game_state = 0
        game_data = messages.parse_message(msg,game_data)
        # print(f'recieved message {str(msg,"utf-8")}')

def simplify_vector(vector):
    x = vector[0]
    y = vector[1]
    done = False
    vector_counter = 0
    while done == False:
        vector_counter = 0
        for x in range(8):
            i = x+2
            if x % i == 0 and y % i == 0:
                x = x/i
                y = y/i
            else:
                vector_counter += 1
        if vector_counter == 8:
            done = True

server_listener = threading.Thread(target=lambda:listen_to_server(client))
server_listener.start()

shoot_counter = 0

move_speed = 5

while game_state != 0:
    clock.tick(60)
    if game_state == 1: # main game loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                messages.send_message("quit",client)
                pygame.quit()
                client.close()
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            new_x = (game_data["players"][player_id]["x"]+move_speed)+75
            if not (new_x < 0 or new_x + 75 > WIDTH):
                game_data["players"][player_id]["x"]+=move_speed
                messages.send_message(f"move {player_id} {move_speed}",client)
        elif keys[pygame.K_LEFT]:
            new_x = (game_data["players"][player_id]["x"]-move_speed)
            if not (new_x < 0 or new_x + 75 > WIDTH):
                game_data["players"][player_id]["x"]-=move_speed
                messages.send_message(f"move {player_id} -{move_speed}",client)
        elif keys[pygame.K_UP]:
            new_y = (game_data["players"][player_id]["y"]-move_speed)
            if not (new_y < 0 or new_y + 75 > HEIGHT):
                game_data["players"][player_id]["y"]-=move_speed
                messages.send_message(f"move y {player_id} -{move_speed}",client)
        elif keys[pygame.K_DOWN]:
            new_y = (game_data["players"][player_id]["y"]+move_speed)+75
            if not (new_y < 0 or new_y > HEIGHT):
                game_data["players"][player_id]["y"]+=move_speed
                messages.send_message(f"move y {player_id} {move_speed}",client)

        if keys[pygame.K_SPACE]:
            if shoot_counter > 10:
                shoot_counter = 0
                #shoot()

        animation_counter += 1
        if animation_counter == 10:
            if player1_animation == "idle":
                if player1_animation_state == 2:
                    player1_animation_direction = -1
                if player1_animation_state == 0:
                    #NOTE: to enable animations change the 0 to a 1 on the following line
                    player1_animation_direction = 0
                player1_animation_state += player1_animation_direction
            if player2_animation == "idle":
                if player2_animation_state == 2:
                    player2_animation_direction = -1
                if player2_animation_state == 0:
                    player2_animation_direction = 0
                player2_animation_state += player2_animation_direction
            animation_counter = 0

        display_bg()
        display_players()
        pygame.display.update()

#close client
client.close()
pygame.quit()
quit()
