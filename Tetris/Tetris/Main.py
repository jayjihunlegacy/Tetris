import wx
from TetrisCore import *
from Machine import *
from Trainer import *

def play_machine():
	app=wx.App()

	# this should be changed to loading 'specific machine'
	machine = DeterministicMachine()
	tetris=Tetris(mode='Machine', inputMachine = machine)
	tetris.start()
	app.MainLoop()

def train_machine():
	app=wx.App()
	machine = DeterministicMachine()
	tetris = Tetris(mode='Train', inputMachine=machine, maxTick=1000)
	score = tetris.start()
	app.MainLoop()


def play_history(filename):
	folder='D:/Dropbox/Tetris/'
	if filename[1]==':':
		full=filename
	else:
		full = folder+filename
	app = wx.App()
	tetris = Tetris(mode='Save',inputFile=full)
	tetris.start()
	app.MainLoop()

def human_play():
	app = wx.App()
	tetris = Tetris(mode='Human')
	tetris.start()
	app.MainLoop()

def evolution_train():
	trainer = EvolutionTrainer(
		pop_per_gen=256,
		sel_per_gen=64,
		max_generation=-1
		)
	trainer.train()

def neural_train():
	trainer = NeuralNetTrainer(
		num_of_hidden=100
		)
	trainer.train()

def main():
	#human_play()
	#play_history('Evo_G2_P1_#11_1_2016-06-02_12-34-39-500409.sav')
	#play_machine()
	#train_machine()
	#evolution_train()
	neural_train()

if __name__=='__main__':
	main()
