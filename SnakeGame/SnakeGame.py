import random, pygame, time, math
import numpy as np

class SnakeGame(): 
	"""docstring for SnakeGame"""
	def __init__(self):
		self.screenSize = (100,200)
		self.snakePos = [40,20]
		self.snakeBody = [[40,20],[30,20],[20,20]]
		self.foodPos = [random.randrange(1,self.screenSize[0]/10  )*10,random.randrange(1,self.screenSize[1]/10 )*10]
		#self.snakePos = [100,50]
		#self.snakeBody = [[100,50],[90,50],[80,50]]
		self.foodSpawn = True
		self.score = 0
		self.initPyGame()
		# Play Surface
		self.PlaySurface = pygame.display.set_mode(self.screenSize)
		pygame.display.set_caption('SnakeGame!')
		self.fpsController= pygame.time.Clock()
		# Controlling 
		self.directions = ['RIGHT','LEFT','UP','DOWN']
		# 0 Right, 1 Left, 2 Up, 3 Down 
		self.historique = []



	def initPyGame(self):
		check_errors = pygame.init()
		if check_errors[1] > 0:
			print('(!) had {0} initializing errors, exiting...'.format(check_errors[1]))
			sys.exit(-1)
		else :
			print('(+) PyGame successfully initialized!')


	def render(self):
		# Colors
		pygame.event.get()
		red   = pygame.Color(255,0,0)   	# Snake Head
		green = pygame.Color(0,255,0) 		# Snake Body
		black = pygame.Color(0,0,0)   		# Score
		white = pygame.Color(255,255,255) 	# Background
		brown = pygame.Color(165,42,42) 	# Food
		self.PlaySurface.fill(white)
		for pos in self.snakeBody[1:] :
			pygame.draw.rect(self.PlaySurface,green,pygame.Rect(pos[0],pos[1],10,10))
		pygame.draw.rect(self.PlaySurface,red,pygame.Rect(self.snakeBody[0][0],self.snakeBody[0][1],10,10))
		if self.foodSpawn:
			pygame.draw.rect(self.PlaySurface,brown,pygame.Rect(self.foodPos[0],self.foodPos[1],10,10))
		pygame.display.flip()
		self.fpsController.tick(30)



	def isDone(self):
		for block in self.snakeBody[1:]:
			if self.snakePos[0]==block[0] and self.snakePos[1]==block[1]:
				return 1

		if self.snakePos[0]>self.screenSize[0] - 10 or self.snakePos[0]<0 or self.snakePos[1]>self.screenSize[1] - 10 or self.snakePos[1]<0 :
			return 1
		return 0


	def getObservation(self,direction): 
		x,y = self.snakePos[0],self.snakePos[1]

		def loop(x_inc,y_inc,x_head,y_head):
			distance = 0
			base_distance = math.hypot(x_inc,y_inc)
			food = -1
			body = -1
			wall = -1
			# Moving the head
			x = x_head + x_inc
			y = y_head + y_inc

			while  x > -1 and y > -1 and x < self.screenSize[0] and y < self.screenSize[1]:
				if [x,y] in self.snakeBody:
					if body == -1:
						body = distance
				if [x,y] == self.foodPos:
					if food == -1:
						food = distance
				# Moving further
				distance += base_distance

				if x == 0 or y == 0 or x == self.screenSize[0] or y == self.screenSize[1]:
					if wall == -1:
						wall = distance

				x += x_inc
				y += y_inc

			max_dist = math.hypot(self.screenSize[0],self.screenSize[1])

			if body == -1 :
				body = max_dist
			if food == -1 :
				food = max_dist
			if wall == -1 :
				wall = max_dist

			return [wall, food, body]
		
		if direction == 'LEFT':
			observation = np.array([loop(-10, 0, x, y),loop(-10, -10, x, y),loop(0, -10, x, y),loop(10, -10, x, y),loop(10, 0, x, y),loop(10, 10, x, y),loop(0, 10, x, y),loop(-10, 10, x, y)])
		elif direction == 'RIGHT':
			observation = np.array([loop(10, 0, x, y),loop(10, 10, x, y),loop(0, 10, x, y),loop(-10, 1, x, y),loop(-10, 0, x, y),loop(-10, -10, x, y),loop(0, -10, x, y),loop(10, -10, x, y)])
		elif direction == 'UP':
			observation = np.array([loop(0, -10, x, y),loop(10, -10, x, y),loop(10, 0, x, y),loop(10, 10, x, y),loop(0, 10, x, y),loop(-10, 10, x, y),loop(-10, 0, x, y),loop(-10, -10, x, y)])
		elif direction == 'DOWN':
			observation = np.array([loop(0, 10, x, y),loop(-10, 10, x, y),loop(-10, 0, x, y),loop(-10, -10, x, y),loop(0, -10, x, y),loop(10, -10, x, y),loop(10, 0, x, y),loop(10, 10, x, y)])
		
		max_dist = math.hypot(self.screenSize[0],self.screenSize[1])
		observation.shape = (24,)
		observation_scaled = 1 - 2 * observation / max_dist
		return observation_scaled




	def getReward(self): 
		new_distance_food = abs(self.snakePos[0] - self.foodPos[0]) + abs(self.snakePos[1] - self.foodPos[1])
		old_distance_food = abs(self.snakeBody[1][0] - self.foodPos[0]) + abs(self.snakeBody[1][1] - self.foodPos[1])

		if not self.foodSpawn:
			return 10
		elif new_distance_food < old_distance_food:
			return 2
		else :
			return -1.5


	def step(self,action):
		direction  = self.directions[action]
		if  direction == 'RIGHT':
			self.snakePos[0] += 10
		elif direction == 'LEFT':
			self.snakePos[0] -= 10
		elif  direction == 'DOWN':
			self.snakePos[1] += 10
		elif  direction == 'UP':
			self.snakePos[1] -= 10

		# Snake body mechanism
		self.snakeBody.insert(0,list(self.snakePos))

		if self.snakePos[0]==self.foodPos[0] and self.snakePos[1]==self.foodPos[1]:
			self.score +=1
			self.foodSpawn=False
		else :
			self.snakeBody.pop()
		obs,reward,done,info = self.getObservation(direction),self.getReward(),self.isDone(),self.score
		if not self.foodSpawn :
			while True:
				self.foodPos=[random.randrange(1,self.screenSize[0]/10 -1)*10,random.randrange(1,self.screenSize[1]/10-1)*10]  
				if self.foodPos not in self.snakeBody:
					break
			self.foodSpawn=True

		return obs,reward,done,info

	def reset(self):
		self.snakePos = [40,20]
		self.snakeBody = [[40,20],[30,20],[20,20]]
		self.foodPos = [random.randrange(1,self.screenSize[0]/10 -1)*10,random.randrange(1,self.screenSize[1]/10-1)*10]
		self.foodSpawn = True
		self.score = 0

	def greedy(self,lastDirection):
		self.historique.append(lastDirection)
		if len(self.historique) > 2:
			self.historique.pop(0)

		if self.checkSquare() :
			for i in range(0,4) :
				if self.check(i):
					direction = i
		else:
			direction  = lastDirection

		changed = False

		if self.snakePos[0] < self.foodPos[0]  and self.snakePos[0] < self.screenSize[0] -10 and  direction != 1 and self.check(0):
			direction = 0
			changed = True
		elif self.snakePos[0] > self.foodPos[0] and self.snakePos[0] > 0 and direction != 0 and self.check(1):
			direction = 1
			changed = True

		else :
			if self.snakePos[1] <  self.foodPos[1] and self.snakePos[1] < self.screenSize[1] - 10 and direction != 2 and self.check(3):
				direction = 3
				changed = True

			elif self.snakePos[1] >  self.foodPos[1] and self.snakePos[1] > 0 and direction != 3 and self.check(2):
				direction = 2
				changed = True
		if not changed :
			if  self.snakePos[0] < self.screenSize[0]-10  and self.check(0)  and 1 not in self.historique:
				direction = 0
			elif self.snakePos[0] > 0  and self.check(1) and 0 not in self.historique:
				direction = 1
			elif  self.snakePos[1] < self.screenSize[1] - 10  and  self.check(3) and 2 not in self.historique:
				direction = 3
			elif  self.snakePos[1] > 0  and  self.check(2) and 3 not in self.historique:
				direction = 2
		return direction


	def checkSquare(self):
		horiz = 0
		vertc = 0
		for block in self.snakeBody:
			if block[0] == self.foodPos[0]:
				horiz +=1
			if block[1] == self.foodPos[1]:
				vertc +=1
		if horiz == 2 and vertc == 2:
			return True
		return False


	def check(self,direction):

		simPos = self.snakePos[:]
		simBody = self.snakeBody[:]
		direction = self.directions[direction]

		if direction == "RIGHT" :
			while simPos[0] <= self.screenSize[0] - 10:
				for block in simBody[1:]:
					if block[0] == simPos[0] and block[1] == simPos[1]:
						return False
				simPos[0]+=10
				simBody.pop()
				simBody.insert(0,list(simPos))
			return True
		elif direction == "LEFT" :
			while simPos[0] >= 0:
				for block in simBody[1:]:
					if block[0] == simPos[0] and block[1] == simPos[1]:
						return False
				simPos[0]-=10
				simBody.pop()
				simBody.insert(0,list(simPos))
			return True
		elif direction == "UP" :
			while simPos[1] >= 0 :
				for block in simBody[1:]:
					if block[0] == simPos[0] and block[1] == simPos[1]:
						return False
				simPos[1]-=10
				simBody.pop()
				simBody.insert(0,list(simPos))
			return True
		elif direction == "DOWN" :
			while simPos[1] <= self.screenSize[1] - 10 :
				for block in simBody[1:]:
					if block[0] == simPos[0] and block[1] == simPos[1]:
						return False
				simPos[1]+=10
				simBody.pop()
				simBody.insert(0,list(simPos))
			return True
