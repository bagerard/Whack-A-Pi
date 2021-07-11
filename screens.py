from typing import List, Dict, Tuple

import pygame
import eztext
import sys

# set SIZE of the screen
from scores import UserScore

SIZE = (1280, 800)
width, height = SIZE

# define colours
BLUE = 26, 0, 255
ORANGE = 255, 165, 0
BLACK = 0, 0, 0
WHITE = 255, 255, 255
YELLOW = 255, 255, 0
RED = 255, 0, 0
GREEN = 0, 255, 0

top = 0


CLOCK_FONT_PATH = "assets/digital-7 (mono).ttf"

clock = pygame.time.Clock()
FPS = 30

def align_h(label, cols=1, col=0, width=SIZE[0]):
    col_width = width / cols
    return ((col_width - label.get_width()) / 2) + col_width * col


def align_v(label, rows=1, row=0, height=SIZE[1]):
    row_height = height / rows
    return ((row_height - label.get_height()) / 2) + row_height * row


def menu_screen(screen, categories_highest_score: Dict[str, UserScore]):
    global top

    line_pos = 15
    screen.fill(BLACK)  # change the colours if needed
    fnt_head = pygame.font.Font(None, 288)
    fnt_title = pygame.font.Font(None, 84)
    lab_head = fnt_head.render("Whack-A-Pi", 1, YELLOW)
    screen.blit(lab_head, (align_h(lab_head), line_pos))
    line_pos += lab_head.get_height() + 60

    fnt_score = pygame.font.Font(CLOCK_FONT_PATH, 200)

    top = line_pos
    max_width = SIZE[0] / 3
    max_height = SIZE[1] - top

    ranked_categories = [
        (cat, user_score) for cat, user_score in categories_highest_score.items()
    ]
    ranked_categories.sort(key=lambda d: d[1].highest_score, reverse=True)

    for idx, (score_category, user_score) in enumerate(
        categories_highest_score.items()
    ):

        rect = left, top, width, height = (
            (max_width * idx) + 10,
            top,
            max_width - 20,
            max_height - 10,
        )
        pygame.draw.rect(screen, WHITE, rect, 1)

        if score_category == ranked_categories[0][0]:
            crown_img = pygame.image.load("assets/crown.png").convert_alpha()
            screen.blit(
                crown_img,
                (
                    left + (width / 2) - crown_img.get_width() / 2,
                    top - (crown_img.get_height() / 2) - 4,
                ),
            )

        line_pos = top  # reset the vertical cursor
        line_pos += 45
        lab_title = fnt_title.render(score_category, 1, WHITE)
        screen.blit(lab_title, (align_h(lab_title, 3, idx), line_pos))

        line_pos += lab_title.get_height() + 30
        lab_score = fnt_score.render(f"{user_score.highest_score:0>3d}", 1, BLUE)
        screen.blit(lab_score, (align_h(lab_score, 3, idx), line_pos))

        line_pos += lab_score.get_height() + 30
        lab_name1 = fnt_title.render(
            f"{user_score.username}", 1, ORANGE
        )
        screen.blit(lab_name1, (align_h(lab_name1, 3, idx), line_pos))

        # old Lastname
        # line_pos += lab_name1.get_height() + 15
        # lab_name2 = fnt_title.render(user_score.somethingelse, 1, ORANGE)
        # screen.blit(lab_name2, (align_h(lab_name2, 3, idx), line_pos))

    pygame.display.flip()


def game_screen(
    screen,
    elapsed,
    score,
    cat_champion: UserScore,
    overall_champion: UserScore,
    wait=False,
):
    screen.fill(BLACK)  # change the colours if needed
    fnt_title = pygame.font.Font(None, 144)
    lab_time_title = fnt_title.render("Time", 1, WHITE)
    screen.blit(lab_time_title, (align_h(lab_time_title, 2, 0), 15))

    fnt_title = pygame.font.Font(None, 144)
    lab_score_title = fnt_title.render("Score", 1, WHITE)
    screen.blit(lab_score_title, (align_h(lab_score_title, 2, 1), 15))

    if wait:
        lab_wait = fnt_title.render("Press light when ready", 1, YELLOW)
        screen.blit(
            lab_wait, (align_h(lab_wait, 1, 0), 15 + lab_score_title.get_height())
        )

    font = pygame.font.Font(CLOCK_FONT_PATH, 432)

    lab_time = font.render(f"{elapsed:0>2d}", 1, ORANGE)
    screen.blit(lab_time, (align_h(lab_time, 2, 0), align_v(lab_time)))

    lab_score = font.render(f"{score:0>3d}", 1, BLUE)
    screen.blit(lab_score, (align_h(lab_score, 2, 1), align_v(lab_score)))

    # Dept Champion
    fnt_subtitle = pygame.font.Font(None, 60)
    lab_hi_title = fnt_subtitle.render("Dept. Hi-Score:", 1, WHITE)

    fnt_hiscore = pygame.font.Font(CLOCK_FONT_PATH, 72)
    lab_hi_score = fnt_hiscore.render(f"{cat_champion.highest_score:0>3d}", 1, BLUE)

    score_top = SIZE[1] - lab_hi_score.get_height() - 80
    hi_top = score_top + (lab_hi_score.get_height() - lab_hi_title.get_height()) / 2

    screen.blit(lab_hi_title, (align_h(lab_hi_title, 4, 2) + 25, hi_top))
    screen.blit(lab_hi_score, (align_h(lab_hi_score, 4, 3), score_top))

    # Global Champion
    fnt_subtitle2 = pygame.font.Font(None, 40)
    lab_hi_title2 = fnt_subtitle2.render("Global Hi-Score:", 1, WHITE)

    fnt_hiscore2 = pygame.font.Font(CLOCK_FONT_PATH, 52)
    lab_hi_score2 = fnt_hiscore2.render(
        f"{overall_champion.highest_score:0>3d}", 1, BLUE
    )

    score_top = SIZE[1] - lab_hi_score.get_height() - 20
    hi_top = score_top + (lab_hi_score.get_height() - lab_hi_title.get_height()) / 2

    screen.blit(lab_hi_title2, (align_h(lab_hi_title, 4, 2) + 25, hi_top))
    screen.blit(lab_hi_score2, (align_h(lab_hi_score, 4, 3), score_top))

    pygame.display.flip()


def _draw_win_screen(screen):
    screen.fill(BLACK, (0, 0, SIZE[0] / 2, SIZE[1]))
    fnt_head = pygame.font.Font(None, 144)
    lab_head = fnt_head.render("High Score!", 1, YELLOW)
    screen.blit(lab_head, (align_h(lab_head, 2, 0), 15))

    lab_btn = fnt_head.render(
        "Submit",
        1,
        YELLOW,
    )
    x = align_h(lab_btn, 2, 0)
    y = SIZE[1] - 30 - lab_btn.get_height()
    screen.blit(lab_btn, (x, y))
    return pygame.draw.rect(
        screen,
        YELLOW,
        (x - 15, y - 15, lab_btn.get_width() + 30, lab_btn.get_height() + 30),
        1,
    )


def _box_clicked(item, pos: Tuple[int, int]):
    return item.top <= pos[1] <= item.bottom and item.left <= pos[0] <= item.right


def win_screen(screen) -> List[str]:
    """Returns User input from the win screen"""
    line_pos = SIZE[1] / 3

    firstname_input = eztext.Input(
        maxlength=30,
        color=WHITE,
        focuscolor=YELLOW,
        prompt="Username: ",
        x=15,
        y=line_pos,
        hasfocus=True,
    )
    # Note if we add inputbox, we need to increment y by 50 each time
    inputboxes = [firstname_input]
    ib_idx = 0  # selected input box index

    submit_btn = _draw_win_screen(screen)

    while True:
        clock.tick(FPS)
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                pos = (pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])

                submit_btn_clicked = _box_clicked(submit_btn, pos)
                if submit_btn_clicked:
                    print("Submit button clicked")
                    return [ib.value for ib in inputboxes]

                for i, ib in enumerate(inputboxes):
                    ib_selected = _box_clicked(ib, pos)
                    if ib_selected:
                        print(f'Input box {i} selected - change focus')
                        inputboxes[ib_idx].set_focus(False)
                        ib.set_focus(True)
                        ib_idx = i
                        break

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_F12:
                    pygame.quit()
                    sys.exit()

                if event.key == pygame.K_TAB:
                    inputboxes[ib_idx].set_focus(False)
                    ib_idx += 1
                    if ib_idx >= len(inputboxes):
                        ib_idx = 0
                    inputboxes[ib_idx].set_focus(True)

                if event.key == pygame.K_RETURN:
                    if all(ib.value != "" for ib in inputboxes):
                        return [ib.value for ib in inputboxes]
                    else:
                        print("Missing required input value")

        submit_btn = _draw_win_screen(screen)
        inputboxes[ib_idx].update(events)
        for ib in inputboxes:
            ib.draw(screen)
        pygame.display.flip()


def lose_screen(screen):
    screen.fill(BLACK, (0, 0, SIZE[0] / 2, SIZE[1]))
    fnt_head = pygame.font.Font(None, 144)
    lab_head = fnt_head.render("Click", 1, YELLOW)
    screen.blit(lab_head, (align_h(lab_head, 2, 0), align_v(lab_head, 3, 0)))

    lab_head = fnt_head.render("to", 1, YELLOW)
    screen.blit(lab_head, (align_h(lab_head, 2, 0), align_v(lab_head, 3, 1)))

    lab_head = fnt_head.render("Continue", 1, YELLOW)
    screen.blit(lab_head, (align_h(lab_head, 2, 0), align_v(lab_head, 3, 2)))
    pygame.display.flip()
