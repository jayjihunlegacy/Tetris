from TetrisCore import *
from Machine import *
from StartMenu import *

def main():
	app = wx.App()
	frame = MainMenuFrame(None)
	frame.Show()
	app.MainLoop()
	#human_play()
	#play_history('Evo_G11_P3_#42_1_2016-06-01_04-21-28-339701.sav')
	#play_machine()
	#train_machine()

if __name__=='__main__':
	main()
