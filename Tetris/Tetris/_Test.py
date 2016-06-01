import multiprocessing as mp
import os
import time

class A(object):
	def __init__(self):
		process = []
		for i in range(4):
			p = mp.Process(target=self.good)
			process.append(p)
		for p in process:
			p.start()
		for p in process:
			p.join()

	def good():
		print("good")

if __name__=='__main__':
	a=A()

