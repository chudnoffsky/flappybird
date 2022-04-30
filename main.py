import pygame
import random
import os

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 850
screen_height = 815

middle_width = int(screen_width / 2)
middle_height = int(screen_height / 2)

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Flappy Bird")
image_icon = pygame.image.load("images/icon.png")
pygame.display.set_icon(image_icon)

# шрифт
font = pygame.font.Font("fonts/Flappy-Bird.ttf", 130)
white = (255, 255, 255)
flying = False
game_over = False
ground_scroll = 0
scroll_speed = 4

# трубы
pipes_gap = 150
pipes_frequency = 1500
last_pipes = pygame.time.get_ticks() - pipes_frequency


pass_pipes = False

# изображения в игре
background = pygame.image.load("images/background.png")
ground_image = pygame.image.load("images/ground.png")
button_image = pygame.image.load("images/restart.png")


def stop_game():
    global game_over, flying, score, bird_main
    game_over = True
    if bird_main.rect.bottom >= 750:
        flying = False
    if game_over:
        if button.draw():
            # игра заново
            game_over = False
            flying = False
            pipes.empty()
            bird_main.rect.x = 100
            bird_main.rect.y = middle_height
            score = 0


# главный класс для персонажа (птицы)
class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.counter = 0
        self.images = []
        self.index = 0

        # анимация птицы (полет, движение и падение)
        for n in range(1, 4):
            self.images.append(pygame.image.load(f"images/bird{n}.png"))
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.clicked = False
        self.vel = 0

    def update(self):
        if flying is True:
            # гравитация птицы
            self.vel += 0.7
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)
            if self.vel > 8:
                self.vel = 8

        if not game_over:
            # прыжок птицы
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False
            elif pygame.mouse.get_pressed()[0] == 1 and not(self.clicked):
                self.clicked = True
                self.vel = -10

            # анимация крыльев птицы
            flap_cooldown = 5
            self.counter += 1

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
                self.image = self.images[self.index]

            # анимация вращения птицы
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)

        # анимация при падении птицы
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)


# главный класс для труб
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load("images/pipe.png")
        self.rect = self.image.get_rect()

        # определяет, труба находится снизу (-1) или сверху (1)
        if position == -1:
            self.rect.topleft = [x, y + int(pipes_gap / 2)]
        elif position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipes_gap / 2)]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()


# главный класс для кнопки
class Button:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()

        # проверка на нажатие мыши
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        screen.blit(self.image, (self.rect.x, self.rect.y))
        return action


score = 0

pipes = pygame.sprite.Group()
bird_delay = pygame.sprite.Group()

bird_main = Bird(100, middle_height)
bird_delay.add(bird_main)

# кнопка restart
button = Button(middle_width - 50, middle_height - 100, button_image)

run = True
while run:
    clock.tick(fps)
    screen.blit(background, (0, 0))

    pipes.draw(screen)
    bird_delay.draw(screen)
    bird_delay.update()

    # дальнейшее отображение фона земли
    screen.blit(ground_image, (ground_scroll, 750))

    # проверка результата
    if len(pipes) > 0:
        if pass_pipes is True:
            if pipes.sprites()[0].rect.right < bird_delay.sprites()[0].rect.left:
                score = score + 1
                pass_pipes = False

        if not(pass_pipes) and bird_delay.sprites()[0].rect.left > pipes.sprites()[0].rect.left \
                and bird_delay.sprites()[0].rect.right < pipes.sprites()[0].rect.right:
            pass_pipes = True

    # обновление счетчика
    image = font.render(str(score), True, white)
    screen.blit(image, (middle_width, 20))

    # столкновение птицы с трубами
    if not(game_over):
        if bird_main.rect.top < 0 or pygame.sprite.groupcollide(bird_delay, pipes, False, False):
            stop_game()
        # если птица падает на землю, то игра закончена (game_over)
        elif bird_main.rect.bottom >= 750:
            stop_game()
        elif flying:
            # генерирует новые трубы
            time_now = pygame.time.get_ticks()
            if time_now - last_pipes > pipes_frequency:
                pipes_height = random.randint(-100, 100)

                pipes.add(Pipe(screen_width, middle_height + pipes_height, 1))
                pipes.add(Pipe(screen_width, middle_height + pipes_height, -1))
                last_pipes = time_now

            pipes.update()

            ground_scroll = ground_scroll - scroll_speed
            if abs(ground_scroll) > 35:
                ground_scroll = 0
    else:
        stop_game()

    for event in pygame.event.get():
        if not(game_over) and not(flying) and event.type == pygame.MOUSEBUTTONDOWN:
            flying = True
        if event.type == pygame.QUIT:
            run = False
    pygame.display.update()

pygame.quit()
