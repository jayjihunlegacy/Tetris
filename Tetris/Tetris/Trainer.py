﻿from Mail import *
from multiprocessing import Process, Manager
from Machine import *
import time
import os
import os.path
import pickle
import numpy as np
from functools import reduce
class Trainer(object):
	def __init__(self):
		pass

	def train(self):
		pass

class EvolutionTrainer(Trainer):
	
	def __init__(self, pop_per_gen, sel_per_gen, max_generation=-1, use_migration=True):
		self.PROCESS_NUM=4
		self.max_generation = max_generation
		self.population_per_generation = pop_per_gen
		self.selection_per_generation = sel_per_gen
		self.gene_per_process = self.population_per_generation // self.PROCESS_NUM
		self.selection_per_process = self.selection_per_generation // self.PROCESS_NUM
		super().__init__()

		self.dict_set=None
		self.lock_set=None
		self.sendmail=False
		self.parenthub=r'D:\Dropbox\Tetris/'
		self.lasttime=None
		self.dotick=True
		self.use_migration=use_migration

	def get_firstpopulation(self):
		if not self.use_migration:
			# when initialize to random genes.
			result = EvolutionMachine.generate_genes(self.population_per_generation)			
			print('First population generated.')
			return result
		else:
			# when import things.
			filelist = os.listdir(self.parenthub)
			filenames = list(filter(lambda filename: filename.endswith('.model'),filelist))
			if len(filenames) == 0:
				print('No parents found.')
				exit(0)
			genes = []

			for filename in filenames:
				full = self.parenthub + filename
				with open(full, 'rb') as f:
					l=pickle.load(f)
				genes.append(l)

			genes = EvolutionMachine.make_offsprings(genes, self.population_per_generation)

			print('First population migrated.')
			return genes

	def tick(self):
		if not self.dotick:
			return
		if self.lasttime is None:
			self.lasttime = time.time()
		else:
			now = time.time()
			period = now-self.lasttime
			print('%.3fs passed.'%(period,))
			self.lasttime=now

	def train(self):
		print('Training start!')
		
		self.tick()

		# 1. get first population.
		genes = self.get_firstpopulation()
		

		# 2. generate machines and tetrises.
		app = wx.App()
		machines = [EvolutionMachine(gene=None) for i in range(self.PROCESS_NUM)]	
		tetrises = [Tetris(mode='Train', inputMachine=machine,maxTick=1000) for machine in machines]

		manager = Manager()

		# prepare input/output communication dictionaries.
		fitness_dict = manager.dict()
		zeromachine_dict = manager.dict()		
		genes_dict = manager.dict()
		offsprings_dict = manager.dict()
		parents_dict = manager.dict()
		self.dict_set = (fitness_dict, zeromachine_dict, genes_dict, offsprings_dict, parents_dict)
		
		m_locks = [manager.Lock() for i in range(self.PROCESS_NUM)]
		m_res_locks = [manager.Lock() for i in range(self.PROCESS_NUM)]
		b_locks = [manager.Lock() for i in range(self.PROCESS_NUM)]
		b_res_locks = [manager.Lock() for i in range(self.PROCESS_NUM)]

		for lock in m_locks:
			lock.acquire()
		for lock in m_res_locks:
			lock.acquire()
		for lock in b_locks:
			lock.acquire()
		for lock in b_res_locks:
			lock.acquire()

		# Spawn processes for measuring.
		processes=[]
		for procnum in range(self.PROCESS_NUM):
			lock_set = (m_locks[procnum], m_res_locks[procnum], b_locks[procnum], b_res_locks[procnum])
			p = Process(
				target=self.worker, 
				args=(procnum,machines[procnum], tetrises[procnum], lock_set)
				)
			processes.append(p)
			p.start()

		# for each generation, !!!!!!!!!!!!!!!!!!!
		generation = 0
		anyFound=False
		
		self.tick()

		while generation != self.max_generation:
			generation+=1	
			fitness_dict.clear()
			zeromachine_dict.clear()
			genes_dict.clear()
			offsprings_dict.clear()		
			parents_dict.clear()

			# 10-wise report.
			if generation%10 == 1:
				A_nums = [len(gene[0]) for gene in genes]
				B_nums = [len(gene[1]) for gene in genes]
				print('A-Complexities : (Min,Avg,Max) = (%i,%i,%i)'%(min(A_nums), sum(A_nums)//len(A_nums), max(A_nums)))
				print('B-Complexities : (Min,Avg,Max) = (%i,%i,%i)'%(min(B_nums), sum(B_nums)//len(B_nums), max(B_nums)))



			# Map the inputs.
			gene_pool = [genes[i:i+self.gene_per_process] for i in range(0,len(genes),self.gene_per_process)]		
			for i in range(self.PROCESS_NUM):
				genes_dict[i] = gene_pool[i]
		
			#=======print("Start measuring")=======

			# Let workers work!
			for lock in m_locks:
				lock.release()
		
			# Wait until workers are done!
			for lock in m_res_locks:
				lock.acquire()

			self.tick()

			#=======print("End measuring")=======

			# Reduce the results.
			fitnesses = []
			isZeroMachine=[]
			for i in range(self.PROCESS_NUM):
				fitnesses+=fitness_dict[i]
				isZeroMachine+=zeromachine_dict[i]

			#3. select some good genes
			ranks=sorted(range(len(fitnesses)), key=lambda i:fitnesses[i], reverse=True)
			indices = ranks[0:self.selection_per_generation]

			#3-1. if everybody failed, pick randomly...
			if max(fitnesses) == 0:
				# if enough number exist, kill all zero instances.
				if sum(isZeroMachine) < self.population_per_generation-self.selection_per_generation:
					for idx,iszero in enumerate(isZeroMachine):
						if iszero:
							genes[idx]=None
					genes = [gene for gene in genes if gene is not None]

				success_genes = random.sample(genes,self.selection_per_generation)
			#3-2. if somebody succeeded, pick them.
			else:
				if (not anyFound) and self.sendmail:
					subject = 'Genetic Algorithm Notification'
					body = 'Genome found.'
					sendEmail(subject,body)

				success_genes = [genes[index] for index in indices]
				anyFound=True
		
			print('Generation : %i. Best fitness : %i. Zero machines : %i'%(generation,max(fitnesses),sum(isZeroMachine)))
						
			# 4. Breed the successful genes.
			# Map the inputs.
			success_gene_pool = [success_genes[i:i+self.selection_per_process] for i in range(0,len(success_genes),self.selection_per_process)]
			for i in range(self.PROCESS_NUM):
				parents_dict[i]=success_gene_pool[i]
			
			#========print('Start breeding')=========
			for lock in b_locks:
				lock.release()

			for lock in b_res_locks:
				lock.acquire()

			self.tick()

			#========print('End breeding')============
			
			genes=[]
			for i in range(self.PROCESS_NUM):
				genes+=offsprings_dict[i]

		# End training.

		# join processes.
		for p in m_processes + b_processes:
			p.join()

	def worker(self, procnum, machine, tetris, lock_set):
		fitness_dict, zero_dict, gene_dict, offspring_dict, parents_dict = self.dict_set
		m_lock, m_res_lock, b_lock, b_res_lock = lock_set

		generation = 0
		while generation != self.max_generation:	
					
			#============1. Measuring===============
			#wait until main process signals.
			m_lock.acquire()

			generation+=1
			fitnesses=[]
			isZeroMachine=[]
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
			m_res_lock.release()
			#============Measuring done==================
			

			#============2. Breeding ====================
			#wait until main process signals.
			b_lock.acquire()

			success_genes = parents_dict[procnum]
			offspring_genes = EvolutionMachine.make_offsprings(success_genes,self.gene_per_process)
			offspring_dict[procnum]=offspring_genes

			# signal the main process that the job is done!
			b_res_lock.release()

class NeuralNetTrainer(Trainer):
	def __init__(self, num_of_hidden=100, size_of_batch=16, num_of_gen=-1):
		self.num_of_hidden=num_of_hidden
		self.size_of_batch =size_of_batch
		self.num_of_gen=num_of_gen
		super().__init__()

	def train(self):
		self.machine = NeuralNetMachine(
			num_of_hidden=self.num_of_hidden,
			gene=None
			)
		self.machine.instantiate(0.001)
		app = wx.App()
		tetris = Tetris(mode='Train', inputMachine=self.machine, maxTick=400)
		
		keycodes={wx.WXK_LEFT:0, wx.WXK_RIGHT:1, wx.WXK_UP:2, wx.WXK_DOWN:3, wx.WXK_SPACE:4}

		#tetris.start()
		generation=0
		while generation != self.num_of_gen:
			generation+=1
			batch=[]
			print('Generation #%i'%(generation,))
			for episode in range(self.size_of_batch):
				# 1. run the game.
				self.machine.refresh()
				score = tetris.start()

				# 2. collect output/input
				inputs=self.machine.inputs
				outputs=tetris.board.keys

				outputdict={}
				# 2-1. postprocess the keys.
				for data in outputs:
					tick, keycode=data
					key_num = keycodes[keycode]

					if tick not in outputdict.keys():
						outputdict[tick]=[0,0,0,0,0]

					outputdict[tick][key_num]=1

				# 2-2. collect pair.
				collected=[]
				for tick,input in inputs:
					if tick in outputdict.keys():
						output=outputdict[tick]
						pair=[input,output]
						collected.append(pair)
				
				# 3. determine rewards.
				if score>0:
					reward=score
					print('Score : ',score)
				else:
					if len(outputs)==0:
						reward=0
					else:
						reward=-1
					#if zero machine, reward = -1

				# 4. apply reward
				if reward==0:
					collected=[[input, [0.1,0.1,0.1,0.1,0.1]]for tick, input in inputs[0:10]]
				else:
					collected=[[input, [v*reward for v in output]] for input, output in collected]
				batch.append(collected)
			
			# if anything to back-propagate
			if len(batch)==0:
				continue
			else:
				pass
				#print('Back prop!')
			#
			# concatenate all history regardless of episode.
			batch = reduce(lambda x,y:x+y, batch)

			X_s = [data[0][0] for data in batch]
			Y_s = [data[1] for data in batch]

			train_x = np.array(X_s)
			train_y = np.array(Y_s)

			#print(train_x.shape)
			#print(train_y.shape)
			
			# do backprop
			self.machine.backprop(train_x, train_y)
		self.machine.save_weights()

			