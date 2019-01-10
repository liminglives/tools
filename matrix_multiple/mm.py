import numpy as np
import time

start1 = time.time()
a = np.loadtxt(open('a.csv'), delimiter=',', skiprows=0)

b = np.loadtxt(open('b.csv'), delimiter=',', skiprows=0)

start = time.time()
np.dot(a, b)
print 'matrix matrix ', time.time() - start, start - start1


c = np.loadtxt(open('c.csv'), delimiter=',', skiprows=0)

start = time.time()
np.dot(a, c)
print 'matrix vector ', time.time() - start

d = np.loadtxt(open('d.csv'), delimiter=',', skiprows=0)

start = time.time()
#print np.dot(d, c)
print 'vector vector ', time.time() - start
