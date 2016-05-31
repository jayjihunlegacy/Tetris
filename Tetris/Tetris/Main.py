import wx
from TetrisCore import *
from Machine import *

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
	folder='E:/Tetris/'
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
	max_generation = -1
	population_per_generation = 128
	selection_per_population = 64
	anyFound=False
	
	#machines = list()
	
	#1. generate initial population
	genes = EvolutionMachine.generate_genes(population_per_generation)
	print("1. First population generated.")
	machine = EvolutionMachine(gene=None)
	app = wx.App()
	tetris = Tetris(mode='Train',inputMachine=machine,maxTick=1000)
	generation = 0

	while generation != max_generation:
		generation+=1
		fitnesses = []
		isZeroMachine = []
		#2. measure fitnesses
		for idx, gene in enumerate(genes):
			machine.gene = gene
			machine.name = 'Evo_G'+str(generation)+'_#'+str(idx+1)		
			machine.instantiate()
			tetris.board.initBoard()
			score = tetris.start()
			keyhistory = tetris.board.keys
			isZeroMachine.append(1 if len(keyhistory)==0 else 0)
			fitnesses.append(score)

		#3. select some good genes
		ranks=sorted(range(len(fitnesses)), key=lambda i:fitnesses[i], reverse=True)
		indices = ranks[0:selection_per_population]

		#3-1. if everybody failed, pick randomly...
		if max(fitnesses) == 0:
			# if enough number exist, kill all zero instances.
			if sum(isZeroMachine) < population_per_generation-selection_per_population:
				for idx,iszero in enumerate(isZeroMachine):
					if iszero:
						genes[idx]=None
				genes = [gene for gene in genes if gene is not None]

			success_genes = random.sample(genes,selection_per_population)
		#3-2. if somebody succeeded, pick them.
		else:
			if not anyFound:
				subject = 'Genetic Algorithm Notification'
				body = 'Genome found.\n'
				sendEmail(subject,body)

			success_genes = [genes[index] for index in indices]
			anyFound=True
		
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
