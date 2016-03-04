import time, pygame, sys, os, json
from pygame.locals import *
from screens import *
import react

mode = "menu"
game_level = -1
high_scores = [[0, "Olivier", "Athos",None,None],
				[0, "Rene", "Aramis",None,None],
				[0, "Isaac", "Porthos",None,None]]

gameengine = react.Game()
filename = "scores.json"
	
def save_scores():
	if os.access(filename, os.W_OK):
		os.rename(filename, filename + "." + str(time.time()))
	with open(filename, mode='w', encoding='utf-8') as f:
		json.dump(high_scores, f, indent=2)

def load_scores():
	global high_scores
	if os.access(filename, os.R_OK):
		print("open")
		with open(filename, 'r', encoding='utf-8') as f:
			high_scores = json.load(f)
	
def on_click():
	global game_level, mode
	click_pos = (pygame.mouse.get_pos() [0], pygame.mouse.get_pos() [1])
	
	if mode == "menu":
		button_width = SIZE[0]/3
		if click_pos[1] > SIZE[1]/3:
			game_level = int(click_pos[0]/button_width)
			mode = "initgame"
	elif mode == "postgame":
		mode = "menu"
		show_mainscreen()
		
def show_mainscreen():
	gameengine.start_idle()
	menu_screen(screen, high_scores)
		
		
def main():
	global mode
	load_scores()
	show_mainscreen()
	while True:
		if mode == "initgame":
			gameengine.stop_idle()
			game_screen(screen,60, 0, high_scores[game_level][0], True)
			if gameengine.ready_wait(30):
				pygame.mixer.music.load("Robot Wars Clean SFX- 3 2 1 Actvate!.mp3")
				pygame.mixer.music.play()
				while pygame.mixer.music.get_busy():
					time.sleep(0.1)

				elapsed = 61
				score = 0
				last_elapsed = -1
				last_score = -1
				pygame.mixer.music.load("mi.mp3")
				pygame.mixer.music.play()
				mode = "game"
				gameengine.start_game()
			else:
				mode = "menu"
				show_mainscreen()

		elif mode == "game":
			elapsed = int(round(60 - gameengine.elapsed_time(),0))
			score = gameengine.score
			if elapsed < 0:
				game_screen(screen,0, score, high_scores[game_level][0])
				pygame.mixer.music.load("airhorn.mp3")
				pygame.mixer.music.play()
				while pygame.mixer.music.get_busy():
					time.sleep(0.1)
				if score > high_scores[game_level][0]:
					ret = win_screen(screen)
					high_scores[game_level][0] = score
					high_scores[game_level][1] = ret[0]
					high_scores[game_level][2] = ret[1]
					high_scores[game_level][3] = ret[2]
					high_scores[game_level][4] = ret[3]
					save_scores()
					mode = "menu"
					show_mainscreen()
				else:
					lose_screen(screen)
					mode = "postgame"
				
			elif elapsed != last_elapsed or score != last_score:
				game_screen(screen,elapsed, score, high_scores[game_level][0])
				last_elapsed = elapsed
				last_score = score
			
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit() 
				sys.exit()
			if event.type == KEYDOWN:
				if event.key == K_F12:
					gameengine.stop_idle()
					gameengine.stop_game()
					pygame.quit()
					sys.exit() 
			if event.type == pygame.MOUSEBUTTONUP:
					pos = (pygame.mouse.get_pos() [0], pygame.mouse.get_pos() [1])
					#pygame.draw.circle(screen, white, pos, 2, 0) #for debugging purposes - adds a small dot where the screen is pressed
					on_click()					
try:
	pygame.init()
	screen = pygame.display.set_mode(SIZE)
	main()
except:
	pygame.quit()
	sys.exit()
