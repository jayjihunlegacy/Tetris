import multiprocessing as mp
import os
import time
def worker1(lock,lists):
	
	i=0
	while True:
		i+=1
		pid = os.getpid()
		print('Worker1 :',pid,i,lists[0])
		
		lock.acquire()

	


def worker2():
	print('Worker2 :',pid)

if __name__=='__main__':
	jobs = []
	
	manager = mp.Manager()
	locks = [manager.Lock() for i in range(4)]
	lists=manager.list()
	lists.append(0)

	for i in range(4):
		p=mp.Process(target=worker1,args=(locks[i],lists))
		jobs.append(p)
	[lock.acquire() for lock in locks]
	[p.start() for p in jobs]

	for i in range(20):
		
		time.sleep(1)
		print('release!')
		lists[0]=i
		[lock.release() for lock in locks]
