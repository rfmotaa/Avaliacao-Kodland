import pgzrun
from pygame import Rect
import random

WIDTH = 800
HEIGHT = 450

TILE_WIDTH = 64
camera_x = 0

sounds.background_theme.set_volume(0.3)
sounds.background_theme.play(-1)

game_won = False
win_timer_started = False  # <- Controle para evitar múltiplos agendamentos

class Platform:
    def __init__(self, x, y, w=18, h=18, url='stone'): 
        self.block_width = 18
        self.block_height = 18
        self.rect = Rect(x, y, w, h)
        self.url = url

    def draw(self):
        num_tiles = self.rect.width // self.block_width
        for i in range(num_tiles):
            tile = Actor(self.url)
            tile.left = self.rect.left + i * self.block_width - camera_x
            tile.bottom = self.rect.bottom
            tile.draw()

class Enemy:
    def __init__(self, x, y):
        self.rect = Rect(x, y, 40, 50)
        self.direction = 1
        self.sprite = 'zumbi_andar_direita1'

    def update(self):
        self.rect.x += self.direction * 2
        if self.rect.left < 0 or self.rect.right > 2000:
            self.direction *= -1
            self.sprite = 'zumbi_andar_direita1' if self.direction > 0 else 'zumbi_andar_esquerda1'

    def draw(self):
        sprite = Actor(self.sprite)
        sprite.midbottom = (self.rect.centerx - camera_x, self.rect.bottom)
        sprite.draw()

class Checkpoint:
    def __init__(self, x, y):
        self.rect = Rect(x, y, 32, 48)

    def draw(self):
        flag = Actor('trofeu_pequeno')
        flag.pos = self.rect.centerx - camera_x, self.rect.centery 
        flag.draw()

class Player:
    def __init__(self, x, y):
        self.hitbox_width = 32
        self.hitbox_height = 48
        self.sprite_width = 80
        self.sprite_height = 110
        self.rect = Rect(
            x + (self.sprite_width - self.hitbox_width) // 2,
            y + (self.sprite_height - self.hitbox_height),
            self.hitbox_width,
            self.hitbox_height
        )
        self.velocity_y = 0
        self.velocity_x = 0
        self.on_ground = False

        # Para animação
        self.anim_index = 0
        self.anim_timer = 0
        self.anim_speed = 0.2  # segundos por frame

        # Conjuntos de animação
        self.animations = {
            'parado': ['player_parado'],
            'andar_direita': ['player_andar_direita1', 'player_andar_direita2'],
            'andar_esquerda': ['player_andar_esquerda1', 'player_andar_esquerda2']
        }

        self.current_animation_key = 'parado'
        self.current_animation = self.animations[self.current_animation_key][0]

    def move_left(self):
        self.velocity_x = -3
        self.current_animation_key = 'andar_esquerda'

    def move_right(self):
        self.velocity_x = 3
        self.current_animation_key = 'andar_direita'

    def stop(self):
        self.velocity_x = 0
        if self.on_ground:
            self.current_animation_key = 'parado'
            self.anim_index = 0

    def jump(self):
        if self.on_ground:
            self.velocity_y = -10
            self.on_ground = False
            self.current_animation_key = 'parado'
            sounds.jump.play()

    def update(self, platforms):
        self.rect.x += self.velocity_x
        self._collide(platforms, 'x')
        self.velocity_y += 0.5
        self.rect.y += self.velocity_y
        self.on_ground = False
        self._collide(platforms, 'y')

        # Atualiza animação
        self.anim_timer += 1 / 60  # assumindo 60 FPS
        frames = self.animations[self.current_animation_key]

        if len(frames) > 1:
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.anim_index = (self.anim_index + 1) % len(frames)
            self.current_animation = frames[self.anim_index]
        else:
            self.current_animation = frames[0]
            self.anim_index = 0
            self.anim_timer = 0

    def _collide(self, platforms, axis):
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if axis == 'x':
                    if self.velocity_x > 0:
                        self.rect.right = p.rect.left
                    elif self.velocity_x < 0:
                        self.rect.left = p.rect.right
                    self.velocity_x = 0
                elif axis == 'y':
                    if self.velocity_y > 0:
                        self.rect.bottom = p.rect.top
                        self.on_ground = True
                        self.velocity_y = 0
                        self.current_animation_key = 'parado'
                    elif self.velocity_y < 0:
                        self.rect.top = p.rect.bottom
                        self.velocity_y = 0

    def draw(self):
        sprite = Actor(self.current_animation)
        sprite.topleft = (
            self.rect.left - (self.sprite_width - self.hitbox_width) // 2 - camera_x,
            self.rect.bottom - self.sprite_height
        )
        sprite.draw()

def reset_game():
    global player, enemy, game_won, win_timer_started
    player.rect.x, player.rect.y = 100, 300
    player.velocity_y = 0
    enemy.rect.x = 600
    game_won = False
    win_timer_started = False

platforms = [
    Platform(100, 400, 72, 18),
    Platform(250, 350, 72, 18),
    Platform(350, 325, 72, 18),
    Platform(500, 300, 72, 18),
    Platform(650, 325, 72, 18),
    Platform(800, 275, 72, 18),
    Platform(900, 225, 72, 18),
    Platform(1050, 275, 72, 18),
    Platform(1200, 300, 72, 18),
    Platform(1300, 325, 72, 18),
    Platform(1450, 275, 72, 18),
    Platform(1600, 225, 72, 18),
    Platform(1750, 200, 72, 18),
    Platform(1900, 150, 72, 18),
    Platform(0, 0, 18, 600), #parede esquerda
    Platform(2100, 0, 18, 600), #parede direita
    Platform(0, 445, 2600, 18, 'sand') #chão
]

checkpoint = Checkpoint(1925, 90)
enemy = Enemy(600, 400)
player = Player(100, 300)

def update():
    global camera_x, game_won, win_timer_started

    if not game_won:
        player.update(platforms)
        enemy.update()

        if player.rect.colliderect(enemy.rect):
            reset_game()

        if player.rect.colliderect(checkpoint.rect):
            game_won = True
            if not win_timer_started:
                clock.schedule(reset_game, 5.0)
                win_timer_started = True

    camera_x = max(0, player.rect.centerx - WIDTH // 2)

def draw():
    screen.fill((135, 206, 235))

    for p in platforms:
        p.draw()

    checkpoint.draw()
    enemy.draw()
    player.draw()

    if game_won:
        screen.draw.text(
            "Você venceu!",
            center=(WIDTH // 2, HEIGHT // 2 - 100),
            fontsize=60,
            color="white",
            owidth=2,
            ocolor="black"
        )

def on_key_down(key):
    if key == keys.A:
        player.move_left()
    elif key == keys.D:
        player.move_right()
    elif key == keys.W:
        player.jump()
    elif key == keys.R:
        reset_game()

def on_key_up(key):
    if key in (keys.A, keys.D):
        player.stop()

pgzrun.go()
