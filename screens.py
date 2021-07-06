import pygame
import eztext
import sys

# set SIZE of the screen
SIZE = width, height = 1280, 800

# define colours
BLUE = 26, 0, 255
ORANGE = 255, 165, 0
BLACK = 0, 0, 0
WHITE = 255, 255, 255
YELLOW = 255, 255, 0
RED = 255, 0, 0
GREEN = 0, 255, 0

top = 0


def align_h(label, cols=1, col=0, width=SIZE[0]):
    col_width = width / cols
    return ((col_width - label.get_width()) / 2) + col_width * col


def align_v(label, rows=1, row=0, height=SIZE[1]):
    row_height = height / rows
    return ((row_height - label.get_height()) / 2) + row_height * row


def menu_screen(screen, scores):
    global top

    line_pos = 15
    screen.fill(BLACK)  # change the colours if needed
    fnt_head = pygame.font.Font(None, 288)
    fnt_title = pygame.font.Font(None, 84)
    lab_head = fnt_head.render("Whack-A-Pi", 1, (YELLOW))
    screen.blit(lab_head, (align_h(lab_head), line_pos))
    line_pos += lab_head.get_height() + 60

    fnt_score = pygame.font.Font("digital-7 (mono).ttf", 200)

    top = line_pos
    max_width = SIZE[0] / 3
    max_height = SIZE[1] - top
    for i in range(0, 3):
        rect = left, top, width, height = (
            (max_width * i) + 10,
            top,
            max_width - 20,
            max_height - 10,
        )
        pygame.draw.rect(screen, WHITE, rect, 1)
        if i == 0:
            title = "12 and under"
        elif i == 1:
            title = "13 to 17"

        elif i == 2:
            title = "Adult"

        line_pos = top  # reset the vertical cursor
        line_pos += 45
        lab_title = fnt_title.render(title, 1, (WHITE))
        screen.blit(lab_title, (align_h(lab_title, 3, i), line_pos))

        line_pos += lab_title.get_height() + 30
        lab_score = fnt_score.render("{:0>3d}".format(scores[i][0]), 1, (BLUE))
        screen.blit(lab_score, (align_h(lab_score, 3, i), line_pos))

        line_pos += lab_score.get_height() + 30
        lab_name1 = fnt_title.render(scores[i][1], 1, (ORANGE))
        screen.blit(lab_name1, (align_h(lab_name1, 3, i), line_pos))

        line_pos += lab_name1.get_height() + 15
        lab_name2 = fnt_title.render(scores[i][2], 1, (ORANGE))
        screen.blit(lab_name2, (align_h(lab_name2, 3, i), line_pos))

    pygame.display.flip()


def game_screen(screen, elapsed, score, hiscore, wait=False):
    screen.fill(BLACK)  # change the colours if needed
    fnt_title = pygame.font.Font(None, 144)
    lab_time_title = fnt_title.render("Time", 1, (WHITE))
    screen.blit(lab_time_title, (align_h(lab_time_title, 2, 0), 15))

    fnt_title = pygame.font.Font(None, 144)
    lab_score_title = fnt_title.render("Score", 1, (WHITE))
    screen.blit(lab_score_title, (align_h(lab_score_title, 2, 1), 15))

    if wait:
        lab_wait = fnt_title.render("Press light when ready", 1, (YELLOW))
        screen.blit(
            lab_wait, (align_h(lab_wait, 1, 0), 15 + lab_score_title.get_height())
        )

    font = pygame.font.Font("digital-7 (mono).ttf", 432)

    lab_time = font.render("{:0>2d}".format(elapsed), 1, (ORANGE))
    screen.blit(lab_time, (align_h(lab_time, 2, 0), align_v(lab_time)))

    lab_score = font.render("{:0>3d}".format(score), 1, (BLUE))
    screen.blit(lab_score, (align_h(lab_score, 2, 1), align_v(lab_score)))

    fnt_subtitle = pygame.font.Font(None, 120)
    lab_hi_title = fnt_subtitle.render("Hi-Score:", 1, (WHITE))

    fnt_hiscore = pygame.font.Font("digital-7 (mono).ttf", 144)
    lab_hi_score = fnt_hiscore.render("{:0>3d}".format(hiscore), 1, (BLUE))

    score_top = SIZE[1] - lab_hi_score.get_height() - 30
    hi_top = score_top + (lab_hi_score.get_height() - lab_hi_title.get_height()) / 2

    screen.blit(lab_hi_title, (align_h(lab_hi_title, 4, 2) + 25, hi_top))
    screen.blit(lab_hi_score, (align_h(lab_hi_score, 4, 3), score_top))

    pygame.display.flip()


def _draw_win_screen(screen):
    global btn
    screen.fill(BLACK, (0, 0, SIZE[0] / 2, SIZE[1]))
    fnt_head = pygame.font.Font(None, 144)
    lab_head = fnt_head.render("High Score!", 1, (YELLOW))
    screen.blit(lab_head, (align_h(lab_head, 2, 0), 15))

    lab_btn = fnt_head.render(
        "Submit",
        1,
        YELLOW,
    )
    x = align_h(lab_btn, 2, 0)
    y = SIZE[1] - 30 - lab_btn.get_height()
    screen.blit(lab_btn, (x, y))
    btn = pygame.draw.rect(
        screen,
        YELLOW,
        (x - 15, y - 15, lab_btn.get_width() + 30, lab_btn.get_height() + 30),
        1,
    )


def win_screen(screen):
    line_pos = SIZE[1] / 3
    SPACE = 50
    inputboxes = []
    inputboxes.append(
        eztext.Input(
            maxlength=30,
            color=WHITE,
            focuscolor=YELLOW,
            prompt="First: ",
            x=15,
            y=line_pos,
            hasfocus=True,
        )
    )
    line_pos += SPACE
    inputboxes.append(
        eztext.Input(
            maxlength=30,
            color=WHITE,
            focuscolor=YELLOW,
            prompt="Last: ",
            x=15,
            y=line_pos,
        )
    )
    line_pos += SPACE
    inputboxes.append(
        eztext.Input(
            maxlength=15,
            color=WHITE,
            focuscolor=YELLOW,
            prompt="Twitter: @",
            x=15,
            y=line_pos,
        )
    )
    line_pos += SPACE
    inputboxes.append(
        eztext.Input(
            maxlength=30,
            color=WHITE,
            focuscolor=YELLOW,
            prompt="Cont: ",
            x=15,
            y=line_pos,
        )
    )

    ib_idx = 0
    while True:
        # clock.tick(30)
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                pos = (pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
                if btn.top <= pos[1] <= btn.bottom:
                    if btn.left <= pos[0] <= btn.right:
                        ret = []
                        for ib in inputboxes:
                            ret.append(ib.value)
                        return ret

                # print (pos)
                for i in range(0, len(inputboxes)):
                    ib = inputboxes[i]
                    print(ib.top, ib.bottom, ib.left, ib.right)
                    if ib.top <= pos[1] <= ib.bottom:
                        if ib.left <= pos[0] <= ib.right:
                            # print(ib.prompt)
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
                    if inputboxes[0].value != "" and inputboxes[1].value != "":
                        ret = []
                        for ib in inputboxes:
                            ret.append(ib.value)
                        return ret

        _draw_win_screen(screen)
        inputboxes[ib_idx].update(events)
        for ib in inputboxes:
            ib.draw(screen)
        pygame.display.flip()


def lose_screen(screen):
    print("Display Lose screen")
    screen.fill(BLACK, (0, 0, SIZE[0] / 2, SIZE[1]))
    fnt_head = pygame.font.Font(None, 144)
    lab_head = fnt_head.render("Click", 1, (YELLOW))
    screen.blit(lab_head, (align_h(lab_head, 2, 0), align_v(lab_head, 3, 0)))

    lab_head = fnt_head.render("to", 1, (YELLOW))
    screen.blit(lab_head, (align_h(lab_head, 2, 0), align_v(lab_head, 3, 1)))

    lab_head = fnt_head.render("Continue", 1, (YELLOW))
    screen.blit(lab_head, (align_h(lab_head, 2, 0), align_v(lab_head, 3, 2)))
    pygame.display.flip()
