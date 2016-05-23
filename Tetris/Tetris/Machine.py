import random as r
from TetrisCore import *
import copy
class Machine(object):
	def __init__(self, gene=None):
		if gene is None:
			#randomly initialize gene.
			pass
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
		output = []
		for j in range(Board.BoardHeight):
			lis=[]
			for i in range(Board.BoardWidth):
				if input[j][i]!=0:
					lis+=[1]
				else:
					lis+=[0]
			output+=lis
		return output


class RandomMachine(Machine):
	def __init__(self, cool_time=10):
		super().__init__()
		self.name='RandomMachine'
		self.TICK_COOLTIME = cool_time
		r.seed(11557)

	def instantiate(self):
		pass

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
	def __init__(self, cool_time=100):
		super().__init__()
		self.name='DeterministicMachine'
		self.TICK_COOLTIME = cool_time
		pass

	def instantiate(self):
		pass

	def feedForward(self, input, tick):
		#output must be in form (LEFT, RIGHT, UP, DOWN, SPACE)

		board = Machine.digitize(input)
	
		return (0,0,0,0,0)



class EvolutionMachine(Machine):
	pass

class NeuralNetMachine(Machine):
	pass