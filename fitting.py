# coding=utf-8

import matplotlib.pyplot as plt
import math
import numpy
import random
import fileToList

def polyLeastFit(x,y,order):
    matA = []
    for i in range(0, order + 1):
        matA1 = []
        for j in range(0, order + 1):
            tx = 0.0
            for k in range(0, len(x)):
                dx = 1.0
                for l in range(0, j + i):
                    dx = dx * x[k]
                tx += dx
            matA1.append(tx)
        matA.append(matA1)
    matA = numpy.array(matA)

    matB = []
    for i in range(0, order + 1):
        ty = 0.0
        for k in range(0, len(x)):
            dy = 1.0
            for l in range(0, i):
                dy = dy * x[k]
            ty += y[k] * dy
        matB.append(ty)
    matB = numpy.array(matB)
    matAA = numpy.linalg.solve(matA, matB)
    #print 'fit finished !'

    return matAA

def polyLeastFitCal(x,mat):
    y = []
    for i in range(0, len(x)):
        yy = 0.0
        for j in range(0, len(mat)):
            dy = 1.0
            for k in range(0, j):
                dy *= x[i]
            dy *= mat[j]
            yy += dy
        y.append(yy)
    #print 'fit calculation finished !'
    return y



def polyLeastFitTest():
    fig = plt.figure()
    ax = fig.add_subplot(111)
    order = 9
    timeFile = unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\12.12\\result\\synCoincidenceEM_10milliSec0329.txt', 'utf8')
    timeList = fileToList.fileToList(timeFile)
    tau = 1000000000000
    xa = []
    ya = []

    for i in range(len(timeList)):
        xa.append(timeList[i][0] )
        ya.append(timeList[i][1])

    # xa=xa[:80000]
    # ya=ya[:80000]
    #ax.plot(xa,ya,color='m',linestyle='',marker='.')

    matAA = polyLeastFit(xa, ya, order)
    yya = polyLeastFitCal(xa, matAA)
    for i in range(len(yya)):
        yya[i]=yya[i]-ya[i]
        print yya[i]
    ax.plot(xa, yya, color='g', linestyle='-', marker='')
    ax.legend()
    plt.show()
