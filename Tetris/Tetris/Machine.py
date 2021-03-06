﻿import random as r
from TetrisCore import *
import os
os.environ['THEANO_FLAGS']='floatX=float32,device=cpu'
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation
from keras.utils import np_utils
from keras.layers.advanced_activations import LeakyReLU
from keras.optimizers import SGD
import numpy


class Machine(object):
	def __init__(self, gene=None):
		self.gene = gene
		self.model = None
		self.name = 'GeneralMachine'
		self.instantiate()

	#for overriding.
	def instantiate(self):
		#instantiate gene into some model.
		pass

	#for overriding.
	def feedForward(self, input, tick):
		output = None
		#output must be in form (LEFT, RIGHT, DOWN, UP, SPACE)
		return output

	def digitize(input):
		if input is None:
			return None
		output = []
		for j in range(Board.BoardHeight):
			lis=[]
			for i in range(Board.BoardWidth):
				if input[j][i]!=0:
					lis+=[1]
				else:
					lis+=[0]
			output.append(lis)
		return output


class RandomMachine(Machine):
	def __init__(self, cool_time=10):
		super().__init__()
		self.name='RandomMachine'
		self.TICK_COOLTIME = cool_time
		r.seed(11557)

	#overriding.
	def instantiate(self):
		pass

	#overriding.
	def feedForward(self, input, tick):
		#output must be in form (LEFT, RIGHT, UP, DOWN, SPACE)

		if tick%self.TICK_COOLTIME == 0:
			output = tuple()
			for i in range(5):
				output+=(r.getrandbits(1),)
			return output
		else:
			return (0,0,0,0,0)


class DeterministicMachine(Machine):
	def __init__(self, cool_time=1, gene=None):
		super().__init__(gene=gene)
		self.name='DeterministicMachine'
		self.TICK_COOLTIME = cool_time
		self.aimPosition = None
		self.dummyboard=Board(None, dummy=True)

	#overriding.
	def instantiate(self):
		#if gene is None, randomly generate.
		if self.gene is None:
			self.gene = (-4, -1)
		#1. number of holes.
		#2. height penalty sum.

		self.w = list(self.gene)

		self.aims=list()
		for rotate in range(4):
			self.aims.append([0,rotate])
			for left in range(1,7):
				self.aims.append([left,rotate])
			for right in range(1,4):
				self.aims.append([-right,rotate])

		self.instructions=list()
		for aim in self.aims:
			inst=list()
			#if rotate
			if aim[1]:
				inst+=['U' for i in range(aim[1])]

			if aim[0]>0:
				inst+=['L' for i in range(aim[0])]
			else:
				inst+=['R' for i in range(-aim[0])]
			self.instructions.append(inst)

	#overriding.
	def feedForward(self, input, tick):
		'''
		if have aimPosition, try to move to that aimPosition.
		if not have, make aimPosition, and try.
		'''
		#output must be in form (LEFT, RIGHT, UP, DOWN, SPACE)

		#input = (board, curX, curY, pieces)
		if input[3][0].pieceShape == Tetrominoes.TShape and input[2]==Board.BoardHeight-1:
			return (0,0,0,1,0)

		if self.aimPosition is None:
			self.dummyboard.origboard = input[0]
			self.dummyboard.origX = input[1]
			self.dummyboard.origY = input[2]
			self.dummyboard.origpieces = tuple()
			self.dummyboard.origpieces += (input[3][0].shape(),)
			self.dummyboard.origpieces += (input[3][1].shape(),)
			self.dummyboard.origpieces += (input[3][2].shape(),)
			self.dummyboard.origpieces += (input[3][3].shape(),)
			self.dummyboard.origpieces += (input[3][4].shape(),)
			self.dummyboard.origpieces += (input[3][5].shape(),)
		
			# generate possible scenarios.
			scenarios = self.generate_scenarios()

			# digitize scenarios.
			#scenarios = [Machine.digitize(scenario) for scenario in scenarios]

			# evaluate the scenarios and pick the best.
			scores = [self.evaluate_scenario(scenario) for scenario in scenarios]	
			
			max_scenario_index = scores.index(max(scores))
			
			# set aimPosition according the max_scenario.
			self.aimPosition = [self.aims[max_scenario_index][0], self.aims[max_scenario_index][1]]
			print("Aim Position Set!!:",self.aimPosition)

		if tick % self.TICK_COOLTIME == 0:
			# try to move to that aimPosition.
			# if have to rotate
			if self.aimPosition[1]:
				self.aimPosition[1]-=1
				return (0,0,1,0,0)
			# if have to go left:
			if self.aimPosition[0] > 0:
				self.aimPosition[0]-=1
				return (1,0,0,0,0)
			#if have to go right:
			if self.aimPosition[0] < 0:
				self.aimPosition[0]+=1
				return (0,1,0,0,0)
			# nothing to do any more.
			self.aimPosition = None
			return (0,0,0,0,1)
		else:
			return (0,0,0,0,0)

	def reset_dummyboard(self):
		for i in range(Board.BoardHeight):
			for j in range(Board.BoardWidth):
				self.dummyboard.board[i][j] = self.dummyboard.origboard[i][j]
		self.dummyboard.curX = self.dummyboard.origX
		self.dummyboard.curY = self.dummyboard.origY
		self.dummyboard.curPiece.setShape(self.dummyboard.origpieces[0])
		self.dummyboard.nextPiece.setShape(self.dummyboard.origpieces[1])
		self.dummyboard.next2Piece.setShape(self.dummyboard.origpieces[2])
		self.dummyboard.next3Piece.setShape(self.dummyboard.origpieces[3])
		self.dummyboard.next4Piece.setShape(self.dummyboard.origpieces[4])
		self.dummyboard.next5Piece.setShape(self.dummyboard.origpieces[5])

	def generate_scenarios(self):
		scenarios=list()
		for instruction in self.instructions:
			self.reset_dummyboard()
			results = list()
			for cmd in instruction:
				if cmd=='U':
					results.append(self.dummyboard.perform_valid_key('UP', isstr=True, verbose=False))
				elif cmd=='L':
					results.append(self.dummyboard.perform_valid_key('LEFT', isstr=True, verbose=False))
				elif cmd=='R':
					results.append(self.dummyboard.perform_valid_key('RIGHT', isstr=True, verbose=False))
				else:
					print('INVALID cmd :',cmd)
				
			ispossible = all(results)
			if not ispossible:
				scenarios.append(None)
			else:
				self.dummyboard.dropDown()
				result=list()
				for i in range(Board.BoardHeight):
					row = list()
					for j in range(Board.BoardWidth):
						row.append(1 if self.dummyboard.board[i][j] else 0)
					result.append(row)
				scenarios.append(result)
		return scenarios

	def evaluate_scenario(self,scenario):
		if scenario is None:
			return -float('inf')
		
		x_vector=list()
		#1. number of holes.
		hole_num=0
		for i in range(Board.BoardWidth):
			upperExist=False
			for j in reversed(range(Board.BoardHeight)):
				if scenario[j][i]:
					upperExist=True
				if (not scenario[j][i]) and upperExist:
					hole_num+=1

		x_vector.append(hole_num)

		#2. penalty sum.
		penalty_sum=0
		for height in range(Board.BoardHeight):
			penalty_sum+=sum(scenario[height]) * (height+1)
		x_vector.append(penalty_sum)


		# get dot product
		dot_product=0
		for i in range(len(x_vector)):
			dot_product += x_vector[i] * self.w[i]
		
		return dot_product

class EvolutionMachine(Machine):
	INPUT_NEURON_NUM = 81
	HIDDEN_NEURON_NUM = 40
	OUTPUT_NEURON_NUM = 5

	LEVEL_A_MIN_SYNAPSE = 200
	LEVEL_A_MAX_SYNAPSE = 3000
	LEVEL_B_MIN_SYNAPSE = 20
	LEVEL_B_MAX_SYNAPSE = 180

	LEVEL_A_MAX_CHANGE = 20
	LEVEL_B_MAX_CHANGE = 10

	def __init__(self, gene, cool_time=1,name='EvolutionMachine'):
		super().__init__(gene=gene)
		self.name=name
		self.TICK_COOLTIME = cool_time

	#overriding.
	def instantiate(self):
		#real instantiation using self.gene
		self.model = self.gene
		
	#overriding.
	def feedForward(self, input, tick):
		
		board,curX,curY,pieces = input
		refined_board = EvolutionMachine.refine_board(board,curX,curY,pieces[0])
		#flattened board with length of 81.
		flattened_board = [item for sublist in refined_board for item in sublist]
		flattened_board+=[1]

		#hidden neurons with length of 40.
		hidden_neurons = [0 for i in range(EvolutionMachine.HIDDEN_NEURON_NUM)]

		#output neurons with length of 5.
		output_neurons = [0 for i in range(EvolutionMachine.OUTPUT_NEURON_NUM)]
		
		# two list of tuples.
		A_synapses, B_synapses = self.model

		# first level feed forward.
		for a_synapse in A_synapses:
			start, end, weight = a_synapse
			if flattened_board[start]:
				hidden_neurons[end] += weight

		# second level feed forward.
		for b_synapse in B_synapses:
			start, end, weight = b_synapse
			if hidden_neurons[start]>0:
				output_neurons[end] += hidden_neurons[start] * weight

		output = tuple([1 if neuron>0 else 0 for neuron in output_neurons])
		#print('Feed forward :',self.name,' ',output,' ',tick)
		return output
		#output must be in form (LEFT, RIGHT, DOWN, UP, SPACE)

	@staticmethod
	def refine_board(board,curX,curY,curPiece):
		# 1. Take only 4 top lines of the board.
		top_line = 0
		for i in reversed(range(Board.BoardHeight,3)):
			line = board[i]
			is_any_block = any(line)
			if is_any_block:
				top_line=i-3
				break

		refined_board=board[top_line:top_line+4]

		# 2. Render current piece.
		table = list()
		for i in range(4):
			table.append([0,0,0,0,0,0,0,0,0,0])
		minY = curPiece.minY()
		for coord in curPiece.coords:
			relX,relY = coord
			Y = relY-minY
			X = relX+curX
			table[Y][X] = 1
		return refined_board+table


	def generate_genes(pop_per_gen):
		result = []

		for i in range(pop_per_gen):
			#1. randomly generate A_level synapses
			num_of_syn = r.randint(500,700)
			gene_a=[]
			A_syn_dict =dict()
			while len(gene_a) != num_of_syn:
				start = r.randint(0,EvolutionMachine.INPUT_NEURON_NUM-1)
				end = r.randint(0,EvolutionMachine.HIDDEN_NEURON_NUM-1)
				weight = 1 if r.getrandbits(1) else -1
				synapse = (start,end,weight)
				if synapse[:-1] in A_syn_dict.keys():
					continue
				gene_a.append(synapse)
				A_syn_dict[synapse[:-1]]=1

			#2. randomly generate B_level synapses
			num_of_syn = r.randint(40,80)
			gene_b=[]
			B_syn_dict = dict()
			while len(gene_b) != num_of_syn:
				start = r.randint(0,EvolutionMachine.HIDDEN_NEURON_NUM-1)
				end = r.randint(0,EvolutionMachine.OUTPUT_NEURON_NUM-1)
				weight = 1 if r.getrandbits(1) else -1
				synapse = (start,end,weight)
				if synapse[:-1] in B_syn_dict.keys():
					continue
				gene_b.append(synapse)
				B_syn_dict[synapse[:-1]]=1

			newgene=(gene_a,gene_b)
			result.append(newgene)
		return result

	def make_offsprings(parent_genes, pop_per_gen):
		
		num_of_parents = len(parent_genes)
		while len(parent_genes) != pop_per_gen:
			mother = r.choice(parent_genes[0:num_of_parents])
			father = r.choice(parent_genes[0:num_of_parents])

			A_syn_m, B_syn_m = mother
			A_syn_f, B_syn_f = father
			
			#1. average A_level synapses
			smaller = min(len(A_syn_m), len(A_syn_f))
			bigger = max(len(A_syn_m), len(A_syn_f))
			num_of_A = r.randint(smaller,bigger)
			A_syn_pool = A_syn_m+A_syn_f
			gene_a = r.sample(A_syn_pool,num_of_A)

			#2. average B_level synapses
			smaller = min(len(B_syn_m), len(B_syn_f))
			bigger = max(len(B_syn_m), len(B_syn_f))
			num_of_B = r.randint(smaller,bigger)	
			B_syn_pool = B_syn_m+B_syn_f
			gene_b = r.sample(B_syn_pool,num_of_B)

			A_syn_dict = dict()
			B_syn_dict = dict()
			for A_syn in gene_a:
				A_syn_dict[A_syn[:-1]]=1
			for B_syn in gene_b:
				B_syn_dict[B_syn[:-1]]=1
			#3. make mutation on A.
			# delete [0,4] weights in A_level and insert another [0,4] weights.
			if len(gene_a) < EvolutionMachine.LEVEL_A_MIN_SYNAPSE:
				delete_a_num = 0
			else :
				delete_a_num = r.randint(0,EvolutionMachine.LEVEL_A_MAX_CHANGE)
			for i in range(delete_a_num):
				gene_a.remove(r.choice(gene_a))

			if len(gene_a) > EvolutionMachine.LEVEL_A_MAX_SYNAPSE:
				insert_a_num = 0
			else:
				insert_a_num = r.randint(0,EvolutionMachine.LEVEL_A_MAX_CHANGE)

			target_a_num = len(gene_a) + insert_a_num

			while len(gene_a) != target_a_num:
				start = r.randint(0,EvolutionMachine.INPUT_NEURON_NUM-1)
				end = r.randint(0,EvolutionMachine.HIDDEN_NEURON_NUM-1)
				weight = 1 if r.getrandbits(1) else -1
				synapse = (start,end,weight)

				if synapse[:-1] in A_syn_dict.keys():
					continue
				gene_a.append(synapse)
				A_syn_dict[synapse[:-1]]=1

			# delete [0,2] weights in B_level and insert another [0,2] weights.
			if len(gene_b) < EvolutionMachine.LEVEL_B_MIN_SYNAPSE:
				delete_b_num=0
			else:
				delete_b_num = r.randint(0,EvolutionMachine.LEVEL_B_MAX_CHANGE)
			for i in range(delete_b_num):
				gene_b.remove(r.choice(gene_b))

			if len(gene_b) > EvolutionMachine.LEVEL_B_MAX_SYNAPSE:
				insert_b_num = 0
			else:
				insert_b_num = r.randint(0,EvolutionMachine.LEVEL_B_MAX_CHANGE)

			target_b_num = len(gene_b) + insert_b_num

			while len(gene_b) != target_b_num:
				start = r.randint(0,EvolutionMachine.HIDDEN_NEURON_NUM-1)
				end = r.randint(0,EvolutionMachine.OUTPUT_NEURON_NUM-1)
				weight = 1 if r.getrandbits(1) else -1
				synapse = (start,end,weight)

				if synapse[:-1] in B_syn_dict.keys():
					continue
				gene_b.append(synapse)
				B_syn_dict[synapse[:-1]]=1

			parent_genes.append((gene_a,gene_b))

		return parent_genes


class NeuralNetMachine(Machine):
	def __init__(self, num_of_hidden, gene, cool_time=1, name='NNMachine'):
		self.num_of_hidden = num_of_hidden		
		self.name=name
		self.TICK_COOLTIME = cool_time
		self.weight_filename='neural.weight'

		super().__init__(gene=gene)

	def instantiate(self, learning_rate=0.01):
		self.learning_rate=learning_rate
		self.build_model()
		if self.gene is not None:
			self.load_weights()
		self.compile_model()
		self.refresh()

	def refresh(self):
		self.inputs=[]

	def build_model(self):
		n_input = 220
		n_hidden = self.num_of_hidden
		n_output = 5

		self.model = Sequential()
		self.model.add(Dense(output_dim=n_hidden, input_dim=n_input))
		self.model.add(LeakyReLU(0.1))
		self.model.add(Dense(output_dim=n_output))
		self.model.add(Activation('sigmoid'))

	def load_weights(self):
		try:
			self.model.load_weights(self.weight_filename)
			print('Weight imported.')
		except:
			print('No weight file found. Initialized randomly.')

	def save_weights(self):
		self.model.save_weights(self.weight_filename,overwrite=True)
		print('weight saved.')

	def compile_model(self):
		sgd=SGD(lr=self.learning_rate)
		self.model.compile(loss='binary_crossentropy',
					 optimizer=sgd,
					 metrics=[]
					 )

	def feedForward(self, input, tick):
		# if cooltime not passed
		if tick%self.TICK_COOLTIME:
			return (0,0,0,0,0)

		# feed forward the neural network.
		board,curX,curY,pieces=input
		refined_board = NeuralNetMachine.refine_board(board,curX,curY,pieces[0])	
		input = numpy.array([refined_board])
		result=self.model.predict(input,batch_size=1)
		result=result[0]

		# save the input.
		self.inputs.append((tick,input))
		
		output = tuple([1 if value>0.5 else 0 for value in result])
		#print("FeedForward :", tick, ' ',output)
		return output

	def refine_board(board, curX, curY, curPiece):
		# deepcopy the board.
		refined_board=[]
		for i in range(Board.BoardHeight):
			for j in range(Board.BoardWidth):
				if board[i][j]:
					refined_board+=[1]
				else:
					refined_board+=[0]

		minY = curPiece.minY()
		for coord in curPiece.coords:
			relX,relY = coord
			Y = curY-relY
			X = curX+relX
			refined_board[Y*Board.BoardWidth + X] = -1
		return refined_board

	def backprop(self,train_x, train_y):
		self.model.fit(train_x, train_y,nb_epoch=1, batch_size=10,verbose=0)