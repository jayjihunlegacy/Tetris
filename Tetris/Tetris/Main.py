from TetrisCore import *

def play_history(filename):
	folder='C:/Tetris/'
	full = folder+filename
	app = wx.App()
	tetris = Tetris()
	tetris.initFrame('Save',full)
	app.MainLoop()

def human_play():
	app = wx.App()
	tetris = Tetris()
	tetris.initFrame('Human')
	app.MainLoop()

def main():
	#human_play()
	play_history('History_51_2016-05-22_18-55-49-753169.sav')

if __name__=='__main__':
	main()
