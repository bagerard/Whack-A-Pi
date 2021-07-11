import time
import traceback
import sys
from enum import Enum
import os

import pygame

from hiscore_menu import init_hiscore_menu
from screens import game_screen, SIZE, menu_screen, lose_screen, win_screen
from react import GameEngine
from scores import ScoreRepository

## Mock GPIO
from gpiozero import Device
from gpiozero.pins.mock import MockFactory
Device.pin_factory = MockFactory()
##

clock = pygame.time.Clock()

FPS = 30

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
            if game_category != 0:
                game_ctx.current_mode = GAME_MODE.INITGAME
            elif game_category == 0:
                # Execute main from principal menu if is enabled

                showmainscreen_cb = lambda: show_mainscreen(
                    game_engine, categories_highest_score
                )

                menu = init_hiscore_menu(on_close_cb=showmainscreen_cb)
                menu.mainloop(
                    surface=screen,
                    # bgfun=partial(paint_background, screen),
                    disable_loop=False,
                    fps_limit=30,
                )
                # Update surface
                pygame.display.flip()
                print("HHAAAAAL")
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
    if os.path.exists(mp3_path):
        pygame.mixer.music.load(mp3_path)
        pygame.mixer.music.play()
        print("done playing music")
    else:
        print(f"fake play music {mp3_path}")


def main():
    game_ctx = GameContext(current_mode=GAME_MODE.MENU)
    score_repo = ScoreRepository(filepath=SCORE_FILE, backup_files=False)

    game_engine = GameEngine(game_time=GAME_TIME)
    show_mainscreen(
        game_engine, categories_highest_score=score_repo.get_highest_scores_by_cat
    )

    game_category = -1

    print("start main while loop")
    prev_mode = game_ctx.current_mode
    played_boxing_bell = False
    while True:
        clock.tick(FPS)
        # time.sleep(0.05)
        if prev_mode != game_ctx.current_mode:
            print("SWITCH TO MODE", game_ctx.current_mode)
            prev_mode = game_ctx.current_mode

        if game_ctx.current_mode == GAME_MODE.INITGAME:
            # Game waiting for user hitting the first button
            played_boxing_bell = False
            game_engine.stop_idle()
            print("game_screen")

            highest_cat_user_score = score_repo.get_highest_scores_by_cat[game_category]
            game_screen(
                screen,
                GAME_TIME,
                0,
                highest_cat_user_score,
                overall_champion=score_repo.overall_champion,
                wait=True,
            )

            game_engine.start_loop_btn_thread()  # BAG DEBUG
            print("game_engine.ready_wait")

            if game_engine.ready_wait(min(60, GAME_TIME)):
                play_music("assets/robots_auto_aim_engaged.wav")
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)

                last_elapsed = -1
                last_score = -1
                play_music("mi.mp3")
                game_ctx.current_mode = GAME_MODE.GAME
                game_engine.start_game()
            else:
                game_ctx.current_mode = GAME_MODE.MENU
                show_mainscreen(
                    game_engine,
                    categories_highest_score=score_repo.get_highest_scores_by_cat,
                )

        elif game_ctx.current_mode == GAME_MODE.GAME:
            # Game starting
            elapsed = int(round(GAME_TIME - game_engine.elapsed_time(), 0))
            game_result = game_engine.game_result

            game_is_finished = elapsed < 0
            if game_is_finished:
                highest_cat_user_score = score_repo.get_highest_scores_by_cat[
                    game_category
                ]
                game_screen(
                    screen,
                    0,
                    game_result.score,
                    highest_cat_user_score,
                    overall_champion=score_repo.overall_champion,
                )
                play_music("airhorn.mp3")

                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)

                if game_result.score >= highest_cat_user_score.highest_score:
                    user_infos = win_screen(screen)
                    firstname = user_infos[0]

                    score_repo.update_user_score(
                        cat=game_category,
                        username=firstname,
                        score=game_result.score,
                        mean_hit_time=game_result.mean_hit_time,
                    )

                    game_ctx.current_mode = GAME_MODE.MENU
                    show_mainscreen(
                        game_engine,
                        categories_highest_score=score_repo.get_highest_scores_by_cat,
                    )
                else:
                    lose_screen(screen)
                    game_ctx.current_mode = GAME_MODE.POSTGAME

            else:
                screen_need_refresh = (
                    elapsed != last_elapsed or game_result.score != last_score
                )
                if screen_need_refresh:
                    game_screen(
                        screen,
                        elapsed,
                        game_result.score,
                        score_repo.get_highest_scores_by_cat[game_category],
                        overall_champion=score_repo.overall_champion,
                    )
                    last_elapsed = elapsed
                    last_score = game_result.score

                    beat_a_champion = (
                        game_result.score >= highest_cat_user_score.highest_score
                    )
                    if beat_a_champion and not played_boxing_bell:
                        play_music("assets/BoxingBell.wav")
                        played_boxing_bell = True

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
                # pos = (pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
                # pygame.draw.circle(
                #     screen, pygame.Color(255, 10, 10), pos, 2, 0
                # )  # for debugging purposes - adds a small dot where the screen is pressed
                game_category = on_click(
                    game_engine, game_ctx, score_repo.get_highest_scores_by_cat
                )


try:
    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    main()
except BaseException as e:
    traceback.print_exception(*sys.exc_info())
    pygame.quit()
    sys.exit()
