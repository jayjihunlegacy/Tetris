from Mail import *
from multiprocessing import Process, Manager
from Machine import *


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

	# 2. generate machines and tetrises.
	app = wx.App()
	machines = [EvolutionMachine(gene=None) for i in range(PROCESS_NUM)]	
	tetrises = [Tetris(mode='Train', inputMachine=machine,maxTick=1000) for machine in machines]
	

	manager = Manager()

	# prepare input/output communication dictionaries.
	fitness_dict = manager.dict()
	zeromachine_dict = manager.dict()
	offsprings_dict = manager.dict()
	genes_dict = manager.dict()
	dict_set = (fitness_dict, zeromachine_dict, genes_dict)
	
	# prepare locks.
	measure_locks = [manager.Lock() for i in range(PROCESS_NUM)]
	measure_res_locks = [manager.Lock() for i in range(PROCESS_NUM)]
	for lock in measure_locks:
		lock.acquire()
	for lock in measure_res_locks:
		lock.acquire()

	# Spawn processes.
	processes=[]
	for procnum in range(PROCESS_NUM):
		lock_set = (measure_locks[procnum], measure_res_locks[procnum])
		p = Process(
			target=measure_worker, 
			args=(machines[procnum], tetrises[procnum], procnum, dict_set,lock_set)
			)
		processes.append(p)
		p.start()

	generation = 0
	while generation != max_generation:
		generation+=1
				
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

		#1.5-1 divide genes and 		
		fitness_dict.clear()
		zeromachine_dict.clear()
		offsprings_dict.clear()		
		
		# Map the inputs.
		gene_pool = [genes[i:i+gene_per_process] for i in range(0,len(genes),gene_per_process)]		
		for i in range(PROCESS_NUM):
			genes_dict[i] = gene_pool[i]
		
		#=======print("Start measuring")=======

		# Let workers work!
		for lock in measure_locks:
			lock.release()
		
		# Wait until workers are done!
		for lock in measure_res_locks:
			lock.acquire()

		#=======print("End measuring")=======

		# Reduce the results.
		fitnesses = []
		isZeroMachine=[]
		for i in range(PROCESS_NUM):
			fitnesses+=fitness_dict[i]
			isZeroMachine+=zeromachine_dict[i]

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

class Trainer(object):
	pass

class EvolutionTrainer(Trainer):
	
	def __init__(self, pop_per_gen, sel_per_gen, max_generation=-1):
		self.PROCESS_NUM=4
		self.max_generation = max_generation
		self.population_per_generation = pop_per_gen
		self.selection_per_generation = sel_per_gen
		self.gene_per_process = self.population_per_generation // self.PROCESS_NUM
		self.selection_per_process = self.selection_per_population // self.PROCESS_NUM
		super().__init__(self)

	def get_firstpopulation(self, random):
		if random:
			# when initialize to random genes.
			return EvolutionMachine.generate_genes(population_per_generation)
		else:
			return None

	def train(self):
		print('Training start!')

		# 1. get first population.
		genes = self.get_firstpopulation(random=True)
		print('First population generated.')

		# 2. generate machines and tetrises.
		app = wx.App()
		machines = [EvolutionMachine(gene=None) for i in range(PROCESS_NUM)]	
		tetrises = [Tetris(mode='Train', inputMachine=machine,maxTick=1000) for machine in machines]



	def measure_worker(machine, tetris, procnum, dict_set, lock_set):	
		fitness_dict, zero_dict, gene_dict = dict_set
		lock,res_lock = lock_set

		generation=0
		# for each generation,
		while True:
			lock.acquire()
			generation+=1
			fitnesses = []
			isZeroMachine = []
			# for each genome,
			for idx, gene in enumerate(gene_dict[procnum]):
				# 1. Measure fitness.
				machine.gene = gene
				machine.name = 'Evo_G'+str(generation)+'_P'+str(procnum)+'_#'+str(idx+1)
				machine.instantiate()
				tetris.board.initBoard()
				score=tetris.start()
				fitnesses.append(score)

				# 2. Test if ZeroMachine.
				keyhistory=tetris.board.keys
				isZeroMachine.append(1 if len(keyhistory)==0 else 0)
			
			# collect data for each genome in generation.
			fitness_dict[procnum] = fitnesses
			zero_dict[procnum] = isZeroMachine

			#signal the main process that the job is done!
			res_lock.release()
		
	def breed_worker(success_genes, pop_per_gen, child_dict, procnum):
		parent_genes = EvolutionMachine.make_offsprings(success_genes,pop_per_gen)
		child_dict[procnum]=parent_genes