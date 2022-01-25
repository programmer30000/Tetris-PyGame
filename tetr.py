import random, datetime
import pygame, os, sys

all_sprites = pygame.sprite.Group()
borders = None
fig_downed = False
score = 0


def cor_image(image):
    for i in range(25, image.get_size()[1], 50):
        for j in range(25, image.get_size()[0], 50):
            if image.get_at((j, i)) == (254, 254, 254):
                # квадрат пустой, заполняем его 0
                for k in range(i - 25, i + 25):
                    for l in range(j - 25, j + 25):
                        if k < image.get_size()[1] and l < image.get_size()[0]:
                            image.set_at((l, k), (254, 254, 254))
    return image


def load_rand_fig(name):
    # эта функция из одного файла со всеми фигурками сразу вырезает случайную фигурку
    # список fig_rects содержит координаты ограничивающих фигурки прямоугольников в данном файле
    fig_rects = [
        # Z- фигурки
        (0, 0, 150, 100), (0, 105, 150, 100), (0, 212, 150, 100), (0, 314, 150, 100),
        (0, 420, 150, 100), (0, 525, 150, 100), (0, 630, 150, 100),
        # Г - фигурки
        (162, 0, 150, 100), (162, 105, 150, 100), (162, 212, 150, 100), (162, 314, 150, 100),
        (162, 420, 150, 100), (162, 525, 150, 100), (162, 630, 150, 100),
        # прямые палочки из 4-х квадратиков
        (324, 0, 200, 50), (324, 58, 200, 50), (324, 115, 200, 50), (324, 173, 200, 50), (324, 230, 200, 50),
        (324, 288, 200, 50),
        (324, 345, 200, 50),
        # квадратики из 4-х
        (324, 403, 100, 100),
        (324, 518, 100, 100), (324, 632, 100, 100), (324, 747, 100, 100), (324, 403, 100, 100),
        (439, 518, 100, 100), (439, 632, 100, 100), (439, 747, 100, 100),
        # Т-фигурки
        (551, 3, 150, 100), (551, 107, 150, 100), (551, 213, 150, 100), (551, 317, 150, 100),
        (551, 421, 150, 100), (551, 527, 150, 100), (551, 633, 150, 100)
    ]

    fullname = name  # os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    image = image.convert()
    # выбираем случайную фигурку
    rect = fig_rects[random.randint(0, len(fig_rects) - 1)]

    fig_image = image.subsurface(pygame.Rect((rect[0], rect[1]), (rect[2] - 1, rect[3] - 1)))
    fig_image.set_colorkey((254, 254, 254))
    # ровняем изображение если оно криво нарисованно (не квадратами 50 на 50)
    image = cor_image(fig_image)
    return fig_image


def load_image(name, colorkey=None):
    fullname = name  # os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Figure:
    def __init__(self, b, c, f):
        self.board = b
        self.fig_x = 7
        self.fig_y = 0

        self.color = c
        self.fig_type = f
        self.fig = [[0, 0, 0, 0] * 4]
        if f == 1:
            self.fig = [[0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0]]
        elif f == 2:
            self.fig = [[0, 1, 0, 0], [1, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        elif f == 3:
            self.fig = [[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        elif f == 4:
            self.fig = [[1, 1, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0], [0, 0, 0, 0]]
        elif f == 5:
            self.fig = [[1, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0]]

    def is_cross(self):
        # проверяем на пересечение с уже существубщими фигурами в стакане
        for y in range(4):
            for x in range(4):
                xb = self.fig_x + x
                yb = self.fig_y + y
                if self.board.inrange(xb, yb):
                    if self.fig[x][y] != 0 and self.board.board[yb][xb] != (0, 0, 0):
                        return True
        return False

    def draw_fig(self, cl=False):
        for y in range(4):
            for x in range(4):
                xb = self.fig_x + x
                yb = self.fig_y + y
                if self.board.inrange(xb, yb):
                    if self.fig[x][y] != 0:
                        if cl:
                            self.board.board[yb][xb] = (0, 0, 0)
                        else:
                            self.board.board[yb][xb] = self.color

    def move(self, xc, yc):
        # удаляем фигуру с доски
        self.draw_fig(True)
        self.fig_y += yc
        self.fig_x += xc

        if self.is_cross() or not self.inbound():
            self.fig_y -= yc
            self.fig_x -= xc
            self.draw_fig()
            return False

        self.draw_fig()
        return True

    def move_down(self):
        return self.move(0, 1)

    def move_left(self):
        return self.move(-1, 0)

    def move_right(self):
        return self.move(1, 0)

    def rotate(self):
        self.draw_fig(True)
        fig_t = []
        for i in self.fig:
            fig_t.append(i.copy())
        for y in range(4):
            for x in range(4):
                self.fig[x][y] = fig_t[y][3 - x]
        if self.is_cross() or not self.inbound():
            self.fig = fig_t.copy()

        self.draw_fig()

    def inbound(self):
        for y in range(4):
            for x in range(4):
                xb = self.fig_x + x
                yb = self.fig_y + y
                if self.fig[x][y] != 0 and not self.board.inrange(xb, yb):
                    return False
        return True


class Border(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)
        self.image = pygame.surface.Surface(pygame.display.get_window_size())
        pygame.draw.rect(self.image, (0, 0, 125), (8, 8, 502, 20 + 902), 2)
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0
        self.image.set_colorkey((0, 0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class Fig(pygame.sprite.Sprite):

    def __init__(self, *group):
        super().__init__(*group)
        # выбираем случайную фигурку

        self.image = load_rand_fig('figs.png')
        self.rect = self.image.get_rect()
        self.rect.x = 160
        self.rect.y = 28
        self.mask = pygame.mask.from_surface(self.image)
        self.cor_mask()

    def cor_mask(self):
        # проверка и корректировака маски
        # нужна только из за плохих спрайтов которые имеют мусор на изображении
        for i in range(25, self.mask.get_size()[1], 50):
            for j in range(25, self.mask.get_size()[0], 50):
                if self.mask.get_at((j, i)) == 0:
                    # квадрат пустой, заполняем его 0
                    for k in range(i - 25, i + 25):
                        for l in range(j - 25, j + 25):
                            if k < self.mask.get_size()[1] and l < self.mask.get_size()[0]:
                                self.mask.set_at((l, k), 0)

    def update(self, *args):
        global fig_downed
        move_step = 50
        if args:
            if args[0] == 1:
                # 1 - значит просто падение вниз
                self.rect = self.rect.move(0, move_step)
                if pygame.sprite.collide_mask(self, borders):
                    self.rect = self.rect.move(0, -move_step)
                    # произошло столкновение с объектом в стакане при попытке движения вниз
                    # добавляем его к стакану
                    borders.image.blit(self.image, (self.rect.x, self.rect.y))
                    borders.mask = pygame.mask.from_surface(borders.image)
                    all_sprites.remove(self)
                    # выставляем глобальный флаг, что фигурка упала
                    fig_downed = True
            elif args[0] == pygame.K_UP:
                # вращение фигуры
                rotated_image = pygame.transform.rotate(self.image, 90)
                self.image = rotated_image
                self.image = cor_image(self.image)
                self.mask = pygame.mask.from_surface(self.image)
                if pygame.sprite.collide_mask(self, borders):
                    rotated_image = pygame.transform.rotate(self.image, -90)
                    self.image = rotated_image
                    self.image = cor_image(self.image)
                    self.mask = pygame.mask.from_surface(self.image)
                self.cor_mask()
            elif args[0] == pygame.K_LEFT:
                # нажали стрелку влево
                self.rect = self.rect.move(-move_step, 0)
                # надо проверить не вышел ли объект за пределы экрана
                if pygame.sprite.collide_mask(self, borders):
                    # если вышел возвращаем его обратно перемещать нельзя
                    self.rect = self.rect.move(move_step, 0)
            elif args[0] == pygame.K_RIGHT:
                # нажали стрелку вправо
                self.rect = self.rect.move(move_step, 0)
                # надо проверить не вышел ли объект за пределы экрана
                if pygame.sprite.collide_mask(self, borders):
                    # если вышел возвращаем его обратно перемещать нельзя
                    self.rect = self.rect.move(-move_step, 0)
            self.mask = pygame.mask.from_surface(self.image)
            self.cor_mask()


class Board:
    # создание поля
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[(0, 0, 0)] * width for _ in range(height)]
        # значения по умолчанию

        self.left = 40
        self.top = 40
        self.cell_size = 30

    def inrange(self, x, y):
        if x >= 0 and x < self.width and y >= 0 and y < self.height:
            return True
        return False

    # настройка внешнего вида
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, a):
        for y in range(self.height):
            for x in range(self.width):
                pygame.draw.rect(a, pygame.Color(125, 125, 125),
                                 ((x * self.cell_size) + self.left, y * self.cell_size + self.top,
                                  self.cell_size, self.cell_size), 1)
                if self.board[y][x] != (0, 0, 0):
                    pygame.draw.rect(a, self.board[y][x],
                                     ((x * self.cell_size) + self.left + 2, y * self.cell_size + self.top + 2,
                                      self.cell_size - 4, self.cell_size - 4))

    def check_line(self):
        y = self.height - 1
        while y >= 0:
            flag = True
            for x in range(self.width):
                if self.board[y][x] == (0, 0, 0):
                    flag = False
            if flag:
                # стираем линию
                self.board.pop(y)
                self.board.insert(0, [[(0, 0, 0)] * self.width])
            else:
                y -= 1


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    # выводим заставку
    fon = pygame.transform.scale(load_image('boxart.jpg'), pygame.display.get_window_size())
    screen.blit(fon, (0, 0))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
            pygame.display.flip()


def settings():
    pass


def main_game_board(hard_level=5):
    board = Board(15, 30)

    board.left = 75
    board.top = 25

    running = True
    fig_moving = False
    fig_colors = [(0, 0, 0), (125, 0, 0), (0, 125, 0), (125, 125, 0), (0, 0, 125), (125, 0, 125)]

    clock = pygame.time.Clock()
    fig = None

    chrez_raz = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    if fig_moving:
                        fig.move_right()
                if event.key == pygame.K_LEFT:
                    if fig_moving:
                        fig.move_left()
                if event.key == pygame.K_UP:
                    if fig_moving:
                        fig.rotate()
                if event.key == pygame.K_ESCAPE:
                    return

        if fig_moving:
            if chrez_raz:
                if not fig.move_down() or not fig.inbound():
                    # board.check_line()
                    fig_moving = False
            chrez_raz = not chrez_raz
        else:
            fig = Figure(board, fig_colors[random.randint(1, 5)], random.randint(1, 4))
            fig_moving = True
        clock.tick(hard_level)
        screen.fill((0, 0, 0))
        board.render(screen)
        pygame.display.flip()


def check_fill_line():
    # идем построчно по стакану c шагом 50, чтобы попадать в центр квадратиков
    # у алгоритма ест дефект - если в текстуры фигур нарисовать в центр черным цветом, то строки не будут удаляться
    # но там нет черного, поэтому не страшно

    global score
    line_n = 0
    for i in range(28, 922, 50):
        flag = True
        line_state = []
        for j in range(10, 502, 50):
            if borders.image.get_at((j + 25, i + 25)) == (0, 0, 0):
                flag = False
                line_state.append(0)
            else:
                line_state.append(1)
        # print(line_state)

        if flag:
            # надо удалять строку

            subf = borders.image.subsurface(pygame.Rect(10, 28, 502, i - 28))
            newsurf = pygame.surface.Surface(subf.get_size())
            newsurf.blit(subf, (0, 0))
            borders.image.blit(newsurf, (10, 28 + 50))
            score += 100
            # print("line fill - " + str(i+25))
    borders.mask = pygame.mask.from_surface(borders.image)


def print_score():
    font = pygame.font.Font(None, 50)
    string_rendered = font.render("Счет", 1, pygame.Color('green'))
    text_rect = string_rendered.get_rect()
    text_rect.top = 150
    text_rect.x = 550
    screen.blit(string_rendered, text_rect)

    string_rendered = font.render(str(score), 1, pygame.Color('green'))
    text_rect = string_rendered.get_rect()
    text_rect.top = 250
    text_rect.x = 550
    screen.blit(string_rendered, text_rect)


def print_game_over():
    font = pygame.font.Font(None, 100)
    string_rendered = font.render("Game over!", 1, pygame.Color('red'))
    text_rect = string_rendered.get_rect()
    text_rect.top = 350
    text_rect.x = 150
    screen.blit(string_rendered, text_rect)


def record_screen():
    intro_text = ["Рекорды", ""]
    menu_rects = []

    screen.fill((0, 128, 128), screen.get_rect())

    f_rec = open("records.txt", "rt")

    for s in f_rec.readlines():
        s = s.rstrip()
        intro_text.append(' - '.join(s.split(';')))

    # сдесть считываем из файла рекорды
    font = pygame.font.Font(None, 50)
    text_coord = 250
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        text_rect = string_rendered.get_rect()
        if text_coord > 300:
            text_coord += 30
        else:
            text_coord += 50

        text_rect.top = text_coord
        if text_coord > 300:
            text_rect.x = 100
        else:
            text_rect.x = 200

        text_coord += text_rect.height
        menu_rects.append([text_rect, line])
        screen.blit(string_rendered, text_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
            pygame.display.flip()


def main_game(hard_level):
    running = True
    fig_moving = False
    global fig_downed
    global borders
    global score

    all_sprites.empty()
    if borders:
        del borders
    borders = Border()

    clock = pygame.time.Clock()
    fig = None

    sprite = Fig()
    all_sprites.add(sprite)

    chrez_raz = True
    tik_set = hard_level
    game_over_flag = False

    score = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE or event.key == pygame.K_DOWN:
                    # делем быстрое опускание
                    tik_set = hard_level
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_DOWN:
                    # делем быстрое опускание
                    tik_set = hard_level * 10
                if not game_over_flag:
                    all_sprites.update(event.key)
                if event.key == pygame.K_ESCAPE:
                    return

        if fig_moving and not game_over_flag:
            if chrez_raz:
                all_sprites.update(1)  # 1 - Это падение вниз
                # тут надо проверять не упали ли мы на дно стакана
                if fig_downed:
                    # надо проверить нет ли полностью заполненных линий в стакане и их убрать
                    check_fill_line()

                    # надо создавать новый спрайт
                    new_fig = Fig()
                    # проверяем не столкнулся ли новый спрайт со стаканом (игра окончена)
                    if pygame.sprite.collide_mask(new_fig, borders):
                        # игра окончена
                        game_over_flag = True
                        print_game_over()

                        # рисуем окошечко для ввода имени
                        font = pygame.font.Font(None, 30)
                        pygame.draw.rect(screen, (0, 0, 0), (150, 250, 300, 120))
                        pygame.draw.rect(screen, (255, 255, 255), (150, 250, 300, 120), 2)
                        pygame.draw.rect(screen, (255, 255, 255), (210, 300, 200, 50), 1)
                        string_rendered = font.render("Введите ваше имя:", 1, pygame.Color('red'))
                        text_rect = string_rendered.get_rect()
                        text_rect.top = 255
                        text_rect.x = 210
                        screen.blit(string_rendered, text_rect)
                        pygame.display.flip()
                        fl_r = True
                        str_name = ""
                        while fl_r:
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    terminate()
                                if event.type == pygame.KEYDOWN:
                                    if event.key == pygame.K_ESCAPE:
                                        fl_r = False
                                    elif event.key == pygame.K_RETURN:  # клавиша Enter
                                        # записываем в таблицу рекордов
                                        f_rec = open('records.txt', 'rt')

                                        # считываем записи
                                        recs = []
                                        if f_rec:
                                            for s in f_rec.readlines():
                                                s = s.rstrip()
                                                recs.append(s.split(';'))
                                            recs.append([str_name, str(score), str(datetime.datetime.now())[:19]])
                                            f_rec.close()
                                        # сортируем
                                        recs.sort(key=lambda x: x[1], reverse=True)

                                        # записываем
                                        f_rec = open('records.txt', 'wt')
                                        for s in recs:
                                            f_rec.write(';'.join(s) + '\n')
                                        f_rec.close()
                                        fl_r = False
                                    elif event.key == pygame.K_BACKSPACE:
                                        if len(str_name) > 0:
                                            str_name = str_name[:-1]
                                    else:
                                        if event.unicode.isalpha() or event.unicode.isdigit() or event.unicode == ' ':
                                            str_name += event.unicode

                                pygame.draw.rect(screen, (0, 0, 0), (210, 300, 200, 50))
                                pygame.draw.rect(screen, (255, 255, 255), (210, 300, 200, 50), 1)

                                font = pygame.font.Font(None, 50)
                                string_rendered = font.render(str_name, 1, pygame.Color('white'))
                                text_rect = string_rendered.get_rect()
                                screen.blit(string_rendered, (212, 302))
                                pygame.display.flip()

                    else:
                        all_sprites.add(new_fig)
                    fig_downed = False
            chrez_raz = not chrez_raz
        elif not game_over_flag:
            # тут создаем новый спрайт
            fig_moving = True
        clock.tick(tik_set)
        screen.fill((0, 0, 0))
        all_sprites.draw(screen)
        print_score()
        if game_over_flag:
            print_game_over()
        pygame.display.flip()


def hard_level_menu():
    intro_text = ["Легкий",
                  "Сложный",
                  "На основе клеточного поля"]
    menu_rects = []

    screen.fill((0, 128, 128), screen.get_rect())

    font = pygame.font.Font(None, 50)
    text_coord = 250
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('red'))
        text_rect = string_rendered.get_rect()
        text_coord += 50
        text_rect.top = text_coord
        text_rect.x = 200
        text_coord += text_rect.height
        menu_rects.append([text_rect, line])
        screen.blit(string_rendered, text_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for r in menu_rects:
                    if r[0].collidepoint(event.pos):
                        if r[1] == intro_text[0]:
                            main_game(5)
                        elif r[1] == intro_text[1]:
                            main_game(10)
                        elif r[1] == intro_text[2]:
                            main_game_board(10)
                        screen.fill((0, 128, 128), screen.get_rect())
                        return

            if event.type == pygame.MOUSEMOTION:
                for r in menu_rects:
                    if r[0].collidepoint(event.pos):
                        string_rendered = font.render(r[1], 1, pygame.Color('blue'))
                        screen.blit(string_rendered, r[0])
                    else:
                        string_rendered = font.render(r[1], 1, pygame.Color('red'))
                        screen.blit(string_rendered, r[0])
        pygame.display.flip()


def menu_screen():
    intro_text = ["", "",
                  "Начать игру",
                  "Рекорды",
                  "Выйти"]
    menu_rects = []

    screen.fill((0, 128, 128), screen.get_rect())

    fon = pygame.transform.scale(load_image('boxart.jpg'), pygame.display.get_window_size())
    screen.blit(fon, (0, 0))

    font = pygame.font.Font(None, 50)
    text_coord = 250
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('red'))
        text_rect = string_rendered.get_rect()
        text_coord += 50
        text_rect.top = text_coord
        text_rect.x = 200
        text_coord += text_rect.height
        menu_rects.append([text_rect, line])
        screen.blit(string_rendered, text_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for r in menu_rects:
                    if r[0].collidepoint(event.pos):
                        if r[1] == intro_text[4]:
                            terminate()
                        elif r[1] == intro_text[2]:
                            hard_level_menu()
                        elif r[1] == intro_text[3]:
                            record_screen()
                        # прерываем цикл и перезапускаем
                        intro_text = ["", "",
                                      "Начать игру",
                                      "Рекорды",
                                      "Выйти"]
                        menu_rects = []

                        screen.fill((0, 128, 128), screen.get_rect())

                        fon = pygame.transform.scale(load_image('boxart.jpg'), pygame.display.get_window_size())
                        screen.blit(fon, (0, 0))

                        font = pygame.font.Font(None, 50)
                        text_coord = 250
                        for line in intro_text:
                            string_rendered = font.render(line, 1, pygame.Color('red'))
                            text_rect = string_rendered.get_rect()
                            text_coord += 50
                            text_rect.top = text_coord
                            text_rect.x = 200
                            text_coord += text_rect.height
                            menu_rects.append([text_rect, line])
                            screen.blit(string_rendered, text_rect)

            if event.type == pygame.MOUSEMOTION:
                for r in menu_rects:
                    if r[0].collidepoint(event.pos):
                        string_rendered = font.render(r[1], 1, pygame.Color('blue'))
                        screen.blit(string_rendered, r[0])
                    else:
                        string_rendered = font.render(r[1], 1, pygame.Color('red'))
                        screen.blit(string_rendered, r[0])
        pygame.display.flip()


# Показываем заставку

pygame.init()
size = 30 * 15 + 250, 30 * 30 + 50
screen = pygame.display.set_mode(size)
start_screen()
menu_screen()
