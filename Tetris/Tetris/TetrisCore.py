from Boards import *
from Shape import *

class Tetris(wx.Frame):
	def __init__(self,mode, inputFile=None, inputMachine=None, maxTick=-1):
		wx.Frame.__init__(self, None, title='Tetris', size=(500, 760))
		self.statusbar = self.CreateStatusBar()
		self.initFrame(mode=mode,inputFile=inputFile,inputMachine=inputMachine,maxTick=maxTick)

	def initFrame(self,mode, inputFile=None,inputMachine=None,maxTick=-1):
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
		
		if mode != 'Train':
			self.board.SetFocus()
			self.NextBlockPanel = NextBlockPanel(self, self.board)
			self.MainSizer = wx.BoxSizer(wx.HORIZONTAL)
			self.MainSizer.Add(self.board, 8, wx.EXPAND)
			self.MainSizer.Add(self.NextBlockPanel, 3, wx.EXPAND)
			self.SetSizer(self.MainSizer)
			self.Layout()
		self.Center()
		self.Show(True)

	def start(self):
		return self.board.start()

class NextBlockPanel(wx.Panel):
	def __init__(self, parent, board):
		wx.Panel.__init__(self, parent)
		self.parent = parent
		self.board = board

		self.nextPiece = Shape()
		self.next2Piece = Shape()
		self.next3Piece = Shape()
		self.next4Piece = Shape()
		self.next5Piece = Shape()

		self.Bind(wx.EVT_PAINT, self.OnPaint)

	def SetNextPieces(self, board):
		'''
		Set next pieces 
		And refresh for call EVT_PAINT
		'''
		self.nextPiece	= board.nextPiece
		self.next2Piece = board.next2Piece
		self.next3Piece = board.next3Piece
		self.next4Piece = board.next4Piece
		self.next5Piece = board.next5Piece
		self.Refresh()

	def OnPaint(self, event):
		dc = wx.PaintDC(self)

		ReviseX = [0, 0, -1, -0.5, -0.5, -1, 0, -1]
		ReviseY = [0, -0.5, -0.5, 0, 0, 0, -0.5, -0.5]
		LengY	= [0, 1.5, 1.5, 2, 1, 1, 1.5, 1.5]

		X = self.GetClientSize().GetWidth() * 0.5

		Y = (LengY[self.nextPiece.shape()] + 1) * self.board.squareHeight()
		for i in range(4):
			shape = self.nextPiece.shape()
			x = self.nextPiece.x(i)
			y = self.nextPiece.y(i)
			self.board.drawSquare(dc, X + (x + ReviseX[shape]) * self.board.squareWidth(), Y + (-y + ReviseY[shape]) * self.board.squareHeight(), shape)

		Y = Y + (LengY[self.nextPiece.shape()] + LengY[self.next2Piece.shape()] + 1) * self.board.squareHeight()
		for i in range(4):
			shape = self.next2Piece.shape()
			x = self.next2Piece.x(i)
			y = self.next2Piece.y(i)
			self.board.drawSquare(dc, X + (x + ReviseX[shape]) * self.board.squareWidth(), Y + (-y + ReviseY[shape]) * self.board.squareHeight(), shape)

		Y = Y + (LengY[self.next2Piece.shape()] + LengY[self.next3Piece.shape()] + 1) * self.board.squareHeight()
		for i in range(4):
			shape = self.next3Piece.shape()
			x = self.next3Piece.x(i)
			y = self.next3Piece.y(i)
			self.board.drawSquare(dc, X + (x + ReviseX[shape]) * self.board.squareWidth(), Y + (-y + ReviseY[shape]) * self.board.squareHeight(), shape)

		Y = Y + (LengY[self.next3Piece.shape()] + LengY[self.next4Piece.shape()] + 1) * self.board.squareHeight()
		for i in range(4):
			shape = self.next4Piece.shape()
			x = self.next4Piece.x(i)
			y = self.next4Piece.y(i)
			self.board.drawSquare(dc, X + (x + ReviseX[shape]) * self.board.squareWidth(), Y + (-y + ReviseY[shape]) * self.board.squareHeight(), shape)

		Y = Y + (LengY[self.next4Piece.shape()] + LengY[self.next5Piece.shape()] + 1) * self.board.squareHeight()
		for i in range(4):
			shape = self.next5Piece.shape()
			x = self.next5Piece.x(i)
			y = self.next5Piece.y(i)
			self.board.drawSquare(dc, X + (x + ReviseX[shape]) * self.board.squareWidth(), Y + (-y + ReviseY[shape]) * self.board.squareHeight(), shape)

