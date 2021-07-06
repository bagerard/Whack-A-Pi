import time
import os
import json

import pygame
import sys

from screens import *
import react
import traceback

game_level = -1

DEFAULT_HIGH_SCORES = [
    [0, "Olivier", "Athos", None, None],
    [0, "Rene", "Aramis", None, None],
    [0, "Isaac", "Porthos", None, None],
]

SCORE_FILE = "scores.json"


class GameContext:
    def __init__(self, current_mode):
        self.current_mode = current_mode


def save_scores(high_scores):
    print("save_score")
    if os.access(SCORE_FILE, os.W_OK):
        os.rename(SCORE_FILE, SCORE_FILE + "." + str(time.time()))
    with open(SCORE_FILE, mode="w", encoding="utf-8") as f:
        json.dump(high_scores, f, indent=2)


def load_scores():
    print("load_score")
    if os.access(SCORE_FILE, os.R_OK):
        print("open")
        with open(SCORE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    print('Load default scores')
    return DEFAULT_HIGH_SCORES


def on_click(game_engine, high_scores, game_ctx):
    print("on_click")
    global game_level
    click_pos = (pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])

    if game_ctx.current_mode == "menu":
        button_width = SIZE[0] / 3
        if click_pos[1] > SIZE[1] / 3:
            game_level = int(click_pos[0] / button_width)
            game_ctx.current_mode = "initgame"
    elif game_ctx.current_mode == "postgame":
        game_ctx.current_mode = "menu"
        show_mainscreen(game_engine, high_scores)


def show_mainscreen(game_engine, high_scores) -> None:
    print("show_mainscreen")
    game_engine.start_idle()
    print("menu_screen")
    menu_screen(screen, high_scores)
    print("out of show_mainscreen")


def play_music(mp3_path: str) -> None:
    # pygame.mixer.music.load(mp3_path)
    # pygame.mixer.music.play()
    print(f'fake play music {mp3_path}')


def main():
    game_ctx = GameContext(current_mode="menu")
    game_engine = react.Game()
    print("main")
    high_scores = load_scores()
    show_mainscreen(game_engine, high_scores=high_scores)

    print('start main while loop')
    prev_mode = game_ctx.current_mode
    while True:
        if prev_mode != game_ctx.current_mode:
            print("SWITCH TO MODE", game_ctx.current_mode)
            prev_mode = game_ctx.current_mode

        if game_ctx.current_mode == "initgame":
            game_engine.stop_idle()
            print('game_screen')
            game_screen(screen, 60, 0, high_scores[game_level][0], True)

            game_engine.start_loop_btn_thread()                         # BAG DEBUG
            print('game_engine.ready_wait')
            if game_engine.ready_wait(60):
                play_music("Robot Wars Clean SFX- 3 2 1 Actvate!.mp3")
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)

                elapsed = 61
                score = 0
                last_elapsed = -1
                last_score = -1
                play_music("mi.mp3")
                game_ctx.current_mode = "game"
                game_engine.start_game()
            else:
                print('! if game_engine.ready_wait(30):')
                game_ctx.current_mode = "menu"
                show_mainscreen(game_engine, high_scores=high_scores)

        elif game_ctx.current_mode == "game":
            elapsed = int(round(60 - game_engine.elapsed_time(), 0))
            score = game_engine.score
            if elapsed < 0:
                game_screen(screen, 0, score, high_scores[game_level][0])
                play_music("airhorn.mp3")
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                if score > high_scores[game_level][0]:
                    ret = win_screen(screen)
                    high_scores[game_level][0] = score
                    high_scores[game_level][1] = ret[0]
                    high_scores[game_level][2] = ret[1]
                    high_scores[game_level][3] = ret[2]
                    high_scores[game_level][4] = ret[3]
                    save_scores(high_scores)
                    game_ctx.current_mode = "menu"
                    show_mainscreen(game_engine, high_scores=high_scores)
                else:
                    lose_screen(screen)
                    game_ctx.current_mode = "postgame"

            elif elapsed != last_elapsed or score != last_score:
                game_screen(screen, elapsed, score, high_scores[game_level][0])
                last_elapsed = elapsed
                last_score = score

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                print(f'Event: QUIT')
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                print(f'Event: KEYDOWN')
                if event.key == pygame.K_F12:
                    print(f'Event: K_F12')
                    game_engine.stop_idle()
                    game_engine.stop_game()
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                print(f'Event: MOUSEBUTTONUP')
                pos = (pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
                pygame.draw.circle(screen, pygame.Color(255, 10, 10), pos, 2, 0) #for debugging purposes - adds a small dot where the screen is pressed
                on_click(game_engine, high_scores, game_ctx)


try:
    pygame.init()
    screen = pygame.display.set_mode(SIZE)

    main()
except BaseException as e:
    traceback.print_exception(*sys.exc_info())
    pygame.quit()
    sys.exit()
