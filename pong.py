#!/usr/bin/python3
#
# Pong


VERSION = "0.1"
GAME_TITLE = "Pong v{0}".format(VERSION)

try:
    import sys
    import os
    import random
    import math    
    import pygame
    from pygame.locals import *
except ImportError as err:
	print("Couldn't load module. {0}".format(err))
	sys.exit(2)
    
SCREEN_WIDTH = 200
SCREEN_HEIGHT = 400
SCREEN_COLOR = (5, 5, 5)

BALL_RADIUS = 8 
BALL_COLOR = (250, 250, 250)
BALL_SPEED = 8

BAT_WIDTH = 40 
BAT_HEIGHT = 8
BAT_COLOR = (250, 250, 250)
BAT_SPEED = 4

SCORE_FONT_COLOR = (250, 250, 250)

FRAMES_PER_SECOND = 60

COURT_NORMAL = 0
COURT_OUTSIDE_TOP = 1
COURT_OUTSIDE_BOTTOM = 2

class Bat(pygame.sprite.Sprite):
    """Bat that can draw itself and know how to move
    Functions: move, draw, reset
    Attributes: rect, boundary, x_velocity
    """
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.Surface((BAT_WIDTH, BAT_HEIGHT))
        self.image.fill(BAT_COLOR)
        
        self.rect = self.image.get_rect()

        self.rect.x = x - BAT_WIDTH / 2
        self.rect.y = y - BAT_HEIGHT / 2
        
        self._start_rect = self.rect.copy()
        
        screen = pygame.display.get_surface()
        self.boundary = screen.get_rect()
        self.x_velocity = 0
        
    def move(self):
        new_pos = self.rect.move(self.x_velocity, 0)
        
        if self.boundary.contains(new_pos):
            self.rect = new_pos
    
    def draw(self, surface):
        surface.fill(BAT_COLOR, self.rect)
        
    def reset(self):
        """Sets the bat back to its original starting position"""
        self.rect = self._start_rect
        
    def update(self):
        if self.x_velocity != 0:
            self.move()

class PlayerBat(Bat):
    """Movable bat that allows one to hit the ball
    Functions: key_down, key_up, update 
    Attributes: rect, boundary, x_velocity"""
        
    def key_down(self, key):
        if key == K_LEFT:
            self.x_velocity -= BAT_SPEED
        elif key == K_RIGHT:
            self.x_velocity += BAT_SPEED
    
    def key_up(self, key):
        if key == K_LEFT:
            self.x_velocity += BAT_SPEED
        elif key == K_RIGHT:
            self.x_velocity -= BAT_SPEED
            

class AIBat(Bat):
    """AI bat that attempts to follow the ball
    Functions: update"""
   
    def update(self, ball):
        if ball.y <= SCREEN_HEIGHT / 4 * 3:
            if self.rect.x + BAT_WIDTH / 2 < ball.x:
                self.x_velocity = BAT_SPEED
            else:
                self.x_velocity = -BAT_SPEED
        elif self.x_velocity != 0:
            self.x_velocity = 0
            
        Bat.update(self)
       
class Ball:
    """A ball that bounces against the walls
    Returns: ball object
    Functions: move, draw, reset
    Attributes: x, y, vector, boundary, hit, offcourt"""
    
    def __init__(self, x, y, boundary):
        self._start_x = x
        self._start_y = y        
        self.boundary = boundary
        
        self.setup()
        
    def set_direction(self):
        angle = math.pi / 4 * (random.randint(1, 4) * 2 - 1)
        self.vector = (angle, BALL_SPEED)
        
    def move(self, bats):
        """Moves the ball and checks for collision with screen and bats"""
        angle, dist = self.vector
        self._new_pos()
        new_pos = Rect(self.x - BALL_RADIUS/2, self.y - BALL_RADIUS/2, BALL_RADIUS, BALL_RADIUS)
        
        # collision with screen
        if not self.boundary.contains(new_pos):
            top_left = not self.boundary.collidepoint(new_pos.topleft)
            top_right = not self.boundary.collidepoint(new_pos.topright)
            bot_left = not self.boundary.collidepoint(new_pos.bottomleft)
            bot_right = not self.boundary.collidepoint(new_pos.bottomright)
            
            # hit the top
            if (top_left and top_right):
                self.offcourt = COURT_OUTSIDE_TOP
            # hit the bottom
            elif (bot_left and bot_right):
                self.offcourt = COURT_OUTSIDE_BOTTOM
            # hit the side walls
            if (bot_left and top_left) or (bot_right and top_right):
                angle = math.pi - angle
                
        # collision checking with bat
        else: 
            set = False # flag when the ball bounces against something
            for bat in bats:
                if new_pos.colliderect(bat.rect) and not self.hit:
                    angle *= -1
                    
                    if math.sin(angle) > 0:
                        # down
                        self.y = bat.rect.top + BALL_RADIUS
                    else:
                        # up
                        self.y = bat.rect.bottom - BALL_RADIUS
                    
                    self.hit = True
                    set = True
                    break
                
                if self.hit and not set:
                    self.hit = False
                
        self.vector = (angle, dist)
    
    def draw(self, surface):
        pygame.draw.circle(surface, BALL_COLOR, (self.x, self.y), BALL_RADIUS)
        
    def setup(self):
        """Places the ball in original starting position and reset hit and offcourt"""
        self.x = self._start_x
        self.y = self._start_y
        self.hit = False
        self.offcourt = COURT_NORMAL
        
        self.set_direction()
    
    def _new_pos(self):
        angle, dist = self.vector
        self.x += dist * math.cos(angle)
        self.y += dist * math.sin(angle)
        self.x = int(self.x)
        self.y = int(self.y)


def draw_score(screen, font, score, x, y):
    score_text = font.render('Score: {0}'.format(score), False, SCORE_FONT_COLOR, SCREEN_COLOR)
    score_pos = score_text.get_rect()
    score_pos.centerx = screen.get_rect().centerx
    screen.blit(score_text, (x, y))
    

def main():
    pygame.init()
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(GAME_TITLE)
    
    clock = pygame.time.Clock()
    
    background = pygame.Surface(screen.get_size()).convert()
    background.fill(SCREEN_COLOR)
    
    score_font = pygame.font.Font(None, 24)      
    player_score = 0
    ai_score = 0    
    
    ball = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, screen.get_rect())
    player_bat = PlayerBat(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)
    ai_bat = AIBat(SCREEN_WIDTH // 2, 30)
       
    while True:        
        draw_score(background, score_font, player_score, 10, SCREEN_HEIGHT - 24)  
        draw_score(background, score_font, ai_score, 10, 12)
        
        screen.blit(background, (0, 0))
        
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return 
                elif event.key == K_d:
                    print(ball.vector)
                else:
                    player_bat.key_down(event.key)
            elif event.type == KEYUP:
                player_bat.key_up(event.key)
       
        player_bat.update()
        player_bat.draw(screen)
        
        ai_bat.update(ball)
        ai_bat.draw(screen)
        
        ball.move((player_bat, ai_bat))
        ball.draw(screen)
        
        if ball.offcourt:
            if ball.offcourt == COURT_OUTSIDE_BOTTOM:
                ai_score += 1
            elif ball.offcourt == COURT_OUTSIDE_TOP:
                player_score += 1
            ball.setup()
            player_bat.reset()
            ai_bat.reset()
         
        pygame.display.update()                
        clock.tick(FRAMES_PER_SECOND)     
        
    
if __name__ == "__main__":
    main()
