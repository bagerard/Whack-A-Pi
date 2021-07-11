import unittest.mock
from typing import List

import pygame_menu

from scores import UserScore


def init_hiscore_menu(on_close_cb, hiscores: List[UserScore]) -> "pygame_menu.Menu":
    theme_menu = pygame_menu.themes.THEME_BLUE.copy()
    theme_menu.scrollbar_cursor = pygame_menu.locals.CURSOR_HAND

    menu = pygame_menu.Menu(
        height=400,
        onclose=on_close_cb,
        theme=pygame_menu.themes.THEME_SOLARIZED,
        title="HiScores",
        width=700,
    )
    table_contrib = menu.add.table()
    table_contrib.default_cell_padding = 5
    table_contrib.default_row_background_color = "white"
    bold_font = pygame_menu.font.FONT_OPEN_SANS_BOLD

    column_names = ["rank"] + list(hiscores[0].pretty_dict().keys())
    table_contrib.add_row(column_names, cell_font=bold_font, cell_font_size=15)

    # Hack but Frame._update_indices turned out to bottleneck for large table (> 50-100 entries)
    # and by mockeypatching it in a dumb way, it seems to have no effects
    with unittest.mock.patch(
        'pygame_menu.widgets.widget.frame.Frame._update_indices',
        new=lambda x: 'Something really cheap.'
    ):
        for idx, user_score in enumerate(hiscores):
            rank = idx + 1
            columns = [rank] + list(user_score.pretty_dict().values())
            table_contrib.add_row(
                columns,
                cell_font=bold_font if idx == 0 else None,
                cell_font_size=15
            )
    table_contrib.update_cell_style(
        1, [2, -1], font=pygame_menu.font.FONT_OPEN_SANS_ITALIC
    )
    return menu
