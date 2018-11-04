import pygame
import time
import json
import random

from pygame.locals import*
from time import sleep

class Sprite():
	def __init__(self):
		self.x = 0
		self.y = 0
		self.w = 0
		self.h = 0
		self.image = null

	def collisionDetection(self, mario, sprite, model):
		if(mario.x > sprite.x + sprite.w):
			return False
		if(mario.x + mario.w < sprite.x):
			return False
		if(mario.y > sprite.y + sprite.h):
			return False
		if(mario.y + mario.h < sprite.y):
			return False
		
		self.collisionHandler(mario,sprite, model)

		return True

	def collisionHandler(self, mario, sprite, model):
		if(sprite.isCoin()):
			return
		# Hits bottom
		elif(mario.y <= sprite.y + sprite.h and mario.prevY > sprite.y + sprite.h):
			mario.y = sprite.y + sprite.h + 1
			mario.verticalVelocity = 0

			if(sprite.isCoinBlock()):
				sprite.addCoin(sprite, model)
		# Hits right wall
		elif(mario.x <= sprite.x + sprite.w and mario.prevX > sprite.x + sprite.w):
			mario.x = sprite.x + sprite.w + 1
		# Lands on Top
		elif(mario.y + mario.h >= sprite.y and mario.prevY + mario.h < sprite.y):
			mario.y = sprite.y - mario.h - 1
			mario.verticalVelocity = 0
			mario.jumpTime = 0
		# Hits left wall
		elif(mario.x + mario.w >= sprite.x and mario.prevX < sprite.x):
			mario.x = sprite.x - mario.w - 1

	def isCoinBlock(self):
		return False
	
	def isMario(self):
		return False
	
	def isCoin(self):
		return False

	def isBrick(self):
		return False
	
	def update(self):
		return

class Mario(Sprite):
	def __init__(self, x,y):
		self.x = x
		self.y = y
		self.w = 60
		self.h = 95
		self.images = []
		self.reversedImages = []
		self.imageIndex = 0
		self.isFacingRight = True
		self.verticalVelocity = 0.0
		self.jumpTime = 0
		self.prevX = 0
		self.prevY = 0

		for i in range(5):
			self.images.append( pygame.image.load("mario" + str(i+1) + ".png"))
			self.reversedImages.append( pygame.image.load("rmario" + str(i+1) + ".png"))

	def locationPast(self):
		self.prevX = self.x
		self.prevY = self.y

	def imageCycle(self):
		if(self.imageIndex != 4):
			self.imageIndex += 1
		else:
			self.imageIndex = 0

	def getImage(self):
		if(self.isFacingRight):
			return self.images[self.imageIndex]
		else:
			return self.reversedImages[self.imageIndex]
	
	def jump(self):
		self.locationPast()
		if(self.jumpTime < 5):
			self.verticalVelocity -= 5
	

	def update(self):
		self.verticalVelocity += 1.2
		self.y += self.verticalVelocity

		if(self.y > 500):
			self.verticalVelocity = 0.0
			self.y = 500
			self.jumpTime = 0

		if(self.verticalVelocity == 0.0):
			self.jumpTime = 0
		else:
			self.jumpTime += 1

	def isMario(self):
		return True
		
class Brick(Sprite):
	def __init__(self, x, y, w, h):
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.image = pygame.image.load("brick.jpg")
		self.image = pygame.transform.scale(self.image, (self.w, self.h))

class Coin(Sprite):
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.w = 75
		self.h = 75
		self.image = pygame.image.load("coin.png")

		self.verticalVelocity = -15.0
		self.horizontalVelocity = random.randint(-10,10)
	
	def isCoin(self):
		return True
	
	def update(self):
		self.verticalVelocity += .5
		self.y += self.verticalVelocity
		self.x += self.horizontalVelocity

class CoinBlock(Sprite):
	def __init__(self, x,y,w,h):
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.coinCounter = 0

		self.images = []
		for i in range(2):
			self.images.append( pygame.image.load("block" + str(i+1) + ".png"))
			self.images[i] = pygame.transform.scale(self.images[i], (self.w, self.h))

	def isCoinBlock(self):
		return True
	
	def getImage(self):
		if(self.coinCounter > 4):
			return self.images[1]
		else:
			return self.images[0]
	
	def addCoin(self,sprite, model):
		if(self.coinCounter < 5):
			self.coinCounter += 1
			model.sprites.append( Coin(sprite.x, sprite.y - 20))

class Model():
	def __init__(self):
		self.sprites = []
		self.sprites.append( Mario(200,500) )
		self.mario = self.sprites[0]
		self.backgroundImage = pygame.image.load("bg.png")

		with open('maps.json') as f:
			data = json.load(f)
			
			for i in range(len(data["bricks"])):
				xx = data["bricks"][i]["x"] 
				yy = data["bricks"][i]["y"] 
				ww = data["bricks"][i]["w"]
				hh = data["bricks"][i]["h"]
				self.sprites.append( Brick(xx, yy, ww, hh))

			for i in range(len(data["coinblocks"])):
				xx = data["coinblocks"][i]["x"] 
				yy = data["coinblocks"][i]["y"] 
				ww = data["coinblocks"][i]["w"]
				hh = data["coinblocks"][i]["h"]
				self.sprites.append( CoinBlock(xx, yy, ww, hh))
	
	def update(self):
		for s in self.sprites:
			s.update()

			if(s.isMario() == False):
				s.collisionDetection(self.mario, s, self)
		
class View():
	def __init__(self, model):
		screen_size = (1000,600)
		self.screen = pygame.display.set_mode(screen_size,32)
		self.model = model

	def update(self):
		self.screen.fill([0,200,100])

		self.screen.blit(self.model.backgroundImage, (0 - (self.model.mario.x)/10,0))

		for s in self.model.sprites:
			if(s.isMario()):
 				self.screen.blit(self.model.mario.getImage(), (500, s.y))
			elif(s.isCoinBlock()):
				self.screen.blit(s.getImage(), (s.x -(self.model.mario.x - 500), s.y))
			else:
				self.screen.blit(s.image, (s.x -(self.model.mario.x - 500), s.y))
				
		pygame.display.flip()

class Controller():
	def __init__(self, model):
		self.model = model
		self.keep_going = True

	def update(self):
		for event in pygame.event.get():
			if event.type == QUIT:
				self.keep_going = False
			elif event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					self.keep_going = False
		keys = pygame.key.get_pressed()
		if keys[K_LEFT]:
			self.model.mario.locationPast()
			self.model.mario.x -= 10
			self.model.mario.imageCycle()
			self.model.mario.isFacingRight = False
		if keys[K_RIGHT]:
			self.model.mario.locationPast()
			self.model.mario.x += 10
			self.model.mario.imageCycle()
			self.model.mario.isFacingRight = True
		if keys[K_SPACE]:
			self.model.mario.jump()

print("Use the arrow keys to move. Press Esc to quit.")
pygame.init()
m = Model()
v = View(m)
c = Controller(m)
while c.keep_going:
	c.update()
	m.update()
	v.update()
	sleep(0.04)
print("Goodbye")