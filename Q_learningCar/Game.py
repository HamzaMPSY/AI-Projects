import pygame
import pymunk
import sys
import random
import math
import numpy as np
from pygame.color import THECOLORS
from pymunk.vec2d import Vec2d
from pymunk.pygame_util import DrawOptions

# Global declaration if i need it 
positions =[]
def to_pygame(p):
    """Small hack to convert pymunk to pygame coordinates"""
    return int(p.x), int(600 - p.y)

class Car:

	def __init__(self, x, y):
		self.car_body = pymunk.Body(5, 1000)
		self.car_body.position = x, y
		self.image = pygame.image.load('car.png')
		x,y = self.image.get_size()
		x -= 10
		y -= 10
		self.car_shape = pymunk.Poly.create_box(self.car_body,(x,y))
		self.car_shape.friction = 0.5
		self.collision_type = 1
		
class Game:

	def __init__(self):
		# Pygame stuff
		pygame.init()
		self.size = (1000, 600)
		self.screen = pygame.display.set_mode(self.size)
		self.screen.set_alpha(None)
		self.clock = pygame.time.Clock()
		self.bg = pygame.image.load('map1.png')
		self.draw_options = DrawOptions(self.screen)
		# Physics stuff
		self.space = pymunk.Space()
		self.space.gravity = Vec2d(0., 0.)
		
		self.steps = 0
		self.exit = False
	
		
		#self.create_car(420, 480 ,0.0) # starting point for car map 2
		self.create_car(360, 530 ,0.0) # starting point for car map 1


		self.show_sonar = True
		



	def render(self):
		self.clock.tick(60)
		self.screen.fill((0,0,0))
		self.screen.blit(self.bg,(0,0))
		self.space.step(1/50.0)
		self.space.debug_draw(self.draw_options)
		p = self.car.car_body.position
		p = Vec2d(to_pygame(p))
		angle = math.degrees(self.car.car_body.angle)
		rotated_image = pygame.transform.rotate(self.car.image,angle)
		offset = Vec2d(rotated_image.get_size()) / 2.
		p  = p - (offset)
		self.screen.blit(rotated_image,(p.x, p.y))
		pygame.display.flip()

	def step(self,action):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.exit = True
			if event.type == pygame.MOUSEBUTTONDOWN:
				positions.append(pygame.mouse.get_pos())

		if len(positions)  > 0:
			for p in positions:
				print(p)
		if action == 0 :
			self.car.car_body.angle -= .0
		elif action == 1 :
			self.car.car_body.angle -= .2
		else:
			self.car.car_body.angle += .2
		
		self.steps += 1

		driving_direction = Vec2d(1, 0).rotated(self.car.car_body.angle)
		self.car.car_body.velocity = 100 * driving_direction
		self.space.step(1/50.0)

		# Get the state
		x, y = self.car.car_body.position
		readings = self.get_sonar_reading(x,y,self.car.car_body.angle)
		normalized_readings  = [ x/20.0 for x in readings]
		state = np.array(normalized_readings)
		# Get the reward

		if  1 in readings :
			self.crashed = True
			done = True
			reward = -1
			self.recover_from_crash(driving_direction)
		else :
			done = False
			reward = self.steps / 1000
			#print(reward)
		return state, reward, done


	def recover_from_crash(self,driving_direction):
		# for map 2
		#self.car.car_body.position=(420, 480)
		# for map 1
		self.car.car_body.position=(360, 530)
		self.car.car_body.angle = 0
		self.steps = 0
			

	def create_car(self,x,y,size=(30, 30)):
		self.car = Car(x,y)
		self.space.add(self.car.car_body,self.car.car_shape)


	def get_sonar_reading(self,x,y, angle):
		readings = []
		arm1 = self.make_sonar_arm(x,y)
		arm2 = arm1
		arm3 = arm1
		readings.append(self.get_arm_distances(arm1,x,y,angle,.5))
		readings.append(self.get_arm_distances(arm1,x,y,angle,0))
		readings.append(self.get_arm_distances(arm1,x,y,angle,-.5))
		pygame.display.update()
		return readings

	def get_arm_distances(self,arm,x,y,angle,offset):
		i = 0
		for point in arm:
			i+=1

			rotated_p = self.get_rotated_point(x, y, point[0], point[1], angle + offset)
			
			if rotated_p[0] <= 0 or rotated_p[1] <=0 or rotated_p[0] >= self.size[0] or rotated_p[1] >= self.size[1]:
				return i
			else :
				obs = self.screen.get_at(rotated_p)
				if self.get_track_or_not(obs) != 0:
					return i
			
			if self.show_sonar:
				pygame.draw.circle(self.screen, (255, 255, 255), (rotated_p), 2)

		return i

	def  get_track_or_not(self,point):
		if point  == THECOLORS["black"]:
			return 0
		else:
			return 1


	def get_rotated_point(self, x_1, y_1 , x_2, y_2 , radians):
		x_change = (x_2 - x_1) * math.cos(radians) + (y_2 - y_1) * math.sin(radians)
		y_change = (y_1 - y_2) * math.cos(radians) - (x_1 - x_2) * math.sin(radians)
		new_x = x_change + x_1
		new_y = self.size[1] - (y_change + y_1)
		return int(new_x), int(new_y)

	def make_sonar_arm(self,x,y):
		spread = 10 
		distance = 10
		arm_points = []
		for i in range(1,41):
			arm_points.append((distance+x + spread * i, y))

		return arm_points

