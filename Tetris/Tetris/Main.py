#from TetrisCore import *
from NewTetrisCore import *

def play_history(filename):
	folder='C:/Tetris/'
	full = folder+filename
	app = wx.App()
	Tetris(
		inputDevice=Board.INPUT_SAVE,
		inputFile=full
		)
	app.MainLoop()

def human_play():
	app = wx.App()
	Tetris()
	app.MainLoop()

def main():
	#human_play()
	play_history('History_13_2016-05-22_17-29-47-653743.sav')

if __name__=='__main__':
	main()
