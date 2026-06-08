
import pygame
import json
import random
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--BotPlayer', type=int, required=True, help='1 or 2')
parser.add_argument('--BotStrategyFile', type=str, required=True)
args = parser.parse_args()

pygame.init()

WIDTH = 900
HEIGHT = 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Notakto (2 Boards)")

FONT = pygame.font.SysFont("arial", 28)
SMALL = pygame.font.SysFont("arial", 18)

WHITE = (255,255,255)
BLACK = (0,0,0)
GRAY = (180,180,180)
RED = (220,50,50)

policy_1 = json.load(open("policy_1.json", "r"))
policy_2 = json.load(open("policy_2.json", "r"))

boards = [['0'] * 9 for _ in range(2)]
active = [True, True]
history = []

human_player = args.BotPlayer
current_player = 1
game_over = False
winner = None

BOARD_ORIGINS = [(50,100),(500,100)]


def board_win(board):
    wins = [
        (0,1,2),(3,4,5),(6,7,8),
        (0,3,6),(1,4,7),(2,5,8),
        (0,4,8),(2,4,6)
    ]
    for a,b,c in wins:
        if board[a] == board[b] == board[c] == 'x':
            return True
    return False


def update_active():
    global active
    for i in range(2):
        if active[i] and board_win(boards[i]):
            active[i] = False


def terminal():
    return not any(active)

def get_boards_str():
    s=""
    for b in range(2):
        s+="".join(boards[b])
    return s

def draw():
    screen.fill(WHITE)

    for b in range(2):
        ox, oy = BOARD_ORIGINS[b]

        color = BLACK if active[b] else GRAY

        for i in range(4):
            pygame.draw.line(screen,color,(ox+i*100,oy),(ox+i*100,oy+300),3)
            pygame.draw.line(screen,color,(ox,oy+i*100),(ox+300,oy+i*100),3)

        txt = FONT.render(f"Board {b+1}",True,color)
        screen.blit(txt,(ox+80,50))

        if not active[b]:
            dead = FONT.render("DEAD",True,RED)
            screen.blit(dead,(ox+95,420))

        for sq in range(9):
            r = sq // 3
            c = sq % 3

            if boards[b][sq] == 'x':
                cx = ox + c*100 + 50
                cy = oy + r*100 + 50

                pygame.draw.line(screen,RED,(cx-25,cy-25),(cx+25,cy+25),6)
                pygame.draw.line(screen,RED,(cx-25,cy+25),(cx+25,cy-25),6)

    if game_over:
        msg = FONT.render(f"Player {winner} Wins",True,BLACK)
    else:
        msg = FONT.render(f"Player {current_player} Turn",True,BLACK)

    screen.blit(msg,(330,10))
    pygame.display.flip()


def action_to_square(action):
    return action // 9, action % 9


def square_to_action(board_id, square):
    return board_id * 9 + square


def valid_action(board_id, square):
    return active[board_id] and boards[board_id][square] == '0'


def play_action(action):
    global current_player, game_over, winner

    b, sq = action_to_square(action)

    boards[b][sq] = 'x'
    history.append(action)

    player_who_moved = current_player

    update_active()

    current_player = 2 if current_player == 1 else 1

    if terminal():
        winner = current_player
        game_over = True


clock = pygame.time.Clock()
running = True

while running:

    if not game_over and current_player != human_player:

        key = get_boards_str()

        if current_player == 1:
            current_policy = policy_1
        else:
            current_policy = policy_2

        if key not in current_policy:
            print("Policy missing history:", key)
            print("Current player:", current_player)
            running = False
        else:
            probs = current_policy[key]

            r = random.random()
            s = 0.0
            chosen = None

            for act, p in probs.items():
                s += p
                if r <= s:
                    chosen = int(act)
                    break

            if chosen is None:
                for act, p in probs.items():
                    if p > 0:
                        chosen = int(act)
                        break

            if chosen is not None:
                play_action(chosen)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and not game_over and current_player == human_player:

            mx, my = pygame.mouse.get_pos()

            for b in range(2):

                ox, oy = BOARD_ORIGINS[b]

                if ox <= mx <= ox+300 and oy <= my <= oy+300:

                    col = (mx - ox) // 100
                    row = (my - oy) // 100

                    sq = int(row * 3 + col)

                    if valid_action(b, sq):
                        play_action(square_to_action(b, sq))

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_r:
                boards = [['0'] * 9 for _ in range(2)]
                active = [True, True]
                history = []
                current_player = 1
                game_over = False
                winner = None

    draw()
    clock.tick(60)

pygame.quit()
