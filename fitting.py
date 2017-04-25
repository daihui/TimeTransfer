# coding=utf-8

import matplotlib.pyplot as plt
import math
import numpy
import random
import fileToList
import filter

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

def polyLeastFitSegment(x,y,order,segmentTime):
    count=0
    s=0
    fitList=[]
    residual=[]
    xTmp=[]
    yTmp=[]
    lastTime=x[0]
    for i,time in enumerate(x):
        if time<lastTime+segmentTime:
            xTmp.append(time)
            yTmp.append(y[i])
            #lastTime=time
            count += 1
        else:
            if len(xTmp)>2*order:
                mat=polyLeastFit(xTmp,yTmp,order)
                y_fit=polyLeastFitCal(xTmp,mat)
                for j,yy in enumerate(y_fit):
                    fitList.append([yTmp[j]-yy])
                    residual.append([(yTmp[j] - yy)])
                count=0
                s+=1
                del xTmp[:]
                del yTmp[:]
                xTmp.append(time)
                yTmp.append(y[i])
                lastTime=time
                count += 1
            else:
                xTmp.append(time)
                yTmp.append(y[i])
                lastTime = time
                count += 1
    if xTmp:
        mat = polyLeastFit(xTmp, yTmp, order)
        y_fit = polyLeastFitCal(xTmp, mat)
        for j, yy in enumerate(y_fit):
            fitList.append([ yTmp[j] - yy])
            residual.append([(yTmp[j] - yy)])
            count += 1
        s+=1
    print 'data fitting in %s segment.'%s
    return fitList,residual


def polyLeastFitTest(date):

    order = 9
    timeFile = unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\result\\synCoincidenceEM_0329.txt'%date, 'utf8')
    timeList = fileToList.fileToList(timeFile)
    xa = []
    ya = []
    y=[]

    for i in range(len(timeList)):
        xa.append(timeList[i][1] )
        ya.append(timeList[i][0] - timeList[i][1])

    xa=xa[80000:120000]
    ya=ya[80000:120000]


    matAA = polyLeastFit(xa, ya, order)
    yya = polyLeastFitCal(xa, matAA)
    for i in range(len(yya)):
        y.append([yya[i]-ya[i]])
        # print yya[i]
    filter.dotFilter(y,0,10000,3)
    fileToList.listToFile(y,timeFile[:-4]+'_%s_residual_dotfilt.txt'%date)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(xa, y, color='g', linestyle='-', marker='')
    # ax.plot(xa,ya,color='m',linestyle='',marker='.')
    ax.legend()
    plt.show()

def polyLeastFitSegmentTest(date):
    order = 9
    timeFile = unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\result\\synCoincidenceEM_0423_eff1-200nsok.txt' % date, 'utf8')
    #timeFile=unicode('E:\Experiment Data\时频传输数据处理\丽江测试\\4.14\\4.14-lzx-lj-400s_coinDiff_segment_search.txt','utf8')
    timeList = fileToList.fileToList(timeFile)
    xa = []
    ya = []
    x=[]

    for i in range(len(timeList)):
        xa.append(timeList[i][1])
        ya.append(timeList[i][0] - timeList[i][1])
        # xa.append(timeList[i][0])
        # ya.append(timeList[i][1])

    # xa = xa[50000:70000]
    # ya = ya[50000:70000]

    fitList,residual=polyLeastFitSegment(xa,ya,order,30000000000000)
    #filter.dotFilter(residual, 0, 10000.0, 3)
    xa,residual=filter.thresholdFilter(xa,residual,0,10000)
    fileToList.listToFile(residual, timeFile[:-4] + '_%s_residual_segment_thresholdFilter0424.txt' % date)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(xa, residual, color='g', linestyle='-', marker='')
    #ax.plot(xa,ya/1000000000,color='m',linestyle='',marker='.')
    ax.legend()
    plt.show()