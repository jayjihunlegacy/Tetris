import random
import datetime
import pickle
import time
from Mail import *
from Boards import *

# end of class.


class Tetris(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, title='Tetris', size=(360, 760))
		self.statusbar = self.CreateStatusBar()

	def initFrame(self,mode,name=None,inputFile=None,inputMachine=None,maxTick=None):
		'''
		initialize frame.
		'''
		#1. create statusbar and initialize.
		self.statusbar.SetStatusText('0')

		#2. create board and start it.
		if mode=='Human':
			self.board = Human_Board(self)
		elif mode == 'Save':
			self.board = Save_Board(self, inputFile)
		elif mode == 'Machine':
			self.board = Machine_Board(self, inputMachine)
		elif mode == 'Train':
			try:
				self.board.machine = inputMachine
				self.board.name = inputMachine.name
				self.board.initBoard()
			except:
				self.board = Train_Board(self, inputMachine, maxTick)

		else:
			print('Invalid mode')
		if name is not None:
			self.name = name
		#self.board.SetFocus()
		#self.Center()
		#self.Show(True)
		return self.board.start()
