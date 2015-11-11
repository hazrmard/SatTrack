__author__ = 'Ibrahim'

# Testing python multiprocessing functionality
import multiprocessing as mp
import time

jobs = []

def worker(i):
    time.sleep(i)
    print 'worker function ', i, ' Name: ', mp.current_process().name


def main(n):
    for i in range(n):
        p = mp.Process(target=worker, args=[i], name='worker '+str(i))
        # p.daemon = True
        jobs.append(p)
        p.start()

if __name__ == '__main__':
    main(5)
    time.sleep(1)
    for p in jobs:
        print p.is_alive()
