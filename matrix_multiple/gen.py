import numpy as np

a = np.random.rand(3000, 3000)
np.savetxt('a.csv', a, delimiter=',')

b = np.random.rand(3000, 3000)
np.savetxt('b.csv', b, delimiter=',')

c = np.random.rand(3000)
np.savetxt('c.csv', c, delimiter=',')

d = np.random.rand(3000)
np.savetxt('d.csv', d, delimiter=',')

