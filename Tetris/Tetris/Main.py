import wx
from StartMenu import *



def main():
	app=wx.App()
	frame = MainMenuFrame(None)
	frame.Show()
	app.MainLoop()

if __name__=='__main__':
	#neural_train()
	main()