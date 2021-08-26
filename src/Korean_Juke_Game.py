import pygame
from pygame.locals import *

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 1200
screen_height = 800

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Korean Juke Game')

#define game variables
main_menu = True
credits_menu = False
tile_size = 50
game_over = 0
red_switches_state = 0
blue_switches_state = 0
is_ball_picked_up = 0

#load images
background_image = pygame.image.load(f'img/background.bmp')
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))
start_image = pygame.image.load(f'img/button/start.png')
start_image = pygame.transform.scale(start_image, (2*tile_size, 2*tile_size))
exit_image = pygame.image.load(f'img/button/exit.png')
exit_image = pygame.transform.scale(exit_image, (2*tile_size, 2*tile_size))
title_image = pygame.image.load(f'img/title.png')
title_image = pygame.transform.scale(title_image, (12*tile_size, 6*tile_size))

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False

        #get mouse position
        pos = pygame.mouse.get_pos()

        #check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        #draw button
        screen.blit(self.image, self.rect)

        return action

class Player():
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self):
        dx = 0
        dy = 0
        walk_cooldown = 10
        global game_over, red_switches_state, blue_switches_state, is_ball_picked_up, credits_menu

        if game_over == 0:

            #get key presses
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped == False and is_ball_picked_up == False:
                self.vel_y = -18
                self.jumped = True
            if key[pygame.K_LEFT]:
                dx -= 5
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx += 5
                self.counter += 1
                self.direction = 1
            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                self.counter = 0
                self.index = 0
                self.image = self.images_left[self.index]
            
            #animation
            if is_ball_picked_up == 0:
                if self.counter > walk_cooldown:
                    self.counter = 0
                    self.index += 1
                    if self.index >= len(self.images_left):
                        self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]
            if is_ball_picked_up == 1:
                if self.counter > walk_cooldown:
                    self.counter = 0
                    self.index += 1
                    if self.index >= len(self.images_left_with_ball):
                        self.index = 0
                if self.direction == 1:
                    self.image = self.images_right_with_ball[self.index]
                if self.direction == -1:
                    self.image = self.images_left_with_ball[self.index]

            #gravity
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            #check for collision
            for tile in world.tile_list:
                #check for collision in x direction
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0

                #check for collision in y direction
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    #check of below the ground i.e. jumping
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    #check of below the ground i.e. falling
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.jumped = False

            #check for collision with enemies
            if pygame.sprite.spritecollide(self, ant_group, False):
                game_over = -1
            
            if pygame.sprite.spritecollide(self, end_blocks_group, False) and is_ball_picked_up:
                credits_menu = True
            if pygame.sprite.spritecollide(self, end_blocks_group, False) and is_ball_picked_up == False:
                game_over = -1

            #update player coords
            self.rect.x += dx
            self.rect.y += dy

        #draw player onto screen
        if is_ball_picked_up:
            screen.blit(self.image, (self.rect.x, self.rect.y - 20))
        else:
            screen.blit(self.image, self.rect)

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.images_right_with_ball = []
        self.images_left_with_ball = []
        self.index = 0
        self.counter = 0
        for num in range(2):
            img_left = pygame.image.load(f'img/juke{num}.png')
            img_left = pygame.transform.scale(img_left, (80, 40))
            img_right = pygame.transform.flip(img_left, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        for num in range(2):
            img_left = pygame.image.load(f'img/juke_with_ball{num}.png')
            img_left = pygame.transform.scale(img_left, (80, 60))
            img_right = pygame.transform.flip(img_left, True, False)
            self.images_right_with_ball.append(img_right)
            self.images_left_with_ball.append(img_left)
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.switched = False
        self.direction = 0

class World():
    def __init__(self, data):
        self.tile_list = []
        self.transparent_blocks = []
        global ball

        #load images
        dirt_img = pygame.image.load('img/dirt.png')
        dirt_with_grass_img = pygame.image.load('img/dirt_with_grass.png')
        transparent_red_block = pygame.image.load('img/red/red_transparent.png')
        transparent_blue_block = pygame.image.load('img/blue/blue_transparent.png')
        blank = pygame.image.load('img/blank.png')
        end_image = pygame.image.load('img/start_tent.png')
        plane = pygame.image.load('img/end_plane.png')

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(dirt_with_grass_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    ant = Enemy(col_count * tile_size, row_count * tile_size + tile_size//2)
                    ant_group.add(ant)
                if tile == 4:
                    img = pygame.transform.scale(transparent_blue_block, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.transparent_blocks.append(tile)
                    blue_block = BlueBlock(col_count * tile_size, row_count * tile_size)
                    block_tile = (blue_block.image, blue_block.rect)
                    self.tile_list.append(block_tile)
                    blue_block_group.add(blue_block)
                if tile == 5:
                    img = pygame.transform.scale(transparent_red_block, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.transparent_blocks.append(tile)
                    red_block = RedBlock(col_count * tile_size + 1000, row_count * tile_size + 1000)
                    block_tile = (red_block.image, red_block.rect)
                    self.tile_list.append(block_tile)
                    red_block_group.add(red_block)
                if tile == 6:
                    img = pygame.transform.scale(end_image, (tile_size*2, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.transparent_blocks.append(tile)
                    end_block = EndBlock(col_count * tile_size, row_count * tile_size)
                    end_blocks_group.add(end_block)
                if tile == 8:
                    blue_switch = BlueSwitch(col_count * tile_size, row_count * tile_size)
                    blue_switch_group.add(blue_switch)
                if tile == 9:
                    red_switch = RedSwitch(col_count * tile_size, row_count * tile_size)
                    red_switch_group.add(red_switch)
                if tile == 10:
                    ball = Ball(col_count * tile_size, row_count * tile_size)
                    ball_group.add(ball)
                if tile == 11:
                    img = pygame.transform.scale(plane, (tile_size*2, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.transparent_blocks.append(tile)
                col_count += 1
            row_count += 1
    
    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
        for block in self.transparent_blocks:
            screen.blit(block[0], block[1])


class Switch(pygame.sprite.Sprite):
    def __init__(self, x, y, switchPath):
        pygame.sprite.Sprite.__init__(self)
        self.switch_images = []
        self.index = 0
        self.switch_state = 0
        for num in range(2):
            img = pygame.image.load(self.switchPath.format(num))
            img = pygame.transform.scale(img, (tile_size, tile_size))
            self.switch_images.append(img)
        self.image = self.switch_images[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class RedSwitch(Switch):
    def __init__(self, x, y):
        self.switchPath = 'img//redSwitch{}.png'
        Switch.__init__(self, x, y, self.switchPath)
    
    def update(self):
        global red_switches_state
        if game_over == 0:
            if self.switch_state == 0:
                self.index = 1
                self.switch_state = 1
            else:
                self.index = 0
                self.switch_state = 0
        else:
            self.index = 0
            self.switch_state = 0
        self.image = self.switch_images[self.index]
        red_switches_state = self.switch_state


class BlueSwitch(Switch):
    def __init__(self, x, y):
        self.switchPath = 'img//blueSwitch{}.png'
        Switch.__init__(self, x, y, self.switchPath)
    
    def update(self):
        global blue_switches_state
        if game_over == 0:
            if self.switch_state == 0:
                self.index = 1
                self.switch_state = 1
            else:
                self.index = 0
                self.switch_state = 0
        else:
            self.index = 0
            self.switch_state = 0
        self.image = self.switch_images[self.index]
        blue_switches_state = self.switch_state
            

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images_left = []
        self.images_right = []
        self.index = 0
        for num in range(2):
            img_left = pygame.image.load(f'img/ant{num}.png')
            img_left = pygame.transform.scale(img_left, (tile_size, tile_size//2))
            img_right = pygame.transform.flip(img_left, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0
        self.animation_counter = 0
    
    def update(self):
        global game_over
        walk_cooldown = 10
        self.rect.x += self.move_direction
        self.move_counter += 1
        self.animation_counter += 1
        if self.move_counter > 100:
            self.move_direction *= -1
            self.move_counter *= -1
        
        #animation
        if self.animation_counter > walk_cooldown:
            self.animation_counter = 0
            self.index += 1
            if self.index >= len(self.images_left):
                self.index = 0
        if self.move_direction == 1:
            self.image = self.images_right[self.index]
        if self.move_direction == -1:
            self.image = self.images_left[self.index]
        
        #collision with ball
        if pygame.sprite.spritecollide(self, ball_group, False):
            game_over = -1

class Ball(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(f'img/korea_ball.png')
        self.image = pygame.transform.scale(self.image, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.is_picked_up = False
    
    def update(self, world_data, player):
        global is_ball_picked_up
        if game_over == 0:
            if self.is_picked_up:
                block_px = (player.rect.x+40)//50
                if block_px % 50 > 25:
                    block_px += 1
                block_py = (player.rect.y+20)//50
                if block_py % 50 > 25:
                    block_py += 1
                if world_data[block_py + 1][block_px] == 1 or world_data[block_py + 1][block_px] == 2:
                    world_data[block_py][block_px] = 10
                    self.rect.x = block_px * 50
                    self.rect.y = block_py * 50
                    self.is_picked_up = False
                    is_ball_picked_up = self.is_picked_up
            else:
                block_px = (self.rect.x+40)//50
                if block_px % 50 > 25:
                    block_px += 1
                block_py = (self.rect.y+20)//50
                if block_py % 50 > 25:
                    block_py += 1
                world_data[block_py][block_px] = 0
                self.rect.x = 100000
                self.rect.y = 100000
                self.is_picked_up = True
                is_ball_picked_up = self.is_picked_up
        else:
            self.rect.x = 4 * 50
            self.rect.y = 2 * 50
            self.is_picked_up = is_ball_picked_up

class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, image_path):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.start_x = x
        self.start_y = y

class RedBlock(Block):
    def __init__(self, x, y):
        self.image_path = f'img/red/dirt.png'
        Block.__init__(self, x, y, self.image_path)
    
    def update(self):
        if game_over == 0:
            if red_switches_state == 0:
                self.rect.x = self.rect.x + 1000
                self.rect.y = self.rect.y + 1000
            else:
                self.rect.x = self.rect.x - 1000
                self.rect.y = self.rect.y - 1000
        else:
            self.rect.x = self.start_x
            self.rect.y = self.start_y

class BlueBlock(Block):
    def __init__(self, x, y):
        self.image_path = f'img/blue/dirt.png'
        Block.__init__(self, x, y, self.image_path)
    
    def update(self):
        if game_over == 0:
            if blue_switches_state == 0:
                self.rect.x = self.rect.x - 1000
                self.rect.y = self.rect.y - 1000
            else:
                self.rect.x = self.rect.x + 1000
                self.rect.y = self.rect.y + 1000
        else:
            self.rect.x = self.start_x
            self.rect.y = self.start_y

class EndBlock(Block):
    def __init__(self, x, y):
        self.image_path = f'img/blank.png'
        Block.__init__(self, x, y, self.image_path)

world_data = [
[1, 11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 8, 2, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 9, 2, 1, 0, 2, 2, 1, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 2, 2, 2, 2, 2, 4, 4, 2, 2, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 3, 0, 0, 0, 0, 1, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 1], 
[1, 2, 2, 2, 2, 2, 0, 0, 1, 2, 2, 2, 2, 2, 2, 4, 4, 4, 2, 2, 2, 2, 2, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 8, 0, 4, 0, 0, 0, 5, 0, 0, 3, 0, 0, 0, 0, 8, 1], 
[1, 0, 0, 2, 2, 5, 5, 5, 2, 2, 5, 5, 5, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1], 
[1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
[1, 6, 0, 1, 0, 0, 3, 0, 0, 0, 0, 3, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
[1, 1, 1, 1, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1] 
]

player = Player(tile_size, tile_size)

ant_group = pygame.sprite.Group()

red_switch_group = pygame.sprite.Group()
blue_switch_group = pygame.sprite.Group()
ball_group = pygame.sprite.Group()
blue_block_group = pygame.sprite.Group()
red_block_group = pygame.sprite.Group()
end_blocks_group = pygame.sprite.Group()

world = World(world_data)

#buttons
start_button = Button(screen_width // 2 - 50, screen_height // 2, start_image)
exit_button = Button(screen_width // 2 - 50, screen_height // 2  + 125, exit_image)

#credits variables
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
darkBlue = (0,0,128)
white = (255,255,255)
black = (0,0,0)
pink = (255,200,200)

movie_credits = '''
KOREAN JUKE GAME

SEBASTIAN SKROBICH      level designer
ŁUKASZ WYLEGAŁA         game director
TEN CO JE CHLEB         graphic designer

POZNAN 2021
'''

centerx, centery = screen.get_rect().centerx, screen.get_rect().centery
deltaY = centery + 50 

run = True
while run:

    clock.tick(fps)
    screen.blit(background_image, (0, 0))

    if main_menu == True:
        screen.blit(title_image, (screen_width // 2 - 6*tile_size, screen_height // 2 - 7*tile_size))
        if exit_button.draw():
            run = False
        if start_button.draw():
            main_menu = False
    elif credits_menu == True:
        screen.fill(0)
        deltaY-= 1
        i=0
        msg_list=[]
        pos_list=[]
        
        font = pygame.font.SysFont('Courier', 30)

        for line in movie_credits.split('\n'):
            msg=font.render(line, True, white)
            msg_list.append(msg)
            pos= msg.get_rect(center=(centerx, centery+deltaY+30*i))
            pos_list.append(pos)
            i=i+1
    
        for j in range(i):
            screen.blit(msg_list[j], pos_list[j])

    else:

        world.draw()

        if game_over == 0:
            ant_group.update()

        ant_group.draw(screen)

        red_switch_group.draw(screen)
        blue_switch_group.draw(screen)
        ball_group.draw(screen)
        blue_block_group.draw(screen)
        red_block_group.draw(screen)
        end_blocks_group.draw(screen)

        player.update()

        if game_over == -1:
            player.reset(tile_size, tile_size)
            red_switches_state = 0
            blue_switches_state = 0
            is_ball_picked_up = 0
            ball_group.update(world_data, player)
            red_switch_group.update()
            blue_switch_group.update()
            blue_block_group.update()
            red_block_group.update()
            game_over = 0
 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e:
                        if pygame.sprite.spritecollide(player, red_switch_group, False):
                            red_switch_group.update()
                            red_block_group.update()
                        if pygame.sprite.spritecollide(player, blue_switch_group, False):
                            blue_switch_group.update()
                            blue_block_group.update()
                    if event.key == pygame.K_g:
                        if pygame.sprite.spritecollide(player, ball_group, False) and is_ball_picked_up == 0:
                            player.rect.y = player.rect.y - 20
                            ball_group.update(world_data, player)
                        elif is_ball_picked_up == 1:
                            ball_group.update(world_data, player)
    pygame.display.update()

pygame.quit()



