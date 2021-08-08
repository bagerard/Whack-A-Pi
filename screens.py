import sys
from dataclasses import dataclass
from typing import List, Dict, Tuple, Any

import pygame
from pygame import Surface
from pygame_vkeyboard import VKeyboardLayout, VKeyboard, VKeyboardRenderer
import eztext

# set SIZE of the screen
from assets import ASSETS_DIR
from scores import UserScore

SIZE = (1280, 720)

# define colours
BLUE = 26, 0, 255
ORANGE = 255, 165, 0
BLACK = 0, 0, 0
WHITE = 255, 255, 255
YELLOW = 255, 255, 0
RED = 255, 0, 0
GREEN = 0, 255, 0

top = 0


CLOCK_FONT_PATH = f"{ASSETS_DIR}/digital-7 (mono).ttf"

clock = pygame.time.Clock()
FPS = 30


def rect_is_clicked(rect, click_pos):
    click_x, click_y = click_pos
    left, top, width, height = rect
    return left <= click_x <= left + width and top <= click_y <= top + height


def align_h(label, cols=1, col=0, width=SIZE[0]):
    """
    Given a label, cut the width into {cols} and return coordinates of the button
    at place {col}
    """
    col_width = width / cols
    return ((col_width - label.get_width()) / 2) + col_width * col


def align_v(label, rows=1, row=0, height=SIZE[1]):
    row_height = height / rows
    return ((row_height - label.get_height()) / 2) + row_height * row


@dataclass
class MainMenuCatBox:
    rect: Tuple[float, float, float, float]
    title: str
    rendered_title: Any
    rendered_title_coord: Tuple[int, int]
    rendered_hiscore: Any
    rendered_hiscore_coord: Tuple[int, int]
    rendered_username: Any
    rendered_username_coord: Tuple[int, int]


class MainMenuGUI:
    def __init__(self, categories_highest_score: Dict[str, UserScore]):
        self.init_line_pos = 10

        # Title "Whack-A-Pi"
        fnt_head = pygame.font.Font(None, 175)
        self.lab_head = fnt_head.render("Whack-A-Pi", 1, YELLOW)

        # Category Box
        fnt_title = pygame.font.Font(None, 84)
        fnt_score = pygame.font.Font(CLOCK_FONT_PATH, 200)

        offset_title_rects = 20
        line_pos = self.init_line_pos + self.lab_head.get_height() + offset_title_rects

        top = line_pos
        max_width = SIZE[0] / 3
        max_height = SIZE[1] - top

        ranked_categories = [
            (cat, user_score) for cat, user_score in categories_highest_score.items()
        ]
        ranked_categories.sort(key=lambda d: d[1].highest_score, reverse=True)

        self.cat_boxes: List[MainMenuCatBox] = []
        self.crown_img_coord: Tuple[int, int]

        for idx, (score_category, user_score) in enumerate(
            categories_highest_score.items()
        ):
            left, top, width, height = (
                (max_width * idx) + 10,
                top,
                max_width - 20,
                max_height - 80,
            )

            is_champion_category = score_category == ranked_categories[0][0]
            if is_champion_category:
                self.crown_img = pygame.image.load(
                    f"{ASSETS_DIR}/crown.png"
                ).convert_alpha()
                self.crown_img_coord = (
                    left + (width / 2) - self.crown_img.get_width() / 2,
                    top - (self.crown_img.get_height() / 2) - 4,
                )

            line_pos = top  # reset the vertical cursor
            line_pos += 45
            lab_title = fnt_title.render(score_category, 1, WHITE)
            lab_title_coord = (align_h(lab_title, 3, idx), line_pos)

            line_pos += lab_title.get_height() + 30
            lab_score = fnt_score.render(f"{user_score.highest_score:0>3d}", 1, BLUE)
            lab_score_coord = (align_h(lab_score, 3, idx), line_pos)

            line_pos += lab_score.get_height() + 30
            lab_username = fnt_title.render(f"{user_score.username}", 1, ORANGE)
            lab_username_coord = (align_h(lab_username, 3, idx), line_pos)
            cat_box = MainMenuCatBox(
                rect=(left, top, width, height),
                title=score_category,
                rendered_title=lab_title,
                rendered_title_coord=lab_title_coord,
                rendered_hiscore=lab_score,
                rendered_hiscore_coord=lab_score_coord,
                rendered_username=lab_username,
                rendered_username_coord=lab_username_coord,
            )
            self.cat_boxes.append(cat_box)

        # HiScores
        hiscores_btn_font = pygame.font.Font(None, 60)
        self.hiscores_btn = hiscores_btn_font.render("HiScores", 1, YELLOW)
        x, y = (
            SIZE[0] / 4 - self.hiscores_btn.get_width() / 2,
            SIZE[1] - 20 - self.hiscores_btn.get_height(),
        )
        self.hiscores_btn_coord = (x, y)
        self.hiscores_btn_rect = (
            10,
            y - 15,
            SIZE[0] / 2 - 21,
            self.hiscores_btn.get_height() + 30,
        )

        # Recent players
        self.recent_scores_btn = hiscores_btn_font.render(
            "Recent Players",
            1,
            YELLOW,
        )
        x = SIZE[0] / 2 + SIZE[0] / 4 - self.recent_scores_btn.get_width() / 2
        self.recent_scores_btn_coord = (x, y)
        self.recent_scores_btn_rect = (
            SIZE[0] / 2 + 10,
            y - 15,
            SIZE[0] / 2 - 21,
            self.recent_scores_btn.get_height() + 30,
        )

    def draw(self, screen):
        screen.fill(BLACK)
        screen.blit(self.lab_head, (align_h(self.lab_head), self.init_line_pos))

        for cat_box in self.cat_boxes:
            pygame.draw.rect(screen, WHITE, cat_box.rect, 1)
            screen.blit(cat_box.rendered_title, cat_box.rendered_title_coord)
            screen.blit(cat_box.rendered_hiscore, cat_box.rendered_hiscore_coord)
            screen.blit(cat_box.rendered_username, cat_box.rendered_username_coord)

        screen.blit(
            self.crown_img,
            self.crown_img_coord,
        )

        # HiScore
        screen.blit(self.hiscores_btn, self.hiscores_btn_coord)
        pygame.draw.rect(
            screen,
            YELLOW,
            self.hiscores_btn_rect,
            1,
        )

        # Recent Score
        screen.blit(self.recent_scores_btn, self.recent_scores_btn_coord)
        pygame.draw.rect(
            screen,
            YELLOW,
            self.recent_scores_btn_rect,
            1,
        )

        pygame.display.flip()

    def selected_category_box(self, click_pos):
        for cat_box in self.cat_boxes:
            if rect_is_clicked(cat_box.rect, click_pos):
                return cat_box.title
        return None

    def clicked_hiscores(self, click_pos):
        return rect_is_clicked(self.hiscores_btn_rect, click_pos)

    def clicked_recent_scores(self, click_pos):
        return rect_is_clicked(self.recent_scores_btn_rect, click_pos)


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


class QuickPickButton:
    def __init__(self, value, rendered_btn_txt, x, y):
        self.rendered_btn_txt = rendered_btn_txt
        self.value = value
        self.btn_label_x = x
        self.btn_label_y = y

        self.left = self.btn_label_x - 15
        self.top = self.btn_label_y - 15
        self.width = self.rendered_btn_txt.get_width() + 30
        self.height = self.rendered_btn_txt.get_height() + 30

    @property
    def right(self):
        return self.left + self.width

    @property
    def bottom(self):
        return self.top + self.height

    def draw(self, screen):
        screen.blit(self.rendered_btn_txt, (self.btn_label_x, self.btn_label_y))
        pygame.draw.rect(
            screen,
            YELLOW,
            (self.left, self.top, self.width, self.height),
            1,
        )


def win_screen(screen, recent_usernames: List[str]) -> List[str]:
    """Display the Win screen where user can enter his username"""
    line_pos = SIZE[1] / 3
    max_username_len = 12  # Fits main screen
    firstname_input = eztext.Input(
        maxlength=max_username_len,
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

    # QuickPick usernames buttons
    quickpick_btns = []
    x_subd = 8
    y_subd = 8
    qp_pos = [((x_subd, xi), (y_subd, yi)) for yi in (3, 4, 5) for xi in range(3)]

    for idx, username in enumerate(recent_usernames[:9]):
        qp_font = pygame.font.Font(None, 30)
        qp_btn = qp_font.render(username, 1, YELLOW)

        h_cols, v_cols = qp_pos[idx]
        quickpick_btns.append(
            QuickPickButton(
                username,
                qp_btn,
                x=align_h(qp_btn, *h_cols) + 20,
                y=align_v(qp_btn, *v_cols),
            )
        )

    while True:
        clock.tick(FPS)
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                pos = (pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])

                submit_btn_clicked = _box_clicked(submit_btn, pos)
                if submit_btn_clicked:
                    print("Submit button clicked")

                    def consumer(text):
                        inputboxes[0].value = text
                        print("Current text : %s" % text)

                    # Initializes and activates vkeyboard
                    layout = VKeyboardLayout(VKeyboardLayout.AZERTY, height_ratio=1)
                    surf = Surface((600, 300))
                    keyboard = VKeyboard(
                        surf, consumer, layout, renderer=VKeyboardRenderer.DARK
                    )

                    while True:
                        events = pygame.event.get()

                        # Update internal variables
                        keyboard.update(events)

                        # Draw the keyboard
                        keyboard.draw(surf)

                        if keyboard.get_text().endswith("#"):
                            keyboard.disable()
                            break

                        #
                        # Perform other tasks here
                        #

                        # Update the display
                        screen.blit(surf, (0, 300))
                        pygame.display.flip()

                    # return [ib.value for ib in inputboxes]

                for i, ib in enumerate(inputboxes):
                    ib_selected = _box_clicked(ib, pos)
                    if ib_selected:
                        print(f"Input box {i} selected - change focus")
                        inputboxes[ib_idx].set_focus(False)
                        ib.set_focus(True)
                        ib_idx = i
                        break

                for quickpick_btn in quickpick_btns:
                    if _box_clicked(quickpick_btn, pos):
                        inputboxes[0].value = quickpick_btn.value

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

        # username QuickPick
        for quickpick_btn in quickpick_btns:
            quickpick_btn.draw(screen)

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
