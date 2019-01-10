import numpy as np
import time

a = np.random.rand(3000, 30000)
b = np.random.rand(30000, 3000)

print "wait"
time.sleep(5)

np.dot(a, b)

