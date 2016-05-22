#from TetrisCore import *
from NewTetrisCore import *


def main():
	app = wx.App()
	Tetris(None, title='Tetris')
	app.MainLoop()

if __name__=='__main__':
	main()
