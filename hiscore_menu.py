import unittest.mock
from typing import List
import uuid
import random

import pygame_menu

from scores import UserScore


def init_hiscore_menu(on_close_cb, hiscores: List[UserScore]) -> "pygame_menu.Menu":
    theme_menu = pygame_menu.themes.THEME_BLUE.copy()
    theme_menu.scrollbar_cursor = pygame_menu.locals.CURSOR_HAND

    menu = pygame_menu.Menu(
        height=600,
        onclose=on_close_cb,
        theme=pygame_menu.themes.THEME_SOLARIZED,
        title="HiScores",
        width=800,
    )
    table_contrib = menu.add.table()
    table_contrib.default_cell_padding = 5
    table_contrib.default_row_background_color = "white"
    bold_font = pygame_menu.font.FONT_OPEN_SANS_BOLD

    column_names = ["rank"] + list(hiscores[0].pretty_dict().keys())
    table_contrib.add_row(column_names, cell_font=bold_font, cell_font_size=19)

    # Assign a rank to each score
    ranked_score = sorted({us.highest_score for us in hiscores}, reverse=1)  # type: ignore
    ranked_score_map = {score: rank for rank, score in enumerate(ranked_score, start=1)}

    # Hack but pygame_menu shows poor performances when dealing with large tables
    # so we mockeypatch some slow part.
    # Same for uuid4 generation which turns out to be a bottleneck from time to time
    # (https://stackoverflow.com/questions/51811206/fast-guids-in-python)
    def fast_uuid4(short: bool = False) -> str:
        """
        Create custom version of uuid4.

        :param short: If ``True`` only returns the first 8 chars of the uuid, else, 18
        :return: UUID of 18 chars
        """
        return str(uuid.UUID(int=random.getrandbits(128), version=4))[
            : 18 if not short else 8
        ]

    def fake_update_indices(x):
        return "something cheap"

    with unittest.mock.patch(
        "pygame_menu._base.uuid4",
        new=fast_uuid4,
    ):
        with unittest.mock.patch(
            "pygame_menu.widgets.widget.table.uuid4",
            new=fast_uuid4,
        ):
            with unittest.mock.patch(
                "pygame_menu.widgets.widget.frame.Frame._update_indices",
                new=fake_update_indices,
            ):
                for user_score in hiscores:
                    rank = ranked_score_map[user_score.highest_score]
                    columns = [rank] + list(user_score.pretty_dict().values())
                    table_contrib.add_row(
                        columns,
                        cell_font=bold_font if rank == 1 else None,
                        cell_font_size=15,
                    )
    table_contrib.update_cell_style(
        1, [2, -1], font=pygame_menu.font.FONT_OPEN_SANS_ITALIC
    )
    return menu
