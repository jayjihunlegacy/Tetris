import os
import os.path
import pickle

folder = r'D:\Dropbox\Tetris/'
filelist = os.listdir(folder)
filelist = list(filter(lambda filename: filename.endswith('.model'), filelist))

for filename in filelist:
	full = folder+filename
	with open(full,'rb') as f:
		l = pickle.load(f)
	a_syn, b_syn = l
	print(filename,len(a_syn),len(b_syn))