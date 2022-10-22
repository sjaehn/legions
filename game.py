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
ANIMATION_TIME = 300

VICTORY_TEXT = [[("la", "Veni, vidi, vici"), ("en", "I came; I saw; I conquered")],
                [("la", "Gloria victori"), ("en", "Glory to the winner")],
                [("la", "Victoria nostra est"), ("en", "Victory is ours")],
                [("la", "Victrix causa deis placuit"), ("en", "The victorious cause pleased the gods")]]

FAIL_TEXT = [[("la", "Quintili Vare, legiones redde"), ("en", "Quintilius Varus, give me back my legions")],
             [("la", "Quem di diligunt, adulescens moritur"), ("en", "He who is loved by the gods will die young")],
             [("la", "Requiescat in pace"), ("en", "Rest in peace")],
             [("la", "Contra vim mortis non est medicamen in hortis"),
              ("en", "No sage grows in the gardens against the power of death")],
             [("la", "Mors ultima linea rerum est"), ("en", "Death is the final limit of things")],
             [("la", "Nec mors humano subiacet arbitrio"), ("en", "Nor is death subject to human discretion")],
             [("la", "Nihil verum nisi mors"), ("en", "Nothing is true but death")],
             [("la", "Dulce et decorum est pro patria mori"),
              ("en", "It is sweet and honorable to die for the fatherland")],
             [("la", "Ut desint vires tamen est laudanda voluntas"),
              ("en", "Although the power is lacking, the will is commendable")]]

ISOLATED_TEXT = [[("la", "Errare humanum est"), ("en", "To err is human")],
                 [("la", "Quo vadis?"), ("en", "Whither goest thou?")]]

TIMEOUT_TEXT = [[("la", "Tempus elapsum"), ("en", "Time is over")],
                [("la", "Tempus pecunia est"), ("en", "Time is money")],
                [("la", "Acta est fabula"), ("en", "The game is over")],
                [("la", "Sero venientibus ossa"), ("en", "The late one only gets the bones")],
                [("la", "Diem perdidi"), ("en", "I lost a day")]]

WELCOME_TEXT = [("en", "Emperor, defeat foreign legions and take over their soldiers. "
                       "Then you will be honored with glory and fame in Rome!")]

NEW_GAME_TEXT = [("la", "In proelium?"), ("en", "Into a new battle?")]

LEVELS = [(4, 120), (4, 60), (5, 120), (5, 60), (6, 120), (6, 60), [5, 30], [6, 30], [6, 20], [6, 15], [6, 10], [6, 5]]


def translate_text(text, lang):
    """
    Selects the text for the provided language from a text dictionary
    
    :param text: text dictionary as a list of tuples containing the language code and the text
    :param lang: language code
    :return: selected text
    """

    for t in text:
        lc, tx = t
        if lc == lang:
            return tx

    return ""


def to_roman(number):
    """
    Converts an integer number to a roman number as a string

    :param number: integer
    :return: roman number as a string
    """

    R_NUMBERS = [("M", 1000), ("CM", 900), ("D", 500), ("CD", 400), ("C", 100), ("XC", 90), ("L", 50), ("XL", 40),
                 ("X", 10), ("IX", 9), ("V", 5), ("IV", 4), ("I", 1)]
    roman = ""
    for r in R_NUMBERS:
        symbol, value = r
        count = int(number / value)
        number -= count * value
        roman += symbol * count
    return roman


def main():

    def enter(pos):
        """
        Tries to enter a new field. Changes game_pos and game_count if the field can be entered.

        :param pos: position of the new field
        :return: True if the field provided by pos can't be entered or the the legion of the field provided by pos can
        be defeated. Otherwise False.
        """

        nonlocal game_pos
        nonlocal game_count
        x, y = pos

        if (x > 0) and (x < WIDTH) and (y > 0) and (y < HEIGHT):
            xi = int(x / (WIDTH / game_map.width))
            yi = int(y / (HEIGHT / game_map.height))
            if ((xi + 1, yi) == game_pos) or ((xi - 1, yi) == game_pos) or ((xi, yi + 1) == game_pos) or (
                    (xi, yi - 1) == game_pos):
                field = game_map.map[xi][yi]
                if field is not None:
                    value = field[0] * field[1]
                    if value > 0:
                        animate_fight((xi, yi))
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
        pygame.mixer.music.load(os.getcwd() + "/track0" + str(snd_idx) + ".ogg")
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
        """
        Draws a multi line text on the screen. Adds line breaks if needed.

        :param text: text string, or a tuple of a text string and a font, or a list thereof to be displayed
        :param rect: position and extends of the text
        """

        x, y, w, h = rect
        text_buffer = []
        text_height = 0
        text_font = font

        # Convert text to list
        if isinstance(text, str):
            text_list = [text]
        elif isinstance(text, tuple):
            text_list = [text]
        elif isinstance(text, list):
            text_list = text
        else:
            return

        for block in text_list:
            # Analyze block data format
            if isinstance(block, tuple):
                block_text, text_font = block
            else:
                block_text = block

            words = [word.split(' ') for word in block_text.splitlines()]
            block_buffer = []

            # Analyze block text
            for line in words:
                line_height = 0
                block_buffer.append("")
                for word in line:
                    words_img = text_font.render(block_buffer[-1] + word, True, (0, 0, 0))
                    words_width, words_height = words_img.get_size()

                    if words_height > line_height:
                        line_height = words_height

                    if words_width >= w:
                        text_height += line_height
                        line_height = 0
                        block_buffer.append("")

                    block_buffer[-1] += word + " "

                text_height += line_height

            # Write text buffer
            text_buffer.append((block_buffer, text_font))

        # Print text on screen
        height_count = 0
        for block in text_buffer:
            block_text, text_font = block

            for line in block_text:
                line_img = text_font.render(line, True, (0, 0, 0))
                line_width, line_height = line_img.get_size()
                line_pos = (x + int(0.5 * w - 0.5 * line_width), y + int(0.5 * h - 0.5 * text_height + height_count))
                screen.blit(line_img, line_pos)
                height_count += line_height
        pygame.display.flip()

    def msg_box(text, buttons, response, rect):
        """
        Draws a message box on the screen and optionally waits for any mouse click events.

        :param text: text string, or a tuple of a text string and a font, or a list thereof to be displayed
        :param buttons: optional, list of button text strings to be displayed on the bottom of the box
        :param response: True if the program has to wait until a click on one of the buttons (if provided) or on any
        position (if no buttons provided), otherwise False
        :param rect: position and extends of the box on the screen
        :return: button number (if buttons provided), otherwise 0
        """

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
                            bx = int(
                                x + 0.5 * w - 0.5 * len(buttons) * 200 - 0.5 * (len(buttons) - 1) * button_padding +
                                button_idx * 200 + button_idx * button_padding)
                            by = int(y + h - 10 - button_padding - button_height)
                            bw = 200
                            bh = button_height

                            if (mx >= bx) and (mx <= bx + bw) and (my >= by) and (my <= by + bh):
                                return button_idx

        return 0

    def animate_fight(pos):
        x, y = pos
        xm = 2 ** size + 2
        ym = 2 ** size + 2
        dx1, dy1 = to_3d(((x + (0.5 * xm) / xm) * (WIDTH / game_map.width),
                          (y + (0.5 * ym) / ym) * (HEIGHT / game_map.height)))
        dx2, dy2 = to_3d(((x + (0.5 * xm + 1.2) / xm) * (WIDTH / game_map.width),
                          (y + (0.5 * ym) / ym) * (HEIGHT / game_map.height)))
        dx = dx2 - dx1
        legion = game_map.map[x][y]
        nr_objs = int((legion[0] + 3) * 0.25 * (legion[1] + 3))
        obj_size = 2 * dx

        # Seed objects
        objs = []
        for o in range(nr_objs):
            o_dx = random.randint(-obj_size, obj_size)
            o_dy = random.randint(-obj_size, obj_size)
            o_x = dx1 + random.randint(-int(0.5 * legion[0] * dx), int(0.5 * legion[0] * dx)) + o_dx
            o_y = int(dy1 + o_dy - 0.5 * obj_size)
            o_pos = (o_x, o_y)
            o_size = random.randint(int(0.5 * obj_size), obj_size)
            o_start = random.randint(0, int(0.5 * ANIMATION_TIME))
            objs.append((o_pos, o_size, o_start))

        # Run animation
        t0 = pygame.time.get_ticks()
        sound_idx = random.randint(0, 2)
        pygame.mixer.Sound.play(sword_sound[sound_idx])
        while pygame.time.get_ticks() < t0 + ANIMATION_TIME:
            draw()
            t = pygame.time.get_ticks() - t0
            for o in objs:
                o_pos, o_size, o_start = o
                o_x, o_y = o_pos
                if (t >= o_start) and (t <= o_start + 0.5 * ANIMATION_TIME):
                    s = pygame.Surface((2 * o_size, 2 * o_size), pygame.SRCALPHA)
                    alpha = int(255 - 255 * ((t - o_start) / (0.5 * ANIMATION_TIME)) ** 2)
                    s.set_alpha(alpha)
                    pygame.draw.circle(s,
                                       (255, 255, 255),
                                       (int(o_size), int(o_size)),
                                       (t - o_start) / int(0.5 * ANIMATION_TIME) * o_size, 0)
                    screen.blit(s, (o_x - o_size, o_y - o_size))
            pygame.display.flip()

    def draw():
        # Draw background first
        screen.blit(background, (0, 0))

        for x in range(game_map.width):
            for y in range(game_map.height):

                # Draw fields
                if game_map.map[x][y] is None:
                    w = 1   # 1px border

                elif not game_map.contains_legion((x, y)):
                    w = 1   # 1px border

                elif ((x, y) == game_pos) and alive:
                    w = 0   # Filled

                elif ((x + 1, y) == game_pos) or ((x - 1, y) == game_pos) or ((x, y + 1) == game_pos) or (
                        (x, y - 1) == game_pos):
                    w = 4   # 1px border

                else:
                    w = 1   # 1px border

                pygame.draw.polygon(screen,
                                    (255, 0, 0, 32),
                                    [to_3d((x * (WIDTH / game_map.width), y * (HEIGHT / game_map.height))),
                                     to_3d(((x + 1) * (WIDTH / game_map.width), y * (HEIGHT / game_map.height))),
                                     to_3d(((x + 1) * (WIDTH / game_map.width), (y + 1) * (HEIGHT / game_map.height))),
                                     to_3d((x * (WIDTH / game_map.width), (y + 1) * (HEIGHT / game_map.height)))],
                                    width=w)

                if (x, y) == game_pos:
                    # Dead: draw cross
                    if not alive:
                        pygame.draw.polygon(screen,
                                            (255, 0, 0, 32),
                                            [to_3d(((x + 0.07) * (WIDTH / game_map.width),
                                                    (y + 0.02) * (HEIGHT / game_map.height))),
                                             to_3d(((x + 0.5) * (WIDTH / game_map.width),
                                                    (y + 0.45) * (HEIGHT / game_map.height))),
                                             to_3d(((x + 0.93) * (WIDTH / game_map.width),
                                                    (y + 0.02) * (HEIGHT / game_map.height))),
                                             to_3d(((x + 0.98) * (WIDTH / game_map.width),
                                                    (y + 0.07) * (HEIGHT / game_map.height))),
                                             to_3d(((x + 0.55) * (WIDTH / game_map.width),
                                                    (y + 0.5) * (HEIGHT / game_map.height))),
                                             to_3d(((x + 0.98) * (WIDTH / game_map.width),
                                                    (y + 0.93) * (HEIGHT / game_map.height))),
                                             to_3d(((x + 0.93) * (WIDTH / game_map.width),
                                                    (y + 0.98) * (HEIGHT / game_map.height))),
                                             to_3d(((x + 0.5) * (WIDTH / game_map.width),
                                                    (y + 0.55) * (HEIGHT / game_map.height))),
                                             to_3d(((x + 0.07) * (WIDTH / game_map.width),
                                                    (y + 0.98) * (HEIGHT / game_map.height))),
                                             to_3d(((x + 0.02) * (WIDTH / game_map.width),
                                                    (y + 0.93) * (HEIGHT / game_map.height))),
                                             to_3d(((x + 0.45) * (WIDTH / game_map.width),
                                                    (y + 0.5) * (HEIGHT / game_map.height))),
                                             to_3d(((x + 0.02) * (WIDTH / game_map.width),
                                                    (y + 0.07) * (HEIGHT / game_map.height))),
                                             to_3d(((x + 0.07) * (WIDTH / game_map.width),
                                                   (y + 0.02) * (HEIGHT / game_map.height)))])

                    pass

                elif game_map.map[x][y] is None:
                    pass

                # Draw barrier
                elif not game_map.contains_legion((x, y)):
                    b_idx = game_map.map[x][y][0]
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

                # Draw soldier
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
                time_img = font.render("Level " + to_roman(level_idx) + "      " + str(t_min) + ":" + str(t_ds) +
                                       str(t_s),
                                       True, (255, 255, 255))
                time_pos = (WIDTH - 200, 20)
                screen.blit(time_img, time_pos)

        pygame.display.flip()

    # Game
    # Init
    random.seed()
    path = os.getcwd() + "/"
    locale = "en"
    TIME_EVENT = pygame.USEREVENT + 1

    # Pygame init
    pygame.init()
    screen = pygame.display.set_mode((WIDTH + 2 * XFRAME, HEIGHT + 2 * YFRAME))
    pygame.display.set_caption("Legions")

    # Sound init
    pygame.mixer.init()
    play_music()
    MUSIC_END = pygame.USEREVENT + 2
    pygame.mixer.music.set_endevent(MUSIC_END)
    sword_sound = [pygame.mixer.Sound(path + "sword_fight0" + str(i) + ".wav") for i in range(1, 4)]
    moan_sound = pygame.mixer.Sound(path + "moan.wav")

    # Load images, fonts, ...
    bg_marble = load_image(path + "marble.jpg")     # Message box background
    font = pygame.font.Font(path + "Cinzel-Regular.ttf", 24)
    title_font = pygame.font.Font(path + "Cinzel-Regular.ttf", 36)
    sub_font = pygame.font.Font(path + "Cinzel-Regular.ttf", 12)
    soldier = load_image(path + "soldier.png")
    barrier = [load_image(path + "barrier0" + str(n) + ".png") for n in range(1, 5)]

    # Start screen
    game_on = True
    welcome_text = translate_text(WELCOME_TEXT, locale)
    if not welcome_text:
        welcome_text = translate_text(WELCOME_TEXT, "en")
    msg_box([("Legions", title_font), (welcome_text, font)], None, True, (500, 200, 900, 500))

    # Game loop
    while game_on:
        alive = True

        for level in LEVELS:
            size, time = level
            level_idx = LEVELS.index(level) + 1
            if not alive:
                break

            # Create new level
            pygame.time.set_timer(TIME_EVENT, 0)        # Disable timer
            msg_box("Create level " + to_roman(level_idx) + " ...", None, False, (600, 380, 700, 140))
            game_map = Map((size, size), 1, 2 ** size)
            game_pos = game_map.start
            game_count = game_map.force_level(game_pos)
            pygame.time.set_timer(TIME_EVENT, 1000)     # Re-enable timer

            # Load new Background
            img_idx = random.randint(1, 5)
            bgimage = load_image(path + "bg0" + str(img_idx) + ".jpg")
            background = pygame.Surface(screen.get_size(), pygame.SRCALPHA, 32)
            background = background.convert_alpha()
            background.blit(bgimage[0], (0, 0))
            draw()

            # Fighting
            fighting = True
            while fighting:
                # Handle events
                for event in pygame.event.get():

                    if event.type == MUSIC_END:
                        play_music()

                    if event.type == TIME_EVENT:
                        time -= 1
                        draw()

                        if time <= 0:
                            pygame.mixer.Sound.play(moan_sound)
                            msg_idx = random.randint(0, len(TIMEOUT_TEXT) - 1)
                            msg_txt = [translate_text(TIMEOUT_TEXT[msg_idx], "la")]
                            msg_loc = translate_text(TIMEOUT_TEXT[msg_idx], locale)
                            if msg_loc:
                                msg_txt.append(("(" + msg_loc + ")", sub_font))

                            msg_box(msg_txt, None, True, (500, 400, 900, 100))

                            alive = False
                            fighting = False

                    if event.type == pygame.QUIT:
                        quit(0)

                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        pos = pygame.mouse.get_pos()
                        pos = to_2d(pos)
                        b = enter(pos)

                        if not b:
                            alive = False
                            fighting = False
                            draw()
                            pygame.mixer.Sound.play(moan_sound)
                            msg_idx = random.randint(0, len(FAIL_TEXT) - 1)
                            msg_txt = [translate_text(FAIL_TEXT[msg_idx], "la")]
                            msg_loc = translate_text(FAIL_TEXT[msg_idx], locale)
                            if msg_loc:
                                msg_txt.append(("(" + msg_loc + ")", sub_font))

                            msg_box(msg_txt, None, True, (500, 400, 900, 100))

                        elif game_map.is_empty():
                            fighting = False
                            draw()
                            msg_idx = random.randint(0, len(VICTORY_TEXT) - 1)
                            msg_txt = [translate_text(VICTORY_TEXT[msg_idx], "la")]
                            msg_loc = translate_text(VICTORY_TEXT[msg_idx], locale)
                            if msg_loc:
                                msg_txt.append(("(" + msg_loc + ")", sub_font))

                            msg_box(msg_txt, None, True, (500, 400, 900, 100))

                        elif not game_map.has_neighbors(game_pos):
                            alive = False
                            fighting = False
                            draw()
                            pygame.mixer.Sound.play(moan_sound)
                            msg_idx = random.randint(0, len(ISOLATED_TEXT) - 1)
                            msg_txt = [translate_text(ISOLATED_TEXT[msg_idx], "la")]
                            msg_loc = translate_text(ISOLATED_TEXT[msg_idx], locale)
                            if msg_loc:
                                msg_txt.append(("(" + msg_loc + ")", sub_font))

                            msg_box(msg_txt, None, True, (500, 400, 900, 100))

                        else:
                            draw()

        if alive:
            msg_box("Game completed!", None, True, (500, 400, 900, 100))

        # New game?
        new_game_text = [translate_text(NEW_GAME_TEXT, "la")]
        new_game_loc = translate_text(NEW_GAME_TEXT, locale)
        if new_game_loc:
            new_game_text.append(("(" + new_game_loc + ")", sub_font))
        if msg_box(new_game_text, ["Etiam", "Finis"], True, (500, 300, 900, 300)) == 1:
            game_on = False

    pygame.quit()


if __name__ == "__main__":
    main()
