import pygame
import random
from pygame import sprite
from pygame import rect
from pygame import image
import os

from pygame import surface

# 變數用大寫代表不會更改
FPS = 60
WIDTH = 500
HEIGHT = 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255,0,0)
YELLOW = (255,255,0)

# 遊戲初始化 and 創建視窗
pygame.init()                                               # 把 pygame 裡面的遊戲都做初始化
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))           # 創建視窗(寬度, 高度)
pygame.display.set_caption("星際大戰爭")                     # 設定遊戲名稱
clock = pygame.time.Clock()                                 # 創建一個物件對時間做管理

# 載入圖片(載入前要把 pygame 初始化)
background_img = pygame.image.load(os.path.join("img", "background.png")).convert()
player_img = pygame.image.load(os.path.join("img", "player.png")).convert()
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(BLACK)
pygame.display.set_icon(player_mini_img)
bullet_img = pygame.image.load(os.path.join("img", "bullet.png")).convert()
rock_imgs = []
for i in range(7):
    rock_imgs.append(pygame.image.load(os.path.join("img", f"rock{i}.png")).convert())
expl_anim = {}
expl_anim["lg"] = []
expl_anim["sm"] = []
expl_anim["player"] = []
for i in range(9):
    expl_img = pygame.image.load(os.path.join("img", f"expl{i}.png")).convert()
    expl_img.set_colorkey(BLACK)
    expl_anim["lg"].append(pygame.transform.scale(expl_img, (75,75)))
    expl_anim["sm"].append(pygame.transform.scale(expl_img, (30,30)))
    player_expl_img = pygame.image.load(os.path.join("img", f"player_expl{i}.png")).convert()
    player_expl_img.set_colorkey(BLACK)
    expl_anim["player"].append(player_expl_img)
power_imgs = {}
power_imgs["shield"] = pygame.image.load(os.path.join("img", "shield.png")).convert()
power_imgs["gun"] = pygame.image.load(os.path.join("img", "gun.png")).convert()

# 載入音樂
shoot_sound = pygame.mixer.Sound(os.path.join("sound", "shoot.wav"))
shield_sound = pygame.mixer.Sound(os.path.join("sound", "pow0.wav"))
gun_sound = pygame.mixer.Sound(os.path.join("sound", "pow1.wav"))
die_sound = pygame.mixer.Sound(os.path.join("sound", "rumble.ogg"))
expl_sounds = [
    pygame.mixer.Sound(os.path.join("sound", "expl0.wav")),
    pygame.mixer.Sound(os.path.join("sound", "expl1.wav"))
]
pygame.mixer.music.load(os.path.join("sound", "background.ogg"))
pygame.mixer.music.set_volume(0.4)

font_name = os.path.join("font.ttf")
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surf.blit(text_surface, text_rect)

def new_rock():
    r = Rock()
    all_sprites.add(r)
    rocks.add(r)

def draw_health(surf, hp, x, y):
    if hp < 0:
        hp = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (hp/100)*BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

def draw_lives(surf, lives, img, x, y):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 32*i
        img_rect.y = y
        surf.blit(img, img_rect)

def draw_init():
    screen.blit(background_img, (0, 0))
    draw_text(screen, "星際大戰爭", 64, WIDTH/2, HEIGHT/4)
    draw_text(screen, "← →移動飛船 空白艦發射子彈~", 22, WIDTH/2, HEIGHT/2)
    draw_text(screen, "按任意鍵開始遊戲", 18, WIDTH/2, HEIGHT*3/4)
    pygame.display.update()
    waiting = True
    while waiting:
        clock.tick(FPS)                                         # 一秒鐘之內最多被執行FPS次
        # 取得輸入
        for event in pygame.event.get():                        # .get 模組會回傳現在發生的所有事件
            if event.type == pygame.QUIT:                       # 檢查事件類型是否把檔案關閉
                pygame.quit()
            elif event.type == pygame.KEYUP:                  # 檢查事件類型是否按下按鍵
                waiting = False

# sprite 表示畫面上使用的所有東西
class Player(pygame.sprite.Sprite):
    def __init__(self):
        # call 內建 sprite 的初始函式(image 圖片, rect 定位)
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (50, 38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()                   # get_rect 把圖片定位, 框起來
        self.radius = 20
        self.rect.centerx = WIDTH/2
        self.rect.bottom = HEIGHT - 10                      # 離最底部 10
        self.speedx = 8
        self.health = 100
        self.lives = 3
        self.hidden = False
        self.hide_time = 0
        self.gun = 1
        self.gun_time = 0

    def update(self):
        now = pygame.time.get_ticks()
        if self.gun > 1 and now - self.gun_time > 5000:
            self.gun -= 1
            self.gun_time = now

        if self.hidden and now - self.hide_time > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH/2
            self.rect.bottom = HEIGHT - 10
        
        key_pressed = pygame.key.get_pressed()              # key.get_pressed 一連串的布林值 判斷按鍵是否被按下
        if key_pressed[pygame.K_RIGHT]:                     # 判斷 d 鍵是否被按下
            self.rect.x += self.speedx
        if key_pressed[pygame.K_LEFT]:                      # 判斷 a 鍵是否被按下
            self.rect.x -= self.speedx    

        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        if not(self.hidden):
            if self.gun == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            elif self.gun >=2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound.play()

    def hide(self):
        self.hidden = True
        self.hide_time = pygame.time.get_ticks()
        self.rect.center = (WIDTH/2, HEIGHT+500)

    def gunup(self):
        self.gun += 1
        self.gun_time = pygame.time.get_ticks()

class Rock(pygame.sprite.Sprite):
    def __init__(self):
        # call 內建 sprite 的初始函式(image 圖片, rect 定位)
        pygame.sprite.Sprite.__init__(self)
        self.image_ori = random.choice(rock_imgs)
        self.image_ori.set_colorkey(BLACK)
        self.image = self.image_ori.copy()
        self.rect = self.image.get_rect()                   # get_rect 把圖片定位, 框起來
        self.radius = int(self.rect.width * 0.85 / 2)
        self.rect.x = random.randrange(0,WIDTH - self.rect.width)
        self.rect.y = random.randrange(-180, -100)           # 離最底部 10
        self.speedy = random.randrange(2, 5)
        self.speedx = random.randrange(-3, 3)               # 一負一正才會有往左或往右跑
        self.total_degree = 0
        self.rot_degree = random.randrange(-3, 3)

    def rotate(self):
        self.total_degree += self.rot_degree
        self.total_degree = self.total_degree % 360
        self.image = pygame.transform.rotate(self.image_ori, self.total_degree)
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center

    def update(self):
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
            self.rect.x = random.randrange(0,WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)           
            self.speedy = random.randrange(2, 10)
            self.speedx = random.randrange(-3, 3)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        # call 內建 sprite 的初始函式(image 圖片, rect 定位)
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()                   # get_rect 把圖片定位, 框起來
        self.rect.centerx = x                               # 子彈的中心
        self.rect.bottom = y                                # 子彈的底部
        self.speedy = -10
    

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:                            # 子彈底部超出畫面
            self.kill()                                     # 從所有有子彈的sprite群組中刪除

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        # call 內建 sprite 的初始函式(image 圖片, rect 定位)
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = expl_anim[self.size][0]
        self.rect = self.image.get_rect()                   
        self.rect.center = center                           
        self.frame = 0                            
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50
    

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(expl_anim[self.size]):
                self.kill()
            else:
                self.image = expl_anim[self.size][self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = center

class Power(pygame.sprite.Sprite):
    def __init__(self, center):
        # call 內建 sprite 的初始函式(image 圖片, rect 定位)
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(["shield", "gun"])
        self.image = power_imgs[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()                   
        self.rect.center = center                  
        self.speedy = 3
    

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:                      
            self.kill()

all_sprites = pygame.sprite.Group()
rocks = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powers = pygame.sprite.Group()
player = Player()
all_sprites.add(player)
for i in range(8):
    new_rock()
    score = 0
pygame.mixer.music.play(-1)

# 遊戲迴圈
show_init = True
running = True
while running:
    if show_init:
        draw_init()
        show_init = False
        # 創建一個 sprite 群組
        all_sprites = pygame.sprite.Group()
        rocks = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powers = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        for i in range(8):
            new_rock()
        score = 0

    clock.tick(FPS)                                         # 一秒鐘之內最多被執行FPS次
    # 取得輸入
    for event in pygame.event.get():                        # .get 模組會回傳現在發生的所有事件
        if event.type == pygame.QUIT:                       # 檢查事件類型是否把檔案關閉
            running = False
        elif event.type == pygame.KEYDOWN:                  # 檢查事件類型是否按下按鍵
            if event.key == pygame.K_SPACE:                 # 是否按下空白鍵
                player.shoot()


    # 更新遊戲
    all_sprites.update()                                    # 會去執行這個群組裡面, 每一個 update 函式
    # 更新子彈跟石頭的位置, 後兩欄為是否刪掉
    # hits 會回傳字典, 是撞到的石頭跟子彈
    hits = pygame.sprite.groupcollide(rocks, bullets, True, True)
    for hit in hits:
        random.choice(expl_sounds).play()
        score += hit.radius
        expl = Explosion(hit.rect.center, "lg")
        all_sprites.add(expl)
        if random.random() > 0.91:
            pow = Power(hit.rect.center)
            all_sprites.add(pow)
            powers.add(pow)
        new_rock()

    hits = pygame.sprite.spritecollide(player, rocks, True, pygame.sprite.collide_circle)
    for hit in hits:
        new_rock()
        player.health -= hit.radius
        expl = Explosion(hit.rect.center, "sm")
        all_sprites.add(expl)
        if player.health <= 0:
            death_expl = Explosion(player.rect.center, "player")
            all_sprites.add(death_expl)
            die_sound.play()
            player.lives -= 1
            player.health = 100
            player.hide()

    hits = pygame.sprite.spritecollide(player, powers, True)
    for hit in hits:
        if hit.type == "shield":
            player.health += 30
            if player.health > 100:
                player.health =100
                shield_sound.play()
        elif hit.type == "gun":
            player.gunup()
            gun_sound.play()

    if player.lives == 0 and not(death_expl.alive()):
        show_init = True

    # 畫面顯示
    screen.fill((BLACK))                                    # (Red,Green,Blue) RGB配色表
    screen.blit(background_img, (0, 0))
    all_sprites.draw(screen)                                # 把 sprite 群組顯示在畫面上
    draw_text(screen, str(score), 18, WIDTH/2, 10)
    draw_health(screen, player.health, 5, 15)
    draw_lives(screen, player.lives, player_mini_img, WIDTH - 100, 15)
    pygame.display.update()                                 # 畫面要更新


pygame.quit()
