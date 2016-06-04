import wx
from Machine import *
from TetrisCore import *
from Trainer import *

class MainMenuFrame(wx.Frame):
	def __init__(self, parent):
		wx.Frame.__init__(self, parent)

		self.Size = (660, 430)
		self.Panel = wx.Panel(self, wx.ID_ANY)

		#selectList = ["Human_play", "Machine_play", "Play_history", "Train_machine"]
		self.rb1 = wx.RadioButton(self.Panel, id=wx.ID_ANY, label='Human_play', pos=(30,265))
		self.rb2 = wx.RadioButton(self.Panel, id=wx.ID_ANY, label='Machine_play', pos=(30,285))
		self.rb3 = wx.RadioButton(self.Panel, id=wx.ID_ANY, label='Train_machine', pos=(30,305))
		self.rb4 = wx.RadioButton(self.Panel, id=wx.ID_ANY, label='Play_history', pos=(30,325))
		self.rb5 = wx.RadioButton(self.Panel, id=wx.ID_ANY, label='Evolution_train', pos=(30,345))

		self.box = wx.StaticBox(self.Panel, id=wx.ID_ANY, label='Choices', pos=(20,245), size=(480, 125)) 
		#self.SelectBox = wx.RadioBox(self.Panel, id=wx.ID_ANY, label='Choices', pos=(30,250), size=(300, 100), choices=selectList, style=wx.RA_SPECIFY_ROWS)
		self.Status = self.CreateStatusBar(style=wx.STB_SHOW_TIPS)
		self.StartButton = wx.Button(self.Panel, id==wx.ID_ANY, label='Start', pos=(520,257), size=(100, 110))

		self.HistoryTextCtrl = wx.TextCtrl(self.Panel, pos=(140,323), size =(350,20))

		self.SelectBox = wx.BoxSizer(wx.VERTICAL)
		self.SelectBox.Add(self.box)
		self.SelectBox.Add(self.rb1)
		self.SelectBox.Add(self.rb2)
		self.SelectBox.Add(self.rb3)
		self.SelectBox.Add(self.rb4)
		self.SelectBox.Add(self.rb5)
		self.SelectBox.Add(self.HistoryTextCtrl)

		self.StartButton.Bind(wx.EVT_BUTTON, self.OnStart)
		
		self.ShowMainImg()

	def ShowMainImg(self):
		FilePath = "Logo.bmp"
		LogoImg = wx.Image(FilePath, wx.BITMAP_TYPE_ANY)
		self.ImageCtrl = wx.StaticBitmap(self.Panel, wx.ID_ANY, wx.Bitmap(LogoImg))

	def OnStart(self, error):
		if self.rb1.GetValue() == True:
			#Human_play
			self.Destroy()
			human_play()
			
		elif self.rb2.GetValue() == True:
			#Machine_play
			self.Destroy()
			play_machine()
			
		elif self.rb3.GetValue() == True:
			#train_machine
			self.Destroy()
			train_machine()
			
		elif self.rb4.GetValue() == True:
			#play_history
			HistoryName = self.HistoryTextCtrl.GetValue()
			self.Destroy()
			play_history(HistoryName)
			
		elif self.rb5.GetValue() == True:
			#evolution_train
			self.Destroy()
			evolution_train()

		else:
			#error
			self.Status.SetStatusText('ANG')
			wx.MessageBox("ANG", "ANG" ,wx.OK | wx.ICON_INFORMATION)
			pass

def play_machine():
	# this should be changed to loading 'specific machine'
	machine = DeterministicMachine()
	tetris=Tetris(mode='Machine', inputMachine = machine)
	tetris.start()

def train_machine():
	machine = DeterministicMachine()
	tetris = Tetris(mode='Train', inputMachine=machine, maxTick=1000)
	score = tetris.start()

def play_history(filename):
	folder='C:/Tetris/'
	if filename[1]==':':
		full=filename
	else:
		full = folder+filename
	tetris = Tetris(mode='Save',inputFile=full)
	tetris.start()

def human_play():
	tetris = Tetris(mode='Human')
	tetris.start()

def evolution_train():
	trainer = EvolutionTrainer(
		pop_per_gen=256,
		sel_per_gen=64,
		max_generation=-1,
		use_migration=False
		)
	trainer.train()