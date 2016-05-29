from TetrisCore import *
from Machine import *


def play_machine():
	app=wx.App()

	# this should be changed to loading 'specific machine'
	machine = DeterministicMachine()
	#machine = RandomMachine()

	tetris=Tetris()
	tetris.initFrame('Machine', inputMachine=machine)
	app.MainLoop()

def train_machine():
	app=wx.App()
	machine = DeterministicMachine()
	tetris = Tetris()
	score = tetris.initFrame('Train', inputMachine=machine, maxTick=1000)
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

def evolution_train():
	max_generation = 10
	population_per_generation = 16
	selection_per_population = 4

	app = wx.App()
	machines = list()

	#1. generate adam and eve.
	#2. 

	#1. generate initial population
	genes = EvolutionMachine.generate_genes(population_per_generation)

	for generation in range(1,max_generation+1):
		fitnesses = []
		machines = []
		#2. measure fitnesses
		for gene in genes:
			machine = EvolutionMachine(gene)
			tetris = Tetris()
			score = tetris.initFrame('Train', inputMachine = machine, maxTick = 1000)
			fitnesses.append(score)

		#3. select some good genes
		ranks=sorted(range(len(fitnesses)), key=lambda i:fitnesses[i], reverse=True)
		indices = ranks[0:selection_per_population]

		success_genes = [genes[index] for index in indices]
		
		print('Generation : %i. Best fitness : %i'%(generation,max(fitnesses)))

		#4. make offsprings
		genes = EvolutionMachine.make_offsprings(success_genes, population_per_generation)


def main():
	#human_play()
	#play_history('DeterministicMachine_92_2016-05-29_15-11-08-830112.sav')
	#play_machine()
	#train_machine()
	evolution_train()

if __name__=='__main__':
	main()
