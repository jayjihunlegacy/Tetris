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
		pass

	#overriding.
	def instantiate(self):
		if self.gene is None:
			self.gene = (-1, -2)
			#if gene is None, randomly generate.
			pass
		#1. number of holes.
		#2. height penalty sum.

		self.w = list(self.gene)

		self.aims=list()
		self.aims.append([0,0])
		for rotate in range(4):
			for left in range(1,7):
				self.aims.append([left,rotate])
			for right in range(1,7):
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
			'''
			for scenario in scenarios:
				print(i, self.aims[i])
				score = self.evaluate_scenario(scenario)
				print('Evaluate scenario :')
				if scenario is not None:
					for line in range(3):
						line = 3-line-1
						print(scenario[line])
				else:
					print(None)
				print('Score :',score)
				scores.append(score)
				i+=1
			'''
			scores = [self.evaluate_scenario(scenario) for scenario in scenarios]	
			print(scores)
			print(self.aims)
			max_scenario_index = scores.index(max(scores))
			
			# set aimPosition according the max_scenario.
			self.aimPosition = copy.deepcopy(self.aims[max_scenario_index])
			print("Aim Position Set!!:",self.aimPosition)
			print("Scenario index : %i, score : "%(max_scenario_index,),scores[max_scenario_index])
			print("Scenario :")
			best_scenario = scenarios[max_scenario_index]
			for j in [2,1,0]:
				print(best_scenario[j])

		if tick % self.TICK_COOLTIME == 0:
			print(self.aimPosition)
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
			print('Here, nothing to do anymore.',self.aimPosition)
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
					results.append(board.perform_valid_key('UP', True))
				elif cmd=='L':
					results.append(board.perform_valid_key('LEFT', True))
				elif cmd=='R':
					results.append(board.perform_valid_key('RIGHT', True))
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
		for j in range(1, Board.BoardHeight-1):
			for i in range(1, Board.BoardWidth - 1):
				# if board[j][i] is hole.
				if scenario[j][i]:
					continue
				if scenario[j-1][i] and scenario[j+1][i] and scenario[j][i-1] and scenario[j][i+1]:
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