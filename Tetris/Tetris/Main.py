from TetrisCore import *
from Machine import *


def play_machine():
	app=wx.App()

	#this should be changed to loading 'specific machine'
	#machine = DeterministicMachine()
	machine = RandomMachine()

	tetris=Tetris()
	tetris.initFrame('Machine', inputMachine=machine)
	app.MainLoop()

def train_machine():
	app=wx.App()
	machine = EvolutionMachine()
	tetris = Tetris()
	tetris.initFrame('Train', inputMachine=machine)
	app.MainLoop()

def play_history(filename):
	folder='C:/Tetris/'
	full = folder+filename
	app = wx.App()
	tetris = Tetris()
	tetris.initFrame('Save',inputFile=full)
	app.MainLoop()

def human_play():
	app = wx.App()
	tetris = Tetris()
	tetris.initFrame('Human')
	app.MainLoop()

def main():
	#human_play()
	play_history('RandomMachine_0_2016-05-23_15-33-20-094546.sav')
	#play_machine()

if __name__=='__main__':
	main()
