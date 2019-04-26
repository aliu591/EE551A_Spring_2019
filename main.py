import sys
import time
import random
import pygame
from config import *


class setGame(pygame.sprite.Sprite):
	def __init__(self, img_path, size, position, downlen):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load(img_path)
		self.image = pygame.transform.smoothscale(self.image, size)
		self.rect = self.image.get_rect()
		self.rect.left, self.rect.top = position
		self.downlen = downlen
		self.target_x = position[0]
		self.target_y = position[1] + downlen
		self.type = img_path.split('/')[-1].split('.')[0]
		self.fixed = False
		self.speed_x = 10
		self.speed_y = 10
		self.direction = 'down'

	def move(self):
		if self.direction == 'down':
			self.rect.top = min(self.target_y, self.rect.top+self.speed_y)
			if self.target_y == self.rect.top:
				self.fixed = True
		elif self.direction == 'up':
			self.rect.top = max(self.target_y, self.rect.top-self.speed_y)
			if self.target_y == self.rect.top:
				self.fixed = True
		elif self.direction == 'left':
			self.rect.left = max(self.target_x, self.rect.left-self.speed_x)
			if self.target_x == self.rect.left:
				self.fixed = True
		elif self.direction == 'right':
			self.rect.left = min(self.target_x, self.rect.left+self.speed_x)
			if self.target_x == self.rect.left:
				self.fixed = True

	def getPosition(self):
		return self.rect.left, self.rect.top

	def setPosition(self, position):
		self.rect.left, self.rect.top = position



class makeGame():
	def __init__(self, screen, font, gem_imgs):
		self.screen = screen
		self.font = font
		self.gem_imgs = gem_imgs
		self.reset()

	def start(self):
		clock = pygame.time.Clock()

		all_moving = True

		shape_moving = False

		gem_selected_xy = None
		gem_selected_xy2 = None
		swap_again = False
		add_score = 0
		add_score_showtimes = 10
		time_pre = int(time.time())

		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT or (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE):
					pygame.quit()
					sys.exit()
				elif event.type == pygame.MOUSEBUTTONUP:
					if (not all_moving) and (not shape_moving) and (not add_score):
						position = pygame.mouse.get_pos()
						if gem_selected_xy is None:
							gem_selected_xy = self.checkSelected(position)
						else:
							gem_selected_xy2 = self.checkSelected(position)
							if gem_selected_xy2:
								if self.swapGem(gem_selected_xy, gem_selected_xy2):
									shape_moving = True
									swap_again = False
								else:
									gem_selected_xy = None
			if all_moving:
				all_moving = not self.dropGems(0, 0)

				if not all_moving:
					res_match = self.isMatch()
					add_score = self.removeMatched(res_match)
					if add_score > 0:
						all_moving = True
			if shape_moving:
				gem1 = self.getGemByPos(*gem_selected_xy)
				gem2 = self.getGemByPos(*gem_selected_xy2)
				gem1.move()
				gem2.move()
				if gem1.fixed and gem2.fixed:
					res_match = self.isMatch()
					if res_match[0] == 0 and not swap_again:
						swap_again = True
						self.swapGem(gem_selected_xy, gem_selected_xy2)
					else:
						add_score = self.removeMatched(res_match)
						all_moving = True
						shape_moving = False
						gem_selected_xy = None
						gem_selected_xy2 = None
			self.screen.fill((135, 206, 235))
			self.drawGrids()
			self.gems_group.draw(self.screen)
			if gem_selected_xy:
				self.drawBlock(self.getGemByPos(*gem_selected_xy).rect)
			if add_score:
				self.drawAddScore(add_score)
				add_score_showtimes -= 1
				if add_score_showtimes < 1:
					add_score_showtimes = 10
					add_score = 0
			self.remaining_time -= (int(time.time()) - time_pre)
			time_pre = int(time.time())
			self.showRemainingTime()
			self.drawScore()
			if self.remaining_time <= 0:
				return self.score
			pygame.display.update()
			clock.tick(FPS)

	def reset(self):

		while True:
			self.all_gems = []
			self.gems_group = pygame.sprite.Group()
			for x in range(NUMGRID):
				self.all_gems.append([])
				for y in range(NUMGRID):
					gem = setGame(img_path=random.choice(self.gem_imgs), size=(GRIDSIZE, GRIDSIZE), position=[XMARGIN+x*GRIDSIZE, YMARGIN+y*GRIDSIZE-NUMGRID*GRIDSIZE], downlen=NUMGRID*GRIDSIZE)
					self.all_gems[x].append(gem)
					self.gems_group.add(gem)
			if self.isMatch()[0] == 0:
				break

		self.score = 0

		self.reward = 10

		self.remaining_time = 100

	def showRemainingTime(self):
		remaining_time_render = self.font.render('CountDown: %ss' % str(self.remaining_time), 1, (85, 65, 0))
		rect = remaining_time_render.get_rect()
		rect.left, rect.top = (WIDTH-201, 6)
		self.screen.blit(remaining_time_render, rect)

	def drawScore(self):
		score_render = self.font.render('SCORE:'+str(self.score), 1, (85, 65, 0))
		rect = score_render.get_rect()
		rect.left, rect.top = (10, 6)
		self.screen.blit(score_render, rect)

	def drawAddScore(self, add_score):
		score_render = self.font.render('+'+str(add_score), 1, (255, 100, 100))
		rect = score_render.get_rect()
		rect.left, rect.top = (250, 250)
		self.screen.blit(score_render, rect)

	def generateNewGems(self, res_match):
		if res_match[0] == 1:
			start = res_match[2]
			while start > -2:
				for each in [res_match[1], res_match[1]+1, res_match[1]+2]:
					gem = self.getGemByPos(*[each, start])
					if start == res_match[2]:
						self.gems_group.remove(gem)
						self.all_gems[each][start] = None
					elif start >= 0:
						gem.target_y += GRIDSIZE
						gem.fixed = False
						gem.direction = 'down'
						self.all_gems[each][start+1] = gem
					else:
						gem = setGame(img_path=random.choice(self.gem_imgs), size=(GRIDSIZE, GRIDSIZE), position=[XMARGIN+each*GRIDSIZE, YMARGIN-GRIDSIZE], downlen=GRIDSIZE)
						self.gems_group.add(gem)
						self.all_gems[each][start+1] = gem
				start -= 1
		elif res_match[0] == 2:
			start = res_match[2]
			while start > -4:
				if start == res_match[2]:
					for each in range(0, 3):
						gem = self.getGemByPos(*[res_match[1], start+each])
						self.gems_group.remove(gem)
						self.all_gems[res_match[1]][start+each] = None
				elif start >= 0:
					gem = self.getGemByPos(*[res_match[1], start])
					gem.target_y += GRIDSIZE * 3
					gem.fixed = False
					gem.direction = 'down'
					self.all_gems[res_match[1]][start+3] = gem
				else:
					gem = setGame(img_path=random.choice(self.gem_imgs), size=(GRIDSIZE, GRIDSIZE), position=[XMARGIN+res_match[1]*GRIDSIZE, YMARGIN+start*GRIDSIZE], downlen=GRIDSIZE*3)
					self.gems_group.add(gem)
					self.all_gems[res_match[1]][start+3] = gem
				start -= 1

	def removeMatched(self, res_match):
		if res_match[0] > 0:
			self.generateNewGems(res_match)
			self.score += self.reward
			return self.reward
		return 0

	def drawGrids(self):
		for x in range(NUMGRID):
			for y in range(NUMGRID):
				rect = pygame.Rect((XMARGIN+x*GRIDSIZE, YMARGIN+y*GRIDSIZE, GRIDSIZE, GRIDSIZE))
				self.drawBlock(rect, color=(0, 0, 255), size=1)

	def drawBlock(self, block, color=(255, 0, 255), size=4):
		pygame.draw.rect(self.screen, color, block, size)

	def dropGems(self, x, y):
		if not self.getGemByPos(x, y).fixed:
			self.getGemByPos(x, y).move()
		if x < NUMGRID-1:
			x += 1
			return self.dropGems(x, y)
		elif y < NUMGRID-1:
			x = 0
			y += 1
			return self.dropGems(x, y)
		else:
			return self.isFull()

	def isFull(self):
		for x in range(NUMGRID):
			for y in range(NUMGRID):
				if not self.getGemByPos(x, y).fixed:
					return False
		return True

	def checkSelected(self, position):
		for x in range(NUMGRID):
			for y in range(NUMGRID):
				if self.getGemByPos(x, y).rect.collidepoint(*position):
					return [x, y]
		return None

	def isMatch(self):
		for x in range(NUMGRID):
			for y in range(NUMGRID):
				if x + 2 < NUMGRID:
					if self.getGemByPos(x, y).type == self.getGemByPos(x+1, y).type == self.getGemByPos(x+2, y).type:
						return [1, x, y]
				if y + 2 < NUMGRID:
					if self.getGemByPos(x, y).type == self.getGemByPos(x, y+1).type == self.getGemByPos(x, y+2).type:
						return [2, x, y]
		return [0, x, y]

	def getGemByPos(self, x, y):
		return self.all_gems[x][y]

	def swapGem(self, gem1_pos, gem2_pos):
		margin = gem1_pos[0] - gem2_pos[0] + gem1_pos[1] - gem2_pos[1]
		if abs(margin) != 1:
			return False
		gem1 = self.getGemByPos(*gem1_pos)
		gem2 = self.getGemByPos(*gem2_pos)
		if gem1_pos[0] - gem2_pos[0] == 1:
			gem1.direction = 'left'
			gem2.direction = 'right'
		elif gem1_pos[0] - gem2_pos[0] == -1:
			gem2.direction = 'left'
			gem1.direction = 'right'
		elif gem1_pos[1] - gem2_pos[1] == 1:
			gem1.direction = 'up'
			gem2.direction = 'down'
		elif gem1_pos[1] - gem2_pos[1] == -1:
			gem2.direction = 'up'
			gem1.direction = 'down'
		gem1.target_x = gem2.rect.left
		gem1.target_y = gem2.rect.top
		gem1.fixed = False
		gem2.target_x = gem1.rect.left
		gem2.target_y = gem1.rect.top
		gem2.fixed = False
		self.all_gems[gem2_pos[0]][gem2_pos[1]] = gem1
		self.all_gems[gem1_pos[0]][gem1_pos[1]] = gem2
		return True
	'''info'''
	def __repr__(self):
		return self.info
