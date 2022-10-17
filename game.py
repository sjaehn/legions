import os
import pygame
import math
import random

from map import Map

WIDTH = 1800
HEIGHT = 880
XFRAME = 50
YFRAME = 50
XOFFSET = 0
YOFFSET = -80

VICTORY_TEXT = ["Veni, vidi, vici", "Gloria victori", "Victoria nostra est", "Victrix causa deis placuit"]
FAIL_TEXT = ["Quintili Vare, legiones redde", "Quem dei diligunt, adulescens moritur",
             "Requiescat in pace", "Contra vim mortis non est medicamen in hortis"]
ISOLATED_TEXT = ["Errare humanum est",
                 "Quo vadis?"]
TIMEOUT_TEXT = ["Tempus elapsum", "Tempus pecunia est", "Acta est fabula", "Sero venientibus ossa"]

LEVELS = [(4, 120), (4, 60), (5, 120), (5, 60), (6, 120), (6, 60), [5, 30], [6, 30], [6, 20], [6, 10], [6, 5]]


def to_roman(number):
    roman = ""
    m = int(number / 1000)
    number -= m * 1000
    roman += "M" * m
    cm = int(number / 900)
    number -= cm * 900
    roman += "CM" * cm
    d = int(number / 500)
    number -= d * 500
    roman += "D" * d
    cd = int(number / 400)
    number -= cd * 400
    roman += "CD" * cd
    c = int(number / 100)
    number -= c * 100
    roman += "C" * c
    xc = int(number / 90)
    number -= xc * 90
    roman += "XC" * xc
    l = int(number / 50)
    number -= l * 50
    roman += "L" * l
    xl = int(number / 40)
    number -= xl * 40
    roman += "XL" * xl
    x = int(number / 10)
    number -= x * 10
    roman += "X" * x
    ix = int(number / 9)
    number -= ix * 9
    roman += "IX" * ix
    v = int(number / 5)
    number -= v * 5
    roman += "V" * v
    iv = int(number / 4)
    number -= iv * 4
    roman += "IV" * iv
    roman += "I" * number
    return roman


def main():

    def mouse_down(pos):
        nonlocal game_pos
        nonlocal game_count
        x, y = pos
        print("mouse_down", x, y)
        if (x > 0) and (x < WIDTH) and (y > 0) and (y < HEIGHT):
            xi = int(x / (WIDTH / game_map.width))
            yi = int(y / (HEIGHT / game_map.height))
            print("xi, yi: ", xi, yi)
            if ((xi + 1, yi) == game_pos) or ((xi - 1, yi) == game_pos) or ((xi, yi + 1) == game_pos) or (
                    (xi, yi - 1) == game_pos):
                field = game_map.map[xi][yi]
                if field is not None:
                    value = field[0] * field[1]
                    if value > 0:
                        if value < game_count:
                            game_map.map[game_pos[0]][game_pos[1]] = None
                            game_pos = (xi, yi)
                            game_count += game_map.force_level(game_pos)
                            return True
                        return False
        return True

    def to_3d(pos):
        x, y = pos
        y1 = HEIGHT / (2.0 ** float((HEIGHT - y) / HEIGHT))
        x1 = WIDTH / 2 + (x - WIDTH / 2) * y1 / HEIGHT
        pos1 = (XFRAME + XOFFSET + int(x1), YFRAME + YOFFSET + int(y1))
        return pos1

    def to_2d(pos):
        x, y = pos
        x -= XFRAME + XOFFSET
        y -= YFRAME + YOFFSET
        y1 = HEIGHT - HEIGHT * math.log2(HEIGHT / y)
        x1 = (x - WIDTH / 2) * HEIGHT / y + WIDTH / 2
        pos1 = (int(x1), int(y1))
        return pos1

    def play_music():
        snd_idx = random.randint(1, 3)
        pygame.mixer.music.load("/home/sven/dev/py/legions/track0" + str(snd_idx) + ".ogg")
        pygame.mixer.music.play()

    def load_image(name, colorkey=None):
        fullname = os.path.join('data', name)
        try:
            image = pygame.image.load(fullname)
        except pygame.error as message:
            print('Cannot load image:', name)
            raise SystemExit(message)
        image = image.convert_alpha()

        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))

            image.set_colorkey(colorkey, pygame.SRCALPHA)

        return image, image.get_rect()

    def text_field(text, rect):
        x, y, w, h = rect
        words = [word.split(' ') for word in text.splitlines()]

        # Analyze text
        text_buffer = [""]
        text_height = 0
        for line in words:
            line_height = 0
            for word in line:
                words_img = font.render(text_buffer[-1] + word, True, (0, 0, 0))
                words_width, words_height = words_img.get_size()

                if words_height > line_height:
                    line_height = words_height

                if words_width >= w:
                    text_height += line_height
                    line_height = 0
                    text_buffer.append("")

                text_buffer[-1] += word + " "

            text_height += line_height
            text_buffer.append("")

        # Print text on screen
        height_count = 0
        for line in text_buffer:
            line_img = font.render(line, True, (0, 0, 0))
            line_width, line_height = line_img.get_size()
            line_pos = (x + int(0.5 * w - 0.5 * line_width), y + int(0.5 * h - 0.5 * text_height + height_count))
            screen.blit(line_img, line_pos)
            height_count += line_height
        pygame.display.flip()

    def msg_box(text, buttons, response, rect):
        x, y, w, h = rect

        # Draw background
        screen.blit(bg_marble[0], (x, y), (0, 0, w, h))
        pygame.draw.rect(screen, (32, 32, 32), (x + 5, y + 5, w - 10, h - 10), 1)

        # Draw text
        button_height = 0
        button_padding = 0
        if buttons:
            button_height = 30
            button_padding = 20

        text_field(text, (x + 10, y + 10, w - 20, h - 20 - button_height - 2 * button_padding))

        # Draw buttons
        if buttons:
            for button_text in buttons:
                button_idx = buttons.index(button_text)
                print(button_idx)
                bx = int(x + 0.5 * w - 0.5 * len(buttons) * 200 - 0.5 * (len(buttons) - 1) * button_padding +
                         button_idx * 200 + button_idx * button_padding)
                by = int(y + h - 10 - button_padding - button_height)
                bw = 200
                bh = button_height
                text_field(button_text, (bx, by, bw, bh))
                pygame.draw.rect(screen, (32, 32, 32), (bx, by, bw, bh), 1)

            pygame.display.flip()

        # Wait until button pressed
        while response:
            for event2 in pygame.event.get():
                if event2.type == pygame.QUIT:
                    quit(0)

                if event2.type == MUSIC_END:
                    play_music()

                if event2.type == pygame.MOUSEBUTTONDOWN:
                    if not buttons:
                        return 0

                    else:
                        for button_text in buttons:
                            mx, my = pygame.mouse.get_pos()

                            button_idx = buttons.index(button_text)
                            print(button_idx)
                            bx = int(
                                x + 0.5 * w - 0.5 * len(buttons) * 200 - 0.5 * (len(buttons) - 1) * button_padding +
                                button_idx * 200 + button_idx * button_padding)
                            by = int(y + h - 10 - button_padding - button_height)
                            bw = 200
                            bh = button_height

                            if (mx >= bx) and (mx <= bx + bw) and (my >= by) and (my <= by + bh):
                                return button_idx

    def draw():
        screen.blit(background, (0, 0))

        for x in range(game_map.width):
            for y in range(game_map.height):

                # Draw fields
                if game_map.map[x][y] is None:
                    w = 1

                elif not game_map.contains_legion((x, y)):
                    w = 1

                elif (x, y) == game_pos:
                    w = 0

                elif ((x + 1, y) == game_pos) or ((x - 1, y) == game_pos) or ((x, y + 1) == game_pos) or (
                        (x, y - 1) == game_pos):
                    w = 4

                else:
                    w = 1

                pygame.draw.polygon(screen,
                                    (255, 0, 0, 32),
                                    [to_3d((x * (WIDTH / game_map.width), y * (HEIGHT / game_map.height))),
                                     to_3d(((x + 1) * (WIDTH / game_map.width), y * (HEIGHT / game_map.height))),
                                     to_3d(((x + 1) * (WIDTH / game_map.width), (y + 1) * (HEIGHT / game_map.height))),
                                     to_3d((x * (WIDTH / game_map.width), (y + 1) * (HEIGHT / game_map.height)))],
                                    width=w)

                # Draw soldiers
                if game_map.map[x][y] is None:
                    pass

                elif not game_map.contains_legion((x, y)):
                    b_idx = game_map.map[x][y][0]
                    print("b_idx:", b_idx)
                    bw = 0.9 * (to_3d(((x + 1) * (WIDTH / game_map.width), (y + 0.5) * (HEIGHT / game_map.height)))[0] -
                                to_3d((x * (WIDTH / game_map.width), (y + 0.5) * (HEIGHT / game_map.height)))[0])
                    bx, by = to_3d(((x + 0.5) * (WIDTH / game_map.width), (y + 0.5) * (HEIGHT / game_map.height)))
                    bx -= 0.5 * bw
                    by -= 0.375 * bw

                    b = barrier[b_idx]
                    b1 = pygame.Surface(b[0].get_size(), pygame.SRCALPHA, 32)
                    b1.convert_alpha()
                    b1.blit(b[0], (0, 0))
                    b1 = pygame.transform.scale(b1, (int(bw), int(0.5 * bw)))
                    screen.blit(b1, (bx, by))

                elif (x, y) == game_pos:
                    pass

                else:
                    xm = 2 ** size + 2
                    ym = 2 ** size + 2
                    dx1, dy1 = to_3d(((x + (0.5 * xm) / xm) * (WIDTH / game_map.width),
                                      (y + (0.5 * ym) / ym) * (HEIGHT / game_map.height)))
                    dx2, dy2 = to_3d(((x + (0.5 * xm + 1.2) / xm) * (WIDTH / game_map.width),
                                      (y + (0.5 * ym) / ym) * (HEIGHT / game_map.height)))
                    dx = dx2 - dx1
                    for ys in range(game_map.map[x][y][1] - 1, -1, -1):
                        for xs in range(game_map.map[x][y][0]):
                            sx, sy = to_3d(((x + 0.5 + (0.5 * game_map.map[x][y][0] - xs) / xm) *
                                            (WIDTH / game_map.width),
                                            (y + 0.5 + (0.5 * game_map.map[x][y][1] - ys) / ym) *
                                            (HEIGHT / game_map.height)))
                            s1 = pygame.Surface(soldier[0].get_size(), pygame.SRCALPHA, 32)
                            s1.convert_alpha()
                            s1.blit(soldier[0], (0, 0))
                            s1 = pygame.transform.scale(s1, (int(dx), int(2.5 * dx)))
                            screen.blit(s1, (int(sx - dx), int(sy - 2.5 * dx)))

                # Draw labels
                if game_map.contains_legion((x, y)):
                    l_font = pygame.font.Font(path + "Cinzel-Bold.ttf",
                                              to_3d((0, (y + 0.625) * (HEIGHT / game_map.height)))[1] -
                                              to_3d((0, (y + 0.375) * (HEIGHT / game_map.height)))[1])

                    if (x, y) == game_pos:
                        text1 = l_font.render(str(game_count), True, (255, 255, 255))
                        text2 = l_font.render(str(game_count), True, (0, 0, 0))

                    else:
                        text1 = l_font.render(str(game_map.map[x][y][0]) + ' x ' + str(game_map.map[x][y][1]), True,
                                              (255, 255, 255))
                        text2 = l_font.render(str(game_map.map[x][y][0]) + ' x ' + str(game_map.map[x][y][1]), True,
                                              (0, 0, 0))

                    pos = to_3d(((x + 0.5) * (WIDTH / game_map.width), (y + 0.5) * (HEIGHT / game_map.height)))
                    h = to_3d((0, (y + 0.1) * (HEIGHT / game_map.height)))[1]
                    pos2 = (pos[0] + 2, h + 2)
                    textpos = text2.get_rect(center=pos2)
                    screen.blit(text2, textpos)
                    pos1 = (pos[0], h)
                    textpos = text1.get_rect(center=pos1)
                    screen.blit(text1, textpos)

                # Draw level and time
                t_min = int(time / 60)
                t_ds = int((time - 60 * t_min) / 10)
                t_s = time - 60 * t_min - 10 * t_ds
                time_img = font.render("Level " + to_roman(level_idx) + "      " + str(t_min) + ":" + str(t_ds) + str(t_s),
                                       True, (255, 255, 255))
                time_pos = (WIDTH - 200, 20)
                screen.blit(time_img, time_pos)

        pygame.display.flip()

    # Init
    random.seed()
    path = os.getcwd() + "/"

    pygame.init()
    screen = pygame.display.set_mode((WIDTH + 2 * XFRAME, HEIGHT + 2 * YFRAME))
    pygame.display.set_caption("Legions")

    bg_marble = load_image(path + "marble.jpg")

    pygame.mixer.init()
    play_music()
    MUSIC_END = pygame.USEREVENT + 1
    pygame.mixer.music.set_endevent(MUSIC_END)

    TIME_EVENT = pygame.USEREVENT + 2

    font = pygame.font.Font(path + "Cinzel-Regular.ttf", 24)

    # Soldier
    soldier = load_image(path + "soldier.png")

    # Barrier
    barrier = []
    for n in range(1, 5):
        barrier.append(load_image(path + "barrier0" + str(n) + ".png"))

    game_on = True

    msg_box("Legions\n\nEmperor, defeat foreign legions and take over their soldiers.. "
            "Then you will be honored with glory and fame in Rome!", None, True, (500, 200, 900, 500))

    while game_on:
        alive = True

        for level in LEVELS:
            size, time = level
            level_idx = LEVELS.index(level) + 1
            if not alive:
                break

            pygame.time.set_timer(TIME_EVENT, 0)        # Disable timer
            msg_box("Create level " + to_roman(level_idx) + " ...", None, False, (600, 380, 700, 140))
            game_map = Map((size, size), 1, 2 ** size)
            game_pos = game_map.start
            game_count = game_map.force_level(game_pos)
            pygame.time.set_timer(TIME_EVENT, 1000)     # Re-enable timer

            # Background
            img_idx = random.randint(1, 5)
            bgimage = load_image(path + "bg0" + str(img_idx) + ".jpg")
            background = pygame.Surface(screen.get_size(), pygame.SRCALPHA, 32)
            background = background.convert_alpha()
            background.blit(bgimage[0], (0, 0))
            draw()

            # Fighting
            fighting = True
            while fighting:
                # Handle Input Events
                for event in pygame.event.get():

                    if event.type == MUSIC_END:
                        play_music()

                    if event.type == TIME_EVENT:
                        time -= 1
                        draw()

                        if time <= 0:
                            msg_idx = random.randint(0, len(TIMEOUT_TEXT) - 1)
                            msg_box(TIMEOUT_TEXT[msg_idx], None, True, (500, 400, 900, 100))
                            alive = False
                            fighting = False

                    if event.type == pygame.QUIT:
                        quit(0)

                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        pos = pygame.mouse.get_pos()
                        pos = to_2d(pos)
                        b = mouse_down(pos)

                        if not b:
                            msg_idx = random.randint(0, len(FAIL_TEXT) - 1)
                            msg_box(FAIL_TEXT[msg_idx], None, True, (500, 400, 900, 100))
                            alive = False
                            fighting = False

                        draw()

                        if game_map.is_empty():
                            msg_idx = random.randint(0, len(VICTORY_TEXT) - 1)
                            msg_box(VICTORY_TEXT[msg_idx], None, True, (500, 400, 900, 100))
                            fighting = False

                        elif not game_map.has_neighbors(game_pos):
                            msg_idx = random.randint(0, len(ISOLATED_TEXT) - 1)
                            msg_box(ISOLATED_TEXT[msg_idx], None, True, (500, 400, 900, 100))
                            alive = False
                            fighting = False

        if alive:
            msg_box("Game completed!", None, True, (500, 400, 900, 100))

        if msg_box("A new fight?", ["In proelium", "Finis"], True, (500, 300, 900, 300)) == 1:
            game_on = False

    pygame.quit()


if __name__ == "__main__":
    main()
