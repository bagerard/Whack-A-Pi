import time
import traceback
import sys
from enum import Enum

import pygame

from screens import game_screen, SIZE, menu_screen, lose_screen, win_screen
from react import Game
from scores import ScoreRepository

GAME_TIME = 5

SCORE_FILE = "scores.json"


class GAME_MODE(Enum):
    MENU = 1
    INITGAME = 2
    GAME = 3
    POSTGAME = 4


class GameContext:
    def __init__(self, current_mode: GAME_MODE):
        self.current_mode = current_mode


def on_click(game_engine, game_ctx, categories_highest_score):
    print("on_click")
    click_pos = (pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])

    game_category = -1
    if game_ctx.current_mode == GAME_MODE.MENU:
        button_width = SIZE[0] / 3
        if click_pos[1] > SIZE[1] / 3:
            game_category = int(click_pos[0] / button_width)
            game_ctx.current_mode = GAME_MODE.INITGAME
    elif game_ctx.current_mode == GAME_MODE.POSTGAME:
        game_ctx.current_mode = GAME_MODE.MENU
        show_mainscreen(game_engine, categories_highest_score)

    return list(categories_highest_score.keys())[game_category]


def show_mainscreen(game_engine, categories_highest_score) -> None:
    print("show_mainscreen")
    game_engine.start_idle()
    menu_screen(screen, categories_highest_score)
    print("out of show_mainscreen")


def play_music(mp3_path: str) -> None:
    # pygame.mixer.music.load(mp3_path)
    # pygame.mixer.music.play()
    print(f"fake play music {mp3_path}")


def main():
    game_ctx = GameContext(current_mode=GAME_MODE.MENU)
    score_repo = ScoreRepository(filepath=SCORE_FILE)

    game_engine = Game(game_time=GAME_TIME)
    show_mainscreen(
        game_engine,
        categories_highest_score=score_repo.get_highest_scores_by_cat
        )

    game_category = -1

    print("start main while loop")
    prev_mode = game_ctx.current_mode
    while True:
        if prev_mode != game_ctx.current_mode:
            print("SWITCH TO MODE", game_ctx.current_mode)
            prev_mode = game_ctx.current_mode

        if game_ctx.current_mode == GAME_MODE.INITGAME:
            game_engine.stop_idle()
            print("game_screen")

            highest_user_score = score_repo.get_highest_scores_by_cat[game_category]
            game_screen(screen, GAME_TIME, 0, highest_user_score, wait=True)

            game_engine.start_loop_btn_thread()  # BAG DEBUG
            print("game_engine.ready_wait")

            if game_engine.ready_wait(min(60, GAME_TIME)):
                play_music("Robot Wars Clean SFX- 3 2 1 Actvate!.mp3")
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)

                last_elapsed = -1
                last_score = -1
                play_music("mi.mp3")
                game_ctx.current_mode = GAME_MODE.GAME
                game_engine.start_game()
            else:
                game_ctx.current_mode = GAME_MODE.MENU
                show_mainscreen(game_engine, categories_highest_score=score_repo.get_highest_scores_by_cat)

        elif game_ctx.current_mode == GAME_MODE.GAME:
            elapsed = int(round(GAME_TIME - game_engine.elapsed_time(), 0))
            score = game_engine.score
            if elapsed < 0:
                highest_user_score = score_repo.get_highest_scores_by_cat[game_category]
                game_screen(screen, 0, score, highest_user_score)
                play_music("airhorn.mp3")

                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)

                if score > highest_user_score.highest_score:
                    user_infos = win_screen(screen)
                    firstname = user_infos[0]

                    score_repo.update_user_score(game_category, firstname, score)

                    game_ctx.current_mode = GAME_MODE.MENU
                    show_mainscreen(game_engine, categories_highest_score=score_repo.get_highest_scores_by_cat)
                else:
                    lose_screen(screen)
                    game_ctx.current_mode = GAME_MODE.POSTGAME

            elif elapsed != last_elapsed or score != last_score:
                game_screen(screen, elapsed, score, score_repo.get_highest_scores_by_cat[game_category])
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
                game_category = on_click(game_engine, game_ctx, score_repo.get_highest_scores_by_cat)


try:
    pygame.init()
    screen = pygame.display.set_mode(SIZE)

    main()
except BaseException as e:
    traceback.print_exception(*sys.exc_info())
    pygame.quit()
    sys.exit()
