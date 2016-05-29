import random as r
from TetrisCore import *
import copy
class Machine(object):
	def __init__(self, gene=None):
		self.gene = gene
		self.model = None
		self.instantiate()
		self.name = 'GeneralMachine'
		pass

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
		self.scenarios_set = list()
		pass

	#overriding.
	def instantiate(self):
		if self.gene is None:
			self.gene = (-4, -1)
			#if gene is None, randomly generate.
			pass
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
		if input[3].pieceShape == Tetrominoes.TShape and input[2]==Board.BoardHeight-1:
			return (0,0,0,1,0)

		if self.aimPosition is None:
			board = input[0]
			
			curCoord=input[1:3]
			curPiece = input[3]

			self.dummyboard.board=board
			self.dummyboard.curX=input[1]
			self.dummyboard.curY=input[2]
			self.dummyboard.curPiece=copy.deepcopy(input[3])
		
			# generate possible scenarios.
			scenarios = self.generate_scenarios()

			# digitize scenarios.
			scenarios = [Machine.digitize(scenario) for scenario in scenarios]

			# evaluate the scenarios and pick the best.
			scores=list()
			i=0
			scores = [self.evaluate_scenario(scenario) for scenario in scenarios]	
			self.scenarios_set.append([1 if (score==-float('inf')) else 0 for score in scores])
			
			#print(self.aims)
			max_scenario_index = scores.index(max(scores))
			
			# set aimPosition according the max_scenario.
			self.aimPosition = copy.deepcopy(self.aims[max_scenario_index])
			print("Aim Position Set!!:",self.aimPosition)
			#print("Scenario index : %i, score : "%(max_scenario_index,),scores[max_scenario_index])
			#print("Scenario :")

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
		return (0,0,0,0,0)

	def generate_scenarios(self):
		scenarios=list()
		for instruction in self.instructions:
			board=copy.deepcopy(self.dummyboard)
			results = list()
			for cmd in instruction:
				if cmd=='U':
					results.append(board.perform_valid_key('UP', isstr=True, verbose=False))
				elif cmd=='L':
					results.append(board.perform_valid_key('LEFT', isstr=True, verbose=False))
				elif cmd=='R':
					results.append(board.perform_valid_key('RIGHT', isstr=True, verbose=False))
				else:
					print('INVALID cmd :',cmd)
				
			ispossible = all(results)
			if not ispossible:
				scenarios.append(None)
			else:
				board.dropDown()
				result = copy.deepcopy(board.board)
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
	pass

class NeuralNetMachine(Machine):
	pass