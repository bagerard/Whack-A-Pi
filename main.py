import time
import traceback
import sys
from enum import Enum
import os

import pygame

from assets import ASSETS_DIR
from hiscore_menu import init_hiscore_menu
from screens import game_screen, SIZE, lose_screen, win_screen, MainMenuGUI
from react import GameEngine
from scores import ScoreRepository

## Mock GPIO
# from gpiozero import Device
# from gpiozero.pins.mock import MockFactory
#
# Device.pin_factory = MockFactory()
##

clock = pygame.time.Clock()

FPS = 30
GAME_TIME = 30
HISCORE_THRESHOLD = 5

SCORE_FILE = "scores.json"


class GAME_MODE(Enum):
    MAIN_MENU = 1
    INITGAME = 2
    GAME = 3
    POSTGAME = 4


class GameContext:
    def __init__(self, current_mode: GAME_MODE):
        self.current_mode = current_mode


def on_click(
    main_menu: MainMenuGUI, game_engine, game_ctx, score_repo: ScoreRepository
):
    click_pos = pygame.mouse.get_pos()
    print("on_click", click_pos)
    categories_highest_score = score_repo.get_highest_scores_by_cat

    game_category = None
    if game_ctx.current_mode == GAME_MODE.MAIN_MENU:
        game_category = main_menu.selected_category_box(click_pos)
        if game_category:
            game_ctx.current_mode = GAME_MODE.INITGAME
            pygame.display.flip()
        else:
            if main_menu.clicked_hiscores(click_pos) or main_menu.clicked_recent_scores(
                click_pos
            ):
                showmainscreen_cb = lambda: show_mainscreen(
                    game_engine, categories_highest_score
                )

                rank_by_hiscore = main_menu.clicked_hiscores(click_pos)

                sorted_scores = (
                    score_repo.ranked_user_scores
                    if rank_by_hiscore
                    else score_repo.recent_user_scores
                )
                menu = init_hiscore_menu(
                    on_close_cb=showmainscreen_cb, hiscores=sorted_scores
                )
                menu.mainloop(
                    surface=screen,
                    disable_loop=False,
                    fps_limit=30,
                )
                pygame.display.flip()

    elif game_ctx.current_mode == GAME_MODE.POSTGAME:
        game_ctx.current_mode = GAME_MODE.MAIN_MENU
        game_category = None
        show_mainscreen(game_engine, categories_highest_score)

    return game_category


def show_mainscreen(game_engine, categories_highest_score) -> MainMenuGUI:
    print("show_mainscreen")
    game_engine.start_idle()
    main_menu = MainMenuGUI(categories_highest_score)
    main_menu.draw(screen)
    print("out of show_mainscreen")
    return main_menu


def play_music(mp3_path: str) -> None:
    if os.path.exists(mp3_path):
        pygame.mixer.music.load(mp3_path)
        pygame.mixer.music.play()
        print("done playing music")
    else:
        print(f"fake play music {mp3_path}")


def main():
    run_button_thread = bool(int(os.environ.get("BUTTON_THREAD", 0)))

    game_ctx = GameContext(current_mode=GAME_MODE.MAIN_MENU)
    score_repo = ScoreRepository(filepath=SCORE_FILE, backup_files=False)

    game_engine = GameEngine(game_time=GAME_TIME)
    main_menu = show_mainscreen(
        game_engine, categories_highest_score=score_repo.get_highest_scores_by_cat
    )

    game_category = None

    print("start main while loop")
    prev_mode = game_ctx.current_mode
    played_boxing_bell = False
    while True:
        clock.tick(FPS)

        if prev_mode != game_ctx.current_mode:
            print(f"SWITCHED TO MODE {game_ctx.current_mode}")
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

            if run_button_thread:
                game_engine.start_loop_btn_thread()

            print("game_engine.ready_wait")

            if game_engine.ready_wait(min(60, GAME_TIME)):
                play_music(f"{ASSETS_DIR}/robots_auto_aim_engaged.wav")
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)

                last_elapsed = -1
                last_score = -1
                play_music("mi.mp3")
                game_ctx.current_mode = GAME_MODE.GAME
                game_engine.start_game()
            else:
                game_ctx.current_mode = GAME_MODE.MAIN_MENU
                game_category = None
                main_menu = show_mainscreen(
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
                # play_music("airhorn.mp3")
                # while pygame.mixer.music.get_busy():
                #     time.sleep(0.1)

                if game_result.score >= HISCORE_THRESHOLD:
                    play_music(f"{ASSETS_DIR}/successful-horn.wav")
                    # Player Achieved more than the threshold and can register
                    user_infos = win_screen(
                        screen, recent_usernames=score_repo.recent_gamers_usernames
                    )
                    firstname = user_infos[0]

                    score_repo.update_user_score(
                        cat=game_category,
                        username=firstname,
                        score=game_result.score,
                        mean_hit_time=game_result.mean_hit_time,
                    )

                    game_ctx.current_mode = GAME_MODE.MAIN_MENU
                    game_category = None
                    show_mainscreen(
                        game_engine,
                        categories_highest_score=score_repo.get_highest_scores_by_cat,
                    )
                else:
                    play_music(f"{ASSETS_DIR}/funny-clown-horn.wav")
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
                        0 < game_result.score >= highest_cat_user_score.highest_score
                    )
                    if beat_a_champion and not played_boxing_bell:
                        play_music(f"{ASSETS_DIR}/BoxingBell.wav")
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
                new_game_category = on_click(
                    main_menu, game_engine, game_ctx, score_repo
                )
                game_category = game_category or new_game_category


try:
    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    main()
except BaseException as e:
    traceback.print_exception(*sys.exc_info())
    pygame.quit()
    sys.exit()
