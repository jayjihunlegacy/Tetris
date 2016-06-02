﻿import wx
import random
import datetime
import pickle

class Tetris(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, title='Tetris', size=(360, 760))

	def initFrame(self,mode,inputFile=None,inputMachine=None,maxTick=None):
		'''
		initialize frame.
		'''
		#1. create statusbar and initialize.
		self.statusbar = self.CreateStatusBar()
		self.statusbar.SetStatusText('0')

		#2. create board and start it.
		if mode=='Human':
			self.PlayBoard = Human_Board(self)
		elif mode == 'Save':
			self.PlayBoard = Save_Board(self, inputFile)
		elif mode == 'Machine':
			self.PlayBoard = Machine_Board(self, inputMachine)
		elif mode == 'Train':
			self.PlayBoard = Train_Board(self, inputMachine, maxTick)
		else:
			print('Invalid mode')

		self.Center()
		self.Show(True)
		return self.PlayBoard.start()

class Tetrominoes(object):
	NoShape = 0
	ZShape = 1
	SShape = 2
	LineShape = 3
	TShape = 4
	SquareShape = 5
	LShape = 6
	MirroredLShape = 7

	#Added type (Not Shape, for drawing or special block)
	Aim = 8

class Shape(object):    
    coordsTable = (
        ((0, 0),     (0, 0),     (0, 0),     (0, 0)),
        ((0, -1),    (0, 0),     (-1, 0),    (-1, 1)),
        ((0, -1),    (0, 0),     (1, 0),     (1, 1)),
        ((0, -1),    (0, 0),     (0, 1),     (0, 2)),
        ((-1, 0),    (0, 0),     (1, 0),     (0, 1)),
        ((0, 0),     (1, 0),     (0, 1),     (1, 1)),
        ((-1, -1),   (0, -1),    (0, 0),     (0, 1)),
        ((1, -1),    (0, -1),    (0, 0),     (0, 1))
    )

    def __init__(self):
        self.coords = [[0,0] for i in range(4)]
        self.pieceShape = Tetrominoes.NoShape
        self.setShape(Tetrominoes.NoShape)

    def shape(self):        
        return self.pieceShape

    def setShape(self, shape):        
        table = Shape.coordsTable[shape]
        for i in range(4):
            for j in range(2):
                self.coords[i][j] = table[i][j]

        self.pieceShape = shape

    def setRandomShape(self):        
        self.setShape(random.randint(1, 7))

    def x(self, index):        
        return self.coords[index][0]

    def y(self, index):        
        return self.coords[index][1]

    def setX(self, index, x):        
        self.coords[index][0] = x

    def setY(self, index, y):        
        self.coords[index][1] = y

    def minX(self):        
        m = self.coords[0][0]
        for i in range(4):
            m = min(m, self.coords[i][0])
        return m

    def maxX(self):        
        m = self.coords[0][0]
        for i in range(4):
            m = max(m, self.coords[i][0])
        return m

    def minY(self):        
        m = self.coords[0][1]
        for i in range(4):
            m = min(m, self.coords[i][1])
        return m

    def maxY(self):        
        m = self.coords[0][1]        
        for i in range(4):
            m = max(m, self.coords[i][1])
        return m

    def rotatedLeft(self):        
        if self.pieceShape == Tetrominoes.SquareShape:
            return self

        result = Shape()
        result.pieceShape = self.pieceShape
        
        for i in range(4):
            result.setX(i, self.y(i))
            result.setY(i, -self.x(i))

        return result

    def rotatedRight(self):        
        if self.pieceShape == Tetrominoes.SquareShape:
            return self

        result = Shape()
        result.pieceShape = self.pieceShape
        
        for i in range(4):
            result.setX(i, -self.y(i))
            result.setY(i, self.x(i))

        return result


class Board(wx.Panel):
	BoardWidth=10
	BoardHeight=22
	TICKS_FOR_LINEDOWN=100
	keycodes = [wx.WXK_LEFT, wx.WXK_RIGHT, wx.WXK_UP, wx.WXK_DOWN, wx.WXK_SPACE]
	ID_TIMER = 1

	def __init__(self, parent, dummy=False):		
		if not dummy:
			wx.Panel.__init__(self, parent, style=wx.WANTS_CHARS)
			self.name = 'Noname'
			self.initBoard()
			self.verbose=True
			self.visualize=True
		else:
			self.name = 'Dummy'
			self.numLinesRemoved=0
			self.verbose=False
			self.visualize=False

		self.isdummy=dummy

	def initBoard(self):
		'''
		initialize board.
		Called only at the start.
		'''
		#initiate timer for timer.
		self.timer = wx.Timer(self, Board.ID_TIMER)
		self.ticks=0

		#1. pointers to Current Piece and the next Piece
		self.curPiece = Shape()
		self.nextPiece = Shape()

		#2. coordinate of current Piece (center coordinate of it)
		self.curX = 0
		self.curY = 0
		
		#3. data
		self.numLinesRemoved = 0
		self.board = []

		#4. booleans for go / stop control
		self.isStarted = False
		self.isPaused = False
		self.isOver = False

		#5. bind event handlers.
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_TIMER, self.OnTimer, id=Board.ID_TIMER)
		
		self.clearBoard()

		self.keys=[]
		self.pieces=[]
		self.initBoard_specific()
		

	def shapeAt(self, x,y):
		return self.board[y][x]

	def setShapeAt(self,x,y,shape):
		self.board[y][x] = shape

	def squareWidth(self):
		return self.GetClientSize().GetWidth() / Board.BoardWidth

	def squareHeight(self):
		return self.GetClientSize().GetHeight() / Board.BoardHeight

	def start(self):
		'''
		start the board.
		Called only at the start.
		'''
		# do nothing when paused. (unpause will be done in pause(self))
		if self.isPaused:
			return
		print('Start!')
		self.isStarted=True
		self.numLinesRemoved=0
		self.clearBoard()

		self.newPiece()
		self.timer.Start(1)

	def pause(self):
		'''
		pause or unpause game.
		Called when 'P' is pressed.
		'''
		# skip if the game is not even started.
		if not self.isStarted:
			return

		# set statusbar properly.
		self.isPaused = not self.isPaused
		statusbar =self.GetParent().statusbar
		if self.isPaused:
			self.timer.Stop()
			statusbar.SetStatusText('paused')
		else:
			self.timer.Start(1)
			statusbar.SetStatusText(str(self.numLinesRemoved))

		# refresh.
		self.Refresh()

	def clearBoard(self):
		'''
		clear the board.
		'''
		self.board=[]
		
		for j in range(Board.BoardHeight):
			lis=[Tetrominoes.NoShape for i in range(Board.BoardWidth)]		
			self.board.append(lis)

		#for i in range(Board.BoardHeight * Board.BoardWidth):
	#		self.board.append(Tetrominoes.NoShape)

	def OnPaint(self, event):
		if not (self.visualize or self.isOver):
			return
		dc = wx.PaintDC(self)

		#draw outline of playing board
		dc.SetBrush(wx.Brush('#000000'))
		dc.DrawRectangle(1, 1, self.BoardWidth * self.squareWidth() - 1, self.BoardHeight * self.squareHeight() - 1)

		for i in range(Board.BoardHeight):
			for j in range(Board.BoardWidth):
				shape = self.shapeAt(j, Board.BoardHeight - i - 1)
				if shape != Tetrominoes.NoShape:
					self.drawSquare(dc,
						0 + j * self.squareWidth(),
						i * self.squareHeight(), shape)

		if self.curPiece.shape() != Tetrominoes.NoShape:
			AimY = self.curY
			while AimY > 0:
				if not self.checkMove(self.curPiece, self.curX, AimY - 1):
					break
				AimY-=1
			for i in range(4):
				x = self.curX + self.curPiece.x(i)
				y = AimY - self.curPiece.y(i)
				self.drawSquare(dc, 0 + x * self.squareWidth(), (Board.BoardHeight - y - 1) * self.squareHeight(), Tetrominoes.Aim)
			for i in range(4):
				x = self.curX + self.curPiece.x(i)
				y = self.curY - self.curPiece.y(i)
				self.drawSquare(dc, 0 + x * self.squareWidth(), (Board.BoardHeight - y - 1) * self.squareHeight(), self.curPiece.shape())
					
	def perform_valid_key(self, keycode, verbose=True, isstr=False):
		if keycode == wx.WXK_LEFT or (isstr and keycode=='LEFT'):
			if verbose and self.verbose:
				print('Pressed Key : LEFT')
			return self.tryMove(self.curPiece, self.curX - 1, self.curY)
		elif keycode == wx.WXK_RIGHT or (isstr and keycode=='RIGHT'):
			if verbose and self.verbose:
				print('Pressed Key : RIGHT')
			return self.tryMove(self.curPiece, self.curX + 1, self.curY)
		elif keycode == wx.WXK_UP or (isstr and keycode=='UP'):
			if verbose and self.verbose:
				print('Pressed Key : UP')
			return self.tryMove(self.curPiece.rotatedRight(), self.curX, self.curY)
		elif keycode == wx.WXK_DOWN or (isstr and keycode=='DOWN'):
			if verbose and self.verbose:
				print('Pressed Key : DOWN')
			return self.oneLineDown()		
		elif keycode == wx.WXK_SPACE or (isstr and keycode=='SPACE'):
			if verbose and self.verbose:
				print('Pressed Key : SPACE')
			return self.dropDown()

	def OnTimer(self, event):
		'''
		event handler for TICK_TIMER
		Called when 'tick'
		'''
		
		self.ticks+=1
		#when tick is enough for Linedown, 
		if self.ticks % Board.TICKS_FOR_LINEDOWN == 0:
			self.oneLineDown()
		# location of this code is vague...
		self.OnTimer_specific(event)
				
	

	def dropDown(self):
		'''
		drop down current piece
		'''
		newY = self.curY
		while newY > 0:
			if not self.tryMove(self.curPiece, self.curX, newY - 1):
				break
			newY-=1

		self.pieceDropped()

	def oneLineDown(self):
		'''
		get the piece one line down.
		'''
		# call pieceDropped() when piece CANNOT move.
		if not self.tryMove(self.curPiece, self.curX, self.curY - 1):
			self.pieceDropped()

	def pieceDropped(self):
		'''
		routine for dropped piece.
		Called when piece has landed.
		'''

		for i in range(4):
			x = self.curX + self.curPiece.x(i)
			y = self.curY - self.curPiece.y(i)
			self.setShapeAt(x, y, self.curPiece.shape())

		#remove complete lines.
		self.removeFullLines()


		#spawn new piece
		if not self.isdummy:
			self.newPiece()

	def removeFullLines(self):
		'''
		remove complete lines
		Called when any piece has landed.
		'''

		numFullLines = 0
		
		rowsToRemove=[]

		for i in range(Board.BoardHeight):
			n = 0
			for j in range(Board.BoardWidth):
				if not self.shapeAt(j, i) == Tetrominoes.NoShape:
					n = n + 1
			if n == 10:
				rowsToRemove.append(i)
		rowsToRemove.reverse()
		for m in rowsToRemove:
			for k in range(m, Board.BoardHeight-1):
				for l in range(Board.BoardWidth):
					self.setShapeAt(l, k, self.shapeAt(l, k + 1))

		numFullLines = numFullLines + len(rowsToRemove)

		if numFullLines > 0:
			self.numLinesRemoved = self.numLinesRemoved + numFullLines
			if not self.isdummy:
				statusbar=self.GetParent().statusbar
				statusbar.SetStatusText(str(self.numLinesRemoved))
				self.curPiece.setShape(Tetrominoes.NoShape)
				if self.visualize:
					self.Refresh()

	def newPiece(self):
		'''
		spawn new piece.
		'''

		self.curPiece = self.nextPiece	

		self.nextPiece.setRandomShape()
		shape = self.nextPiece.shape()
		self.pieces.append((self.ticks,shape))
		shape_str = ['Noshape', 'Z-shape', 'S-shape', '|-shape', 'T-shape', 'Square', 'L-shape', "L'-shape"]
		if self.verbose:
			print('Next Shape :',shape_str[shape])

		self.curX = Board.BoardWidth//2 + 1
		self.curY = Board.BoardHeight - 1 + self.curPiece.minY()

		#when cannot place new piece, GAME OVER !
		if not self.tryMove(self.curPiece, self.curX, self.curY):
			self.game_over()

	def checkMove(self, newPiece, newX, newY):
		'''
		check availability of placing newPiece on (newX, newY).
		If failed, return False.
		'''
		for i in range(4):
			x=newX+newPiece.x(i)
			y=newY-newPiece.y(i)

			# if out of boundary, CANT!
			if x < 0 or x >= Board.BoardWidth or y < 0 or y >= Board.BoardHeight:
				return False

			# if other block exists, CANT!
			if self.shapeAt(x, y) != Tetrominoes.NoShape:
				return False

		return True

	def tryMove(self, newPiece, newX, newY):
		'''
		check first, if true:
		try to place newPiece on (newX, newY).
		If failed, return False.
		'''
		if not self.checkMove(newPiece, newX, newY):
			return False

		self.curPiece = newPiece
		self.curX = newX
		self.curY = newY
		if (not self.isdummy) and self.visualize:
			self.Refresh()
		return True

	def drawSquare(self,dc,x,y,shape):

		colors = ['#000000', '#CC6666', '#66CC66', '#6666CC',
                  '#CCCC66', '#CC66CC', '#66CCCC', '#DAAA00',
				  '#646464']

		light = ['#000000', '#F89FAB', '#79FC79', '#7979FC', 
                 '#FCFC79', '#FC79FC', '#79FCFC', '#FCC600',
				 '#969696']

		dark = ['#000000', '#803C3B', '#3B803B', '#3B3B80', 
                '#80803B', '#803B80', '#3B8080', '#806200',
				'#323232']

		pen = wx.Pen(light[shape])
		pen.SetCap(wx.CAP_PROJECTING)
		dc.SetPen(pen)

		dc.DrawLine(x, y + self.squareHeight() - 1, x, y)
		dc.DrawLine(x, y, x + self.squareWidth() - 1, y)

		darkpen = wx.Pen(dark[shape])
		darkpen.SetCap(wx.CAP_PROJECTING)
		dc.SetPen(darkpen)

		dc.DrawLine(x + 1, y + self.squareHeight() - 1,
            x + self.squareWidth() - 1, y + self.squareHeight() - 1)
		dc.DrawLine(x + self.squareWidth() - 1, 
        y + self.squareHeight() - 1, x + self.squareWidth() - 1, y + 1)

		dc.SetPen(wx.TRANSPARENT_PEN)
		dc.SetBrush(wx.Brush(colors[shape]))
		dc.DrawRectangle(x + 1, y + 1, self.squareWidth() - 2, 
		self.squareHeight() - 2)

	def game_over(self):
		self.curPiece.setShape(Tetrominoes.NoShape)
		self.timer.Stop()
		self.isStarted = False
		self.isOver = True
		print('Game over. Score :',self.numLinesRemoved)
		statusbar = self.GetParent().statusbar
		statusbar.SetStatusText('Game Over')
		self.save_history()

	def save_history(self):
		now = datetime.datetime.now()
		time_string = str(now).replace(' ','_').replace('.',':').replace(':','-')
		filename = self.name+'_'+str(self.numLinesRemoved)+'_'+time_string+'.sav'
		folder = 'C:/Tetris/'
		full=folder+filename
		with open(full, 'wb') as f:
			pickle.dump(self.keys,f)
			pickle.dump(self.pieces,f)
		print('Saved')


class Human_Board(Board):
	def __init__(self, parent):
		super().__init__(parent)
		self.name = 'Human'

	def initBoard_specific(self):
		self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

	def OnKeyDown(self, event):
		'''
		event handler for key_down.
		Called when any key is down.
		'''
		# skip when not even started.
		if (not self.isStarted or self.curPiece.shape() == Tetrominoes.NoShape) and not self.isOver:
			event.Skip()
			return

		keycode = event.GetKeyCode()

		if keycode == ord('R') or keycode == ord('r'):
			self.initBoard(self.inputDevice)
			self.start()
			return

		# 1. when toggle Pause
		if keycode == ord('P') or keycode == ord('p'):
			self.pause()
			return

		# 2. when paused, ignore everything
		if self.isPaused or self.isOver:
			return

		# 3. if valid key pressed, put it to save kit
		if keycode in Board.keycodes:
			self.keys.append((self.ticks, keycode))
			self.perform_valid_key(keycode)
		else:
			event.Skip()
			return

	#overriding.
	def OnTimer_specific(self, event):
		p=self.curPiece
		tup=(p.maxX(),p.minX(),p.maxY(),p.minY())
		#print(tup)
		print(p.pieceShape)
		print(self.curX, self.curY)
		pass
	
class Save_Board(Board):
	def __init__(self, parent, inputFile):
		self.inputFile = inputFile
		super().__init__(parent)
		

	def initBoard_specific(self):
		try:
			with open(self.inputFile, 'rb') as f:
				self.keys = pickle.load(f)
				self.pieces = pickle.load(f)
		except:
			print('Failed Loading :',self.inputFile)
			exit()

	def OnTimer_specific(self,event):
		# if some command is left,
		while len(self.keys) > 0:
			data = self.keys[0]
			tick, cmd = data
			if self.ticks == tick:
				self.perform_valid_key(cmd)
				self.keys=self.keys[1:]
			elif self.ticks > tick:
				print('Skipped cmd.')
				print('Current tick : %i, Data : (%i,%i)'%(self.ticks,tick,cmd))
				self.keys=self.keys[1:]
			else:
				break

	#overriding.
	def newPiece(self):
		self.curPiece = self.nextPiece	
		data=self.pieces[0]
		tick, piece = data
		if self.ticks == tick:
			self.nextPiece.setShape(piece)
			self.pieces = self.pieces[1:]
		elif self.ticks > tick:
			print('Skipped shape.')
			print('Current tick : %i, Data : (%i,%i)'%(self.ticks,tick,piece))
			self.pieces = self.pieces[1:]

		self.curX = Board.BoardWidth//2 + 1
		self.curY = Board.BoardHeight - 1 + self.curPiece.minY()

		#when cannot place new piece, GAME OVER !
		if not self.tryMove(self.curPiece, self.curX, self.curY):
			self.game_over()

	#overriding.
	def save_history(self):
		pass


class Machine_Board(Board):
	def __init__(self, parent,inputMachine):
		self.machine = inputMachine
		super().__init__(parent)
		self.name = inputMachine.name

	def initBoard_specific(self):
		pass

	def OnTimer_specific(self,event):
		'''
		in every tick, feedforward through the machine, and get the result.
		apply the result.
		'''
		#output must be in form (LEFT, RIGHT, UP, DOWN, SPACE)
		input = (self.board, self.curX, self.curY, self.curPiece)
		output = self.machine.feedForward(input, self.ticks)
		if output is None:
			return
				
		for i in range(5):
			if output[i]>0:
				self.keys.append((self.ticks, Board.keycodes[i]))
				self.perform_valid_key(Board.keycodes[i])


class Train_Board(Board):
	def __init__(self, parent,inputMachine, maxTick):
		self.machine = inputMachine
		super().__init__(parent)
		self.name = inputMachine.name
		self.verbose=False
		self.visualize= False
		self.maxTick=maxTick

	def initBoard_specific(self):
		pass
	
	def OnTimer_specific(self,event):
		'''
		in every tick, feedforward through the machine, and get the result.
		apply the result.
		'''
		if self.ticks==self.maxTick:
			print('Game over due to max tick.')
			self.game_over()


		#output must be in form (LEFT, RIGHT, UP, DOWN, SPACE)
		input = (self.board, self.curX, self.curY, self.curPiece)
		output = self.machine.feedForward(input, self.ticks)
				
		for i in range(5):
			if output[i]>0:
				self.keys.append((self.ticks, Board.keycodes[i]))
				self.perform_valid_key(Board.keycodes[i],verbose=False)

	def start(self):
		self.isStarted=True
		self.numLinesRemoved = 0
		self.clearBoard()
		self.newPiece()
		while True:
			self.OnTimer(None)
			if self.isOver:
				break
		print("Ticks :",self.ticks)
		return self.numLinesRemoved