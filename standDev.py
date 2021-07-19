import math
n = list(map(float,input('Input data here, comma separated: ').split(',')))
a = sum(n)/len(n)
s = math.sqrt(sum([(k-a)**2 for k in n])/(len(n)-1))
e = s/math.sqrt(len(n))
print('Average of data is',a)
print('Standard Deviation is',s)
print('Standard Error is',e)