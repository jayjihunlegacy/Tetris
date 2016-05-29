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
	folder='E:/Tetris/'
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
	max_generation = 100
	population_per_generation = 64
	selection_per_population = 16

	
	#machines = list()
	
	#1. generate initial population
	genes = EvolutionMachine.generate_genes(population_per_generation)
	app = wx.App()
	tetris = Tetris()
	for generation in range(1,max_generation+1):
		fitnesses = []
		machines = []
		#2. measure fitnesses
		for idx, gene in enumerate(genes):
			name = 'Evo_G'+str(generation)+'_#'+str(idx+1)
			
			machine = EvolutionMachine(gene,name=name)
			
			
			score = tetris.initFrame('Train',name=name, inputMachine = machine, maxTick = 1000)
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
	#play_history('Evo_G53_#19_0_2016-05-30_01-01-34-770212.sav')
	#play_machine()
	#train_machine()
	evolution_train()

if __name__=='__main__':
	main()
