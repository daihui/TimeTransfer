# coding=utf-8

'''
作者:Jairus Chan
程序:多项式曲线拟合算法
'''

import matplotlib.pyplot as plt
import math
import numpy
import random
import fileToList

fig = plt.figure()
ax = fig.add_subplot(111)

#阶数为9阶
order=9

timeFile = unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\12.12\\result\\synCoincidenceEM_0328.txt', 'utf8')
timeList = fileToList.fileToList(timeFile)
tau = 1000000000000
xa=[]
ya=[]

for i in range(len(timeList)):
    xa.append(timeList[i][1]/tau)
    ya.append(timeList[i][0]-timeList[i][1])

# xa=xa[:80000]
# ya=ya[:80000]
#ax.plot(xa,ya,color='m',linestyle='',marker='.')


#进行曲线拟合
matA=[]
for i in range(0,order+1):
	matA1=[]
	for j in range(0,order+1):
		tx=0.0
		for k in range(0,len(xa)):
			dx=1.0
			for l in range(0,j+i):
				dx=dx*xa[k]
			tx+=dx
		matA1.append(tx)
	matA.append(matA1)

#print(len(xa))
#print(matA[0][0])
matA=numpy.array(matA)

matB=[]
for i in range(0,order+1):
	ty=0.0
	for k in range(0,len(xa)):
		dy=1.0
		for l in range(0,i):
			dy=dy*xa[k]
		ty+=ya[k]*dy
	matB.append(ty)

matB=numpy.array(matB)

matAA=numpy.linalg.solve(matA,matB)

#画出拟合后的曲线
#print(matAA)
xxa= xa
yya=[]
for i in range(0,len(xxa)):
	yy=0.0
	for j in range(0,order+1):
		dy=1.0
		for k in range(0,j):
			dy*=xxa[i]
		dy*=matAA[j]
		yy+=dy
	yya.append(yy-ya[i])
	print yy-ya[i]
ax.plot(xxa,yya,color='g',linestyle='-',marker='')

ax.legend()
plt.show()