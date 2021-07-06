import time
import traceback
import sys

import pygame

from screens import game_screen, SIZE, menu_screen, lose_screen, win_screen
from react import Game
from scores import save_scores, load_scores

game_level = -1

GAME_TIME = 5

SCORE_CATEGORIES = ["Dev", "F&A", "Op"]
DEFAULT_HIGH_SCORES = [
    [0, "Olivier"],
    [0, "Rene"],
    [0, "Isaac"],
]

SCORE_FILE = "scores.json"


class GameContext:
    def __init__(self, current_mode):
        self.current_mode = current_mode


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
    menu_screen(screen, high_scores, scores_categories=SCORE_CATEGORIES)
    print("out of show_mainscreen")


def play_music(mp3_path: str) -> None:
    # pygame.mixer.music.load(mp3_path)
    # pygame.mixer.music.play()
    print(f"fake play music {mp3_path}")


def main():
    game_ctx = GameContext(current_mode="menu")
    high_scores = load_scores(SCORE_FILE) or DEFAULT_HIGH_SCORES

    game_engine = Game(game_time=GAME_TIME)
    show_mainscreen(game_engine, high_scores=high_scores)

    print("start main while loop")
    prev_mode = game_ctx.current_mode
    while True:
        if prev_mode != game_ctx.current_mode:
            print("SWITCH TO MODE", game_ctx.current_mode)
            prev_mode = game_ctx.current_mode

        if game_ctx.current_mode == "initgame":
            game_engine.stop_idle()
            print("game_screen")

            highest_score = high_scores[game_level][0]
            game_screen(screen, GAME_TIME, 0, highest_score, wait=True)

            game_engine.start_loop_btn_thread()  # BAG DEBUG
            print("game_engine.ready_wait")

            if game_engine.ready_wait(min(60, GAME_TIME)):
                play_music("Robot Wars Clean SFX- 3 2 1 Actvate!.mp3")
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)

                last_elapsed = -1
                last_score = -1
                play_music("mi.mp3")
                game_ctx.current_mode = "game"
                game_engine.start_game()
            else:
                print("! if game_engine.ready_wait(30):")
                game_ctx.current_mode = "menu"
                show_mainscreen(game_engine, high_scores=high_scores)

        elif game_ctx.current_mode == "game":
            elapsed = int(round(GAME_TIME - game_engine.elapsed_time(), 0))
            score = game_engine.score
            if elapsed < 0:
                highest_score = high_scores[game_level][0]
                game_screen(screen, 0, score, highest_score)
                play_music("airhorn.mp3")

                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)

                if score > highest_score:
                    user_infos = win_screen(screen)
                    firstname = user_infos[0]

                    high_scores[game_level][0] = score
                    high_scores[game_level][1] = firstname

                    save_scores(high_scores, SCORE_FILE)

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
                print(f"Event: QUIT")
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                print(f"Event: KEYDOWN")
                if event.key == pygame.K_F12:
                    print(f"Event: K_F12")
                    game_engine.stop_idle()
                    game_engine.stop_game()
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                print(f"Event: MOUSEBUTTONUP")
                pos = (pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
                pygame.draw.circle(
                    screen, pygame.Color(255, 10, 10), pos, 2, 0
                )  # for debugging purposes - adds a small dot where the screen is pressed
                on_click(game_engine, high_scores, game_ctx)


try:
    pygame.init()
    screen = pygame.display.set_mode(SIZE)

    main()
except BaseException as e:
    traceback.print_exception(*sys.exc_info())
    pygame.quit()
    sys.exit()
