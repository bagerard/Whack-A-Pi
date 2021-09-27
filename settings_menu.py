import time

import pygame_menu

from react import GameEngine


def reset_menu_selection(menu):
    menu.select_widget(None)


def led_check(menu, game_engine: GameEngine, check_time: int):
    """Turn on all led for check_time seconds"""
    print("Start led_check")

    start = time.time()
    elapsed = lambda: time.time() - start

    game_engine.lights.on()
    while elapsed() <= check_time:
        time.sleep(1)

    game_engine.lights.off()
    reset_menu_selection(menu)
    print("Done led_check")


def led_button_check(menu, game_engine: GameEngine):
    """Light up the buttons 1 by 1 to verify that it all work"""
    print("Start led_button_check")
    game_engine.button_test()
    print("Done led_button_check")
    reset_menu_selection(menu)


def init_settings_menu(on_close_cb, game_engine) -> "pygame_menu.Menu":
    theme_menu = pygame_menu.themes.THEME_BLUE.copy()
    theme_menu.scrollbar_cursor = pygame_menu.locals.CURSOR_HAND

    # Main menu, pauses execution of the application
    menu = pygame_menu.Menu(
        height=400, onclose=on_close_cb, theme=theme_menu, title="Main Menu", width=600
    )

    cheat_sub_menu = pygame_menu.Menu(
        height=400, onclose=on_close_cb, theme=theme_menu, title="Cheat Menu", width=600
    )

    # Led check
    led_check_time = 30  # sec
    menu.add.button(
        f"Led check ({led_check_time} sec)",
        led_check,
        menu,
        game_engine,
        led_check_time,
    )

    menu.add.button(
        f"Led & Button check",
        led_button_check,
        menu,
        game_engine,
    )

    menu.add.button("Cheat Menu", cheat_sub_menu)

    cheat_sub_menu.add.button("What were you expecting?!")

    menu.add.button("Exit Game", pygame_menu.events.EXIT)
    return menu
