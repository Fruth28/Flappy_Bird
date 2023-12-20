import pygame
import random

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 864
screen_height = 936

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')

# шрифт
font = pygame.font.SysFont('Bauhaus 93', 60)

# цвет
white = (255, 255, 255)

# переменные
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 150
pipe_frequency = 1500  # миллисекунд
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
last_score = 0
max_score = 0
pass_pipe = False
pipe_count = 0


# загрузка изображений
bg = pygame.image.load('img/bg.png')
ground_img = pygame.image.load('img/ground.png')
button_img = pygame.image.load('img/restart.png')


def draw_text(text, font, text_col, x, y):
    """Выводит текст на экран"""
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def reset_game():
    """Выводит score, сбрасывает pipe_group, возвращает птицу в исходное положение

    :returns: score
    :rtype: int"""
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    score = 0
    return score


class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        """Добавляет в список три изображения птицы. Затем создаёт прямоугольник птицы с центром в координатах (x, y)

        :param x: coordinate
        :type x: int
        :param y: coordinate
        :type y: int"""
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f'img/bird{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def update(self):
        """Если мы не нажимаем на лкм, то птица падает со скоростью vel, но если мы щёлкнем на лкм, то птица поднимется/
        на 10 пикселей. Каждые 5 кадров положение крыльев меняется. Если мы летим в верх, то птица наклонена вверх/
        аналогично вниз. Но если мы коснёмся земли, то птица будет повёрнута вниз под углом 90 градусов"""
        if flying:
            # гравитация
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)

        if game_over is False:
            # прыжок
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked is False:
                self.clicked = True
                self.vel = -10
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

            # управление анимацией
            self.counter += 1
            flap_cooldown = 5

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]

            # наклон птицы
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        """Если position == 1, то создаёт верхнюю трубу, если position == -1, то создаёт нижнюю трубу

        :param x: coordinate
        :type x: int
        :param y: coordinate
        :type y: int
        :param position: top or bottom position
        :type position: int"""
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/pipe.png')
        self.rect = self.image.get_rect()
        # position 1 для верхней трубы, -1 для нижней
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        if position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]

    def update(self):
        """Перемещает трубы влево со скоростью 4 пик/сек и если правый край трубы зашел за край окна, то труба
        уничтожается"""
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()


class Button():
    def __init__(self, x, y, image):
        """Создает прямоугольник, верхний левый угол которого имеет координаты (x, y)

        :param x: coordinate
        :type x: int
        :param y: coordinate
        :type y: int
        :param image: image
        :type image: png"""
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        """Return action == True, если нажать лкм на кнопку restart, иначе return action == False

        :param x: coordinate
        :type x: int
        :param y: coordinate
        :type y: int
        :returns: action
        :rtype: bool"""
        action = False

        # координаты курсора
        pos = pygame.mouse.get_pos()

        # проверка, находится ли курсор над кнопкой restart
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        # нарисовать кнопку
        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action


bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

flappy = Bird(100, int(screen_height / 2))

bird_group.add(flappy)

# создать кнопку restart
button = Button(screen_width // 2 - 50, screen_height // 2 - 100, button_img)

startFont = pygame.font.Font('freesansbold.ttf', 32)


def start():
    """Выводит на начальный экран инструкцию по управлению, последний и максимальный счёт"""
    display = startFont.render(f"ДЛЯ СТАРТА НАЖМИТЕ НА ПРОБЕЛ", True, (255, 255, 255))
    display_use = startFont.render(f"ДЛЯ УПРАВЛЕНИЯ ИСПОЛЬЗУЙТЕ ЛКМ", True, (255, 255, 255))
    display_max_score = startFont.render(f"Score: {last_score}      Max score: {max_score}", True, (255, 255, 255))
    screen.blit(display, (130, 200))
    screen.blit(display_use, (100, 300))
    screen.blit(display_max_score, (250, 400))
    pygame.display.update()


def check_pipe_count():
    global pipe_count, scroll_speed
    if pipe_count > 0 and pipe_count % 5 == 0:
        scroll_speed += 0.1


waiting = True

run = True
while run:

    clock.tick(fps)

    # нарисовать фон
    screen.blit(bg, (0, 0))

    bird_group.draw(screen)
    bird_group.update()
    pipe_group.draw(screen)

    # нарисовать землю
    screen.blit(ground_img, (ground_scroll, 768))

    while waiting:
        start()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    #  если мы нажмём пробел, то начнём игру
                    reset_game()
                    waiting = False

        if event.type == pygame.QUIT:
            waiting = False

    # проверка, прошла ли птица трубу
    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
            and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
                and pass_pipe is False:
            pass_pipe = True
        if pass_pipe:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pipe_count += 1
                pass_pipe = False

    check_pipe_count()

    draw_text(str(score), font, white, int(screen_width / 2), 20)

    # проверка, столкнулась ли птица с трубой или с небом
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        game_over = True

    # проверка, столкнулась ли птица с землёй
    if flappy.rect.bottom >= 768:
        game_over = True
        flying = False

    if game_over is False and flying is True:

        # создание новых труб
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            pipe_height = random.randint(-100, 100)
            btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
            top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now

        # прокрутка земли
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll = 0

        pipe_group.update()

    # проверка, завершилась ли игра, если да, то при нажатии restart, игра перезапустится
    if game_over is True:
        if button.draw() is True:
            waiting = True
            game_over = False
            max_score = max(max_score, score)
            last_score = score
            score = reset_game()
            pipe_count = 0
            scroll_speed = 4

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and flying is False and game_over is False:
            flying = True

    pygame.display.update()

pygame.quit()
