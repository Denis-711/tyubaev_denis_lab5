import pygame as pg
import numpy as np
from random import randint

SCREEN_SIZE = (800, 600)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

pg.init()


class Ball():
    def __init__(self, coord, vel, rad = 15, color = None):
        '''
        Function initializes the ball with certain initial location and speed.
        
        Keyword arguments:
        coord -- list of (x,y) initial coordinates
        vel -- initial balls speed
        '''
        if color == None:
            color = (randint(0, 255), randint(0, 255), randint(0, 255))
        self.color = color
        self.coord = coord
        self.vel = vel
        self.rad = rad
        self.is_alive = True

    def draw(self, screen):
        '''
        Function draws the ball.
        '''
        pg.draw.circle(screen, self.color, self.coord, self.rad)

    def move(self, t_step = 1., g = 2.):
        '''
        Function calculates coordinates of the ball at a certain point in time,
        considering collisions with walls and
        deactivates stopped balls.
        
        Keyword arguments:
        t_step -- quantum of time for which the quantum of motion is calculated. 
        '''
        self.vel[1] += int(g * t_step)
        for i in range(2):
            self.coord[i] += int(self.vel[i] * t_step)
        self.check_walls()
        if self.vel[0]**2 + self.vel[1]**2 < 2**2 and self.coord[1] > SCREEN_SIZE[1] - 2*self.rad:
               self.is_alive = False

    def check_walls(self):
        '''
        Function checks if the ball is outside the boundaries
        of the playing area, if so, then it moves the ball to the boundary and 
        calls a function that implements a collision with 
        the boundaries of the play area.
        '''
        n = [[1, 0], [0, 1]]
        for i in range(2):
            if self.coord[i] < self.rad:
                self.coord[i] = self.rad
                self.flip_vel(n[i], 0.8, 0.9)
            elif self.coord[i] > SCREEN_SIZE[i] - self.rad:
                self.coord[i] = SCREEN_SIZE[i] - self.rad
                self.flip_vel(n[i], 0.8, 0.9)

    def flip_vel(self, axis, coef_perp = 1., coef_par = 1.):
        '''
        Function changes direction of balls velocity and its module.
        
        Keyword arguments:
        axis -- array of 2 ints which defines axis around which velocity
                will be flipped
        coef_perp -- speeds parallel to the axis component reduction coefficient 
        coef_par -- speeds perpendicular to the axis component 
                    reduction coefficient
        '''
        vel = np.array(self.vel)
        n = np.array(axis)
        n = n / np.linalg.norm(n)
        vel_perp = vel.dot(n) * n
        vel_par = vel - vel_perp
        ans = -vel_perp * coef_perp + vel_par * coef_par
        self.vel = ans.astype(np.int).tolist()


class Table():
    pass


class Gun():
    def __init__(self, coord=[30, SCREEN_SIZE[1]//2], 
                 min_pow=20, max_pow=50):
        self.coord = coord
        self.angle = 0
        self.min_pow = min_pow
        self.max_pow = max_pow
        self.power = min_pow
        self.active = False

    def draw(self, screen):
        '''
        Function draws the gun with certain lenght and direction.
        '''
        end_pos = [self.coord[0] + self.power*np.cos(self.angle), 
                   self.coord[1] + self.power*np.sin(self.angle)]
        pg.draw.line(screen, RED, self.coord, end_pos, 5)

    def strike(self):
        '''
        Function creates ball with certain velocity dependint on guns power
        at the location of the gun and turns the gun off.
        Function returns list of (x,y) balls coordinates and velocity as an array.
        '''
        vel = [int(self.power * np.cos(self.angle)), int(self.power * np.sin(self.angle))]
        self.active = False
        self.power = self.min_pow
        return Ball(list(self.coord), vel)
        
    def move(self):
        '''
        Function increases guns lenght if it is active.
        '''
        if self.active and self.power < self.max_pow:
            self.power += 1

    def set_angle(self, mouse_pos):
        '''
        Function changes guns direction depending on the position of the mouse.
        
        Keyword arguments:
        mouse_pos -- array of (x,y) coordinates of the mouse.
        '''
        self.angle = np.arctan2(mouse_pos[1] - self.coord[1], 
                                mouse_pos[0] - self.coord[0])


class BaseTarget():
    def __init__(self, coord, vel, size, color):
        if color == None:
            color = randint((50, 255), randint(50, 255), randint(50,255))
        self.color = color
        self.coord = coord
        self.vel = vel
        self.rad = size
        self.is_alive = True

    def check_walls(self):
        n = [[1, 0]]
        for i in range(2):
            if self.coord[i] < self.rad:
                self.coord[i] = self.rad
                self.direction = (self.direction + 1) % 2 
                self.flip_vel(n[i])
            elif self.coord[i] > SCREEN_SIZE[i] - self.rad:
                self.coord[i] = SCREEN_SIZE[i] - self.rad
                self.flip_vel(n[i])
                self.direction = (self.direction + 1) % 2 
    
    def flip_vel(self, axis):
        vel = np.array(self.vel)
        n = np.array(axis)
        n = n / np.linalg.norm(n)
        vel_perp = vel.dot(n) * n
        vel_par = vel - vel_perp
        ans = -vel_perp + vel_par
        self.vel = ans.astype(np.int).tolist()

    def check_hit(self, ball):
        pass


class Rocket(BaseTarget):
    def __init__(self, coord, vel, rad = 10, color = (255, 0, 0)):
        super().__init__(coord, vel, rad, color)
        self.direction = 1
        self.coord = coord

    def draw(self, screen):
        surf = pg.Surface(SCREEN_SIZE, pg.SRCALPHA)
        circle_x = self.coord[0]
        circle_y = self.coord[1] + self.rad
        pg.draw.rect(surf, self.color, (self.coord, (4 * self.rad, 2 * self.rad)))
        pg.draw.circle(surf, self.color, (circle_x, circle_y), self.rad * 2)
        
        screen.blit(surf, (0, 0))
    
    def bombard(self):
        pass
    
    def move(self, t_step = 1.):
        for i in range(2):
            self.coord[i] += int(self.vel[i] * t_step)
        self.check_walls()
		

class Square(BaseTarget):
    def __init__(self, coord, vel, size = 10, color = (0, 255, 0)):
        super().__init__(self, coord, vel, size, color)

    def draw(self, screen):
        pass

    def move(self):
        pass
    

class Manager():
    def __init__(self):
        '''
        Function initializes the manager
        '''
        self.gun = Gun()
        self.table = Table()
        self.balls = []
        rocket_coord = [100, 100]
        rocket_vel = [10, 0]
        self.rockets = [Rocket(list(rocket_coord), rocket_vel)]
    
    def process(self, events, screen):
        done = self.handle_events(events)
        self.move()
        self.draw(screen)
        self.check_alive()
        return done

    def draw(self, screen):
        '''
        Function calls draw functions for game objects
        '''
        screen.fill(BLACK)
        for rocket in self.rockets:
            rocket.draw(screen)
        for ball in self.balls:
            ball.draw(screen)
        self.gun.draw(screen)

    def move(self):
        '''
        Function calls move functions for game objects
        '''
        for rocket in self.rockets:
            rocket.move()
        for ball in self.balls:
            ball.move()
        self.gun.move()

    def check_alive(self):
        '''
        Check if ball in balls array is alive and if it isnt then deletes it.
        '''
        dead_balls = []
        for i, ball in enumerate(self.balls):
            if not ball.is_alive:
                dead_balls.append(i)

        for i in reversed(dead_balls):
            self.balls.pop(i)
    
    def handle_events(self, events):
        '''
        Function processes events from the queue passed to it.
        
        Keyword arguments:
        events -- events queue
        '''
        done = False
        for event in events:
            if event.type == pg.QUIT:
                done = True
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.gun.coord[1] -= 5
                elif event.key == pg.K_DOWN:
                    self.gun.coord[1] += 5
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.gun.active = True
            elif event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    self.balls.append(self.gun.strike())
        
        if pg.mouse.get_focused():
            mouse_pos = pg.mouse.get_pos()
            self.gun.set_angle(mouse_pos)

        return done


screen = pg.display.set_mode(SCREEN_SIZE)
pg.display.set_caption("The gun of Khiryanov")
clock = pg.time.Clock()

mgr = Manager()

done = False

while not done:
    clock.tick(30)

    done = mgr.process(pg.event.get(), screen)

    pg.display.flip()

