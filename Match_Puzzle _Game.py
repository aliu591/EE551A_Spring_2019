import os
import pygame
from utils import *
from config import *


def main():
	pygame.init()
	screen = pygame.display.set_mode((WIDTH, HEIGHT))

	font = pygame.font.Font(os.path.join(ROOTDIR, 'resources/font.TTF'), 25)

	gem_imgs = []
	for i in range(1, 8):
		gem_imgs.append(os.path.join(ROOTDIR, 'resources/images/gem%s.png' % i))

	game = makeGame(screen, font, gem_imgs)
	while True:
		score = game.start()
		flag = False
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT or (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE):
					pygame.quit()
					sys.exit()
				elif event.type == pygame.KEYUP and event.key == pygame.K_r:
					flag = True
			if flag:
				break
			screen.fill((135, 206, 235))
			text0 = 'Final score: %s' % score
			text1 = 'Use <R> to restart the game.'
			text2 = 'Use <Esc> to quit the game.'
			y = 150
			for idx, text in enumerate([text0, text1, text2]):
				text_render = font.render(text, 1, (85, 65, 0))
				rect = text_render.get_rect()
				if idx == 0:
					rect.left, rect.top = (212, y)
				elif idx == 1:
					rect.left, rect.top = (122.5, y)
				else:
					rect.left, rect.top = (126.5, y)
				y += 100
				screen.blit(text_render, rect)
			pygame.display.update()
		game.reset()


if __name__ == '__main__':
	main()