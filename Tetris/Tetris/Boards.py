﻿import wx
from Shape import *
import datetime
import pickle
class Board(wx.Panel):
	BoardWidth=10
	BoardHeight=22
	TICKS_FOR_LINEDOWN=100
	keycodes = [wx.WXK_LEFT, wx.WXK_RIGHT, wx.WXK_UP, wx.WXK_DOWN, wx.WXK_SPACE]
	ID_TIMER = 1


	def __init__(self, parent, dummy=False, maxTick=-1, train=False):
		#print("Board called")
		self.isdummy=dummy
		self.maxTick=maxTick
		self.istrain = train

		# if dummy, don't make the window.
		if not dummy:
			wx.Panel.__init__(self, parent, style=wx.WANTS_CHARS)
			self.verbose=True
			self.visualize=True
		else:			
			self.verbose=False
			self.visualize=False

		# 1. initiate timer for timer.
		if (not self.isdummy) and (not self.istrain):
			self.timer = wx.Timer(self, Board.ID_TIMER)

		# 2. bind event handlers.
		if (not self.isdummy) and (not self.istrain):
			self.Bind(wx.EVT_PAINT, self.OnPaint)
			self.Bind(wx.EVT_TIMER, self.OnTimer, id=Board.ID_TIMER)

		# 3. pointers to Current Piece and the next Piece
		self.curPiece = Shape()
		self.nextPiece = Shape()
		self.next2Piece = Shape()
		self.next3Piece = Shape()
		self.next4Piece = Shape()
		self.next5Piece = Shape()

		# 4. initBoard()
		self.initBoard()

	def initBoard(self):
		'''
		initialize board.
		Called only at the start.
		'''
		
		self.ticks=0

		self.keys=[]
		self.pieces=[]
		
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
		
		self.clearBoard()

		if not self.isdummy:
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
		

		self.nextPiece.setShape(self.newPiece())
		self.next2Piece.setShape(self.newPiece())
		self.next3Piece.setShape(self.newPiece())
		self.next4Piece.setShape(self.newPiece())
		self.next5Piece.setShape(self.newPiece())
		self.clearBoard()
		self.timer.Start(1)
		self.nextpiece()

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
				self.drawSquare(dc, 0 + x * self.squareWidth(),
					(Board.BoardHeight - y - 1) * self.squareHeight(),
					self.curPiece.shape())
					
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
		
		if self.ticks == self.maxTick:
			self.game_over()

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
			self.nextpiece()

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
				self.curPiece.setShape(Tetrominoes.NoShape)
			if (not self.isdummy) and (not self.istrain):
				statusbar=self.GetParent().statusbar
				statusbar.SetStatusText(str(self.numLinesRemoved))
				
				if self.visualize:
					self.Refresh()

	def newPiece(self):
		'''
		spawn new piece.
		'''
		#print("NEW PIECE CALLED",end=' ')
		newshape = random.randint(1,7)
		shape_str = ['Noshape', 'Z-shape', 'S-shape', '|-shape', 'T-shape', 'Square', 'L-shape', "L'-shape"]
		#print("PIECE :",shape_str[newshape])

		self.pieces.append((self.ticks,newshape))
		
		return newshape


	def nextpiece(self):		
		self.curPiece, self.nextPiece, self.next2Piece, self.next3Piece, self.next4Piece = \
			(self.nextPiece, self.next2Piece, self.next3Piece, self.next4Piece, self.next5Piece)
		self.next5Piece = Shape()
		newShape = self.newPiece()
		self.next5Piece.setShape(newShape)

		
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
		if (not self.isdummy) and (not self.istrain):
			self.timer.Stop()
		self.isStarted = False
		self.isOver = True

		if self.verbose:
			print('Game over. Score :',self.numLinesRemoved)

		if not self.istrain:
			statusbar = self.GetParent().statusbar
			statusbar.SetStatusText('Game Over')

		if not self.isdummy:
			self.save_history()
			

	#overriding.
	def save_history(self):
		# 1. Determine filename.
		if isinstance(self, Human_Board):
			name = 'Human'
		elif isinstance(self, Save_Board):
			return
		elif isinstance(self, Machine_Board):
			name = self.machine.name
		elif isinstance(self, Train_Board):
			if self.numLinesRemoved==0:
				return
			else:
				name=self.machine.name
		# 2. Get time info.
		now = datetime.datetime.now()
		time_string = str(now).replace(' ','_').replace('.',':').replace(':','-')
		filename = name+'_'+str(self.numLinesRemoved)+'_'+time_string+'.sav'

		# 3. Determine foldername.
		if isinstance(self, Train_Board):
			folder = 'D:/Dropbox/Tetris/'
		else:
			folder = 'E:/Tetris/'

		# 4. Save playfile.
		full=folder+filename
		with open(full, 'wb') as f:
			pickle.dump(self.keys,f)
			pickle.dump(self.pieces,f)

		# 5. Save modelfile if training.
		if isinstance(self, Train_Board):
			filename = name+'_'+str(self.numLinesRemoved)+'_'+time_string+'.model'
			full = folder+filename
			with open(full, 'wb') as f:
				pickle.dump(self.machine.gene, f)
		if self.verbose:
			print('Saved')	



class Human_Board(Board):
	def __init__(self, parent):
		super().__init__(parent)

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
		
		data=self.pieces[0]
		tick, piece = data
		if self.ticks == tick:
			self.pieces = self.pieces[1:]
			return piece
		elif self.ticks > tick:
			print('Skipped shape.')
			print('Current tick : %i, Data : (%i,%i)'%(self.ticks,tick,piece))
			self.pieces = self.pieces[1:]
			return piece


	#overriding.
	def save_history(self):
		pass


class Machine_Board(Board):
	def __init__(self, parent,inputMachine):
		self.machine = inputMachine
		super().__init__(parent)

	def initBoard_specific(self):
		pass

	def OnTimer_specific(self,event):
		'''
		in every tick, feedforward through the machine, and get the result.
		apply the result.
		'''
		#output must be in form (LEFT, RIGHT, UP, DOWN, SPACE)

		pieces = (self.curPiece, self.nextPiece, self.next2Piece, self.next3Piece, self.next4Piece, self.next5Piece)
		input = (self.board, self.curX, self.curY, pieces)
		output = self.machine.feedForward(input, self.ticks)
		if output is None:
			return
				
		for i in range(5):
			if output[i]>0:
				self.keys.append((self.ticks, Board.keycodes[i]))
				self.perform_valid_key(Board.keycodes[i])


class Train_Board(Board):
	def __init__(self, parent,inputMachine, maxTick):
		#print("Train_board called.")
		self.machine = inputMachine
		super().__init__(parent,maxTick=maxTick,train=True)
		self.verbose=False
		self.visualize=False

	def initBoard_specific(self):
		pass

	def OnTimer_specific(self,event):
		'''
		in every tick, feedforward through the machine, and get the result.
		apply the result.
		'''

		#output must be in form (LEFT, RIGHT, UP, DOWN, SPACE)
		pieces = (self.curPiece, self.nextPiece, self.next2Piece, self.next3Piece, self.next4Piece, self.next5Piece)
		input = (self.board, self.curX, self.curY, pieces)
		output = self.machine.feedForward(input, self.ticks)

		if output is None:
			return
				
		for i in range(5):
			if output[i]>0:
				self.keys.append((self.ticks, Board.keycodes[i]))
				self.perform_valid_key(Board.keycodes[i],verbose=False)

	def start(self):
		self.initBoard()
		self.isStarted=True
		self.numLinesRemoved = 0
		#self.clearBoard()
		self.nextPiece.setShape(self.newPiece())
		self.next2Piece.setShape(self.newPiece())
		self.next3Piece.setShape(self.newPiece())
		self.next4Piece.setShape(self.newPiece())
		self.next5Piece.setShape(self.newPiece())
		self.nextpiece()
		while True:
			self.OnTimer(None)
			if self.isOver:
				break
		#print("Ticks :",self.ticks)
		return self.numLinesRemoved