import wx
from TetrisCore import *
from Machine import *
from multiprocessing import Process, Manager
from Mail import *
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

def measure_worker(machine, tetris, genes, generation, procnum, fitness_dict, zero_dict):
	fitnesses = []
	isZeroMachine = []

	for idx, gene in enumerate(genes):
		machine.gene = gene
		machine.name = 'Evo_G'+str(generation)+'_P'+str(procnum)+'_#'+str(idx+1)
		machine.instantiate()
		tetris.board.initBoard()
		score=tetris.start()
		keyhistory=tetris.board.keys
		isZeroMachine.append(1 if len(keyhistory)==0 else 0)
		fitnesses.append(score)
	fitness_dict[procnum] = fitnesses
	zero_dict[procnum] = isZeroMachine

def breed_worker(success_genes, pop_per_gen, child_dict, procnum):
	parent_genes = EvolutionMachine.make_offsprings(success_genes,pop_per_gen)
	child_dict[procnum]=parent_genes

def evolution_train():
	max_generation = -1
	population_per_generation = 256
	selection_per_population = 64
	anyFound=False
	PROCESS_NUM=4
	gene_per_process = population_per_generation // PROCESS_NUM
	selection_per_process = selection_per_population // PROCESS_NUM
	
	#machines = list()
	
	#1. generate initial population
	genes = EvolutionMachine.generate_genes(population_per_generation)
	print("1. First population generated.")
	#machine = EvolutionMachine(gene=None)
	machines = [EvolutionMachine(gene=None) for i in range(PROCESS_NUM)]
	app = wx.App()
	#tetris = Tetris(mode='Train',inputMachine=machine,maxTick=1000)
	tetrises = [Tetris(mode='Train', inputMachine=machine,maxTick=1000) for machine in machines]
	generation = 0
	manager = Manager()
	fitness_dict = manager.dict()
	zeromachine_dict = manager.dict()
	offsprings_dict = manager.dict()
	while generation != max_generation:
		generation+=1

		#1.5-1 divide genes and 
		fitnesses = []
		isZeroMachine=[]
		fitness_dict.clear()
		zeromachine_dict.clear()
		offsprings_dict.clear()
		
		#print("Start measuring")
		processes=[]
		gene_pool = [genes[i:i+gene_per_process] for i in range(0,len(genes),gene_per_process)]
		for i in range(PROCESS_NUM):
			p = Process(target=measure_worker, args=(machines[i], tetrises[i], gene_pool[i], generation, i, fitness_dict, zeromachine_dict))
			processes.append(p)

		for p in processes:
			p.start()

		for p in processes:
			p.join()
		
		for i in range(PROCESS_NUM):
			fitnesses+=fitness_dict[i]
			isZeroMachine+=zeromachine_dict[i]
		#print("End measuring")
		
		# code with single processor.
		'''
		fitnesses = []
		isZeroMachine = []
		#2. measure fitnesses
		print('Start measuring')
		for idx, gene in enumerate(genes):
			machine.gene = gene
			machine.name = 'Evo_G'+str(generation)+'_#'+str(idx+1)		
			machine.instantiate()
			tetris.board.initBoard()
			score = tetris.start()
			keyhistory = tetris.board.keys
			isZeroMachine.append(1 if len(keyhistory)==0 else 0)
			fitnesses.append(score)
		print('End measuring')
		'''


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


		#print('Start breeding')
		processes=[]
		success_gene_pool = [success_genes[i:i+selection_per_process] for i in range(0,len(success_genes),selection_per_process)]
		for i in range(PROCESS_NUM):
			p = Process(target=breed_worker, args=(success_gene_pool[i], gene_per_process, offsprings_dict, i))
			processes.append(p)
			
		for p in processes:
			p.start()
			
		for p in processes:
			p.join()
			
		genes=[]
		for i in range(PROCESS_NUM):
			genes+=offsprings_dict[i]
			   
		#print('End breeding')


		'''
		#4. make offsprings
		genes = EvolutionMachine.make_offsprings(success_genes, population_per_generation)
		'''

def main():
	#human_play()
	play_history('Evo_G11_P3_#42_1_2016-06-01_04-21-28-339701.sav')
	#play_machine()
	#train_machine()
	#evolution_train()

if __name__=='__main__':
	main()
