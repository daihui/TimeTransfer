#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'levitan'

import matplotlib.pyplot as plt
import math
import numpy
import random
import fileToList
import filter
import clockTimeCalibrate
import gpsOrbit
from scipy import stats
from scipy.optimize import leastsq

def sphere_fun(P,x,y,z):
    [x0,y0,z0,R]=P
    # print P
    return (numpy.sqrt((x-x0)**2+(y-y0)**2+(z-z0)**2)-R)

def residual_fun(P,x,y,z):
    return abs(sphere_fun(P,x,y,z))

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
    timeUnit=1000000000000.0
    count=0
    s=0
    fitList=[]
    residual=[]
    xa=[]
    ya=[]
    xTmp=[]
    yTmp=[]
    lastTime=x[0]
    lastTimeIndex=0
    for i,time in enumerate(x):
        if time<lastTime+segmentTime:
            xTmp.append(time)
            yTmp.append(y[i])
            #lastTime=time
            count += 1
        else:
            if len(xTmp)>order:
                mat=polyLeastFit(xTmp,yTmp,order)
                y_fit=polyLeastFitCal(xTmp,mat)
                #print mat
                for j,yy in enumerate(y_fit):
                    fitList.append([yy])
                    residual.append([(yTmp[j] - yy)/timeUnit])
                    xa.append(xTmp[j])
                    ya.append(yTmp[j])
                count=0
                s+=1
                del xTmp[:]
                del yTmp[:]
                xTmp.append(time)
                yTmp.append(y[i])
                lastTime=time
                lastTimeIndex=i
                count += 1
            else:
                xTmp.append(time)
                yTmp.append(y[i])
                lastTime = time
                lastTimeIndex = i
                count += 1
    if len(xTmp)>order:
        mat = polyLeastFit(xTmp, yTmp, order)
        y_fit = polyLeastFitCal(xTmp, mat)
        for j, yy in enumerate(y_fit):
            fitList.append([yy])
            residual.append([(yTmp[j] - yy)/timeUnit])
            xa.append(xTmp[j])
            ya.append(yTmp[j])
            count += 1
        s+=1
    else:
        print 'no data or few data in this time segment'
        print len(xTmp)
    print 'data fitting in %s segment.'%s
    return xa,ya,fitList,residual

def polyFitSegment(x,y,order,segmentTime):
    timeUnit=1000000000000.0
    count=0
    s=0
    fitList=[]
    residual=[]
    xa = []
    ya = []
    xTmp=[]
    yTmp=[]
    lastTime=x[0]
    lastTimeIndex=0
    for i,time in enumerate(x):
        if time/timeUnit<lastTime/timeUnit+segmentTime:
            xTmp.append(time/timeUnit)
            yTmp.append(y[i]/timeUnit)
            #lastTime=time
            count += 1
        else:
            if len(xTmp)>2*order:
                mat=numpy.polyfit(xTmp,yTmp,order)
                Fx=numpy.poly1d(mat)
                y_fit=Fx(xTmp)
                for j,yy in enumerate(y_fit):
                    fitList.append([yy])
                    residual.append([(yTmp[j] - yy)])
                    xa.append(xTmp[j]*timeUnit)
                    ya.append(yTmp[j]*timeUnit)
                count=0
                s+=1
                del xTmp[:]
                del yTmp[:]
                xTmp.append(time/timeUnit)
                yTmp.append(y[i]/timeUnit)
                lastTime=time
                lastTimeIndex=i
                count += 1
            else:
                xTmp.append(time/timeUnit)
                yTmp.append(y[i]/timeUnit)
                lastTime = time
                lastTimeIndex = i
                count += 1
    if len(xTmp)>order:
        mat = numpy.polyfit(xTmp, yTmp, order)
        Fx = numpy.poly1d(mat)
        y_fit = Fx(xTmp)
        if len(xTmp) == len(x):
            print 'fit matrix: %s' % mat
        for j, yy in enumerate(y_fit):
            fitList.append([yy])
            residual.append([(yTmp[j] - yy)])
            xa.append(xTmp[j]*timeUnit)
            ya.append(yTmp[j]*timeUnit)
            count += 1
        s+=1
    else:
        print 'no data or few data in this time segment'
        print len(xTmp)
    print 'data fitting in %s segment.'%s
    return xa,ya,fitList,residual

def clockDiffByDistance(timeList1,timeList2,gpsTimeList1,gpsTimeList2,delayList,shift):
    factor1=clockTimeCalibrate.clockTimeFactor(gpsTimeList1)
    factor2=clockTimeCalibrate.clockTimeFactor(gpsTimeList2)
    list1=clockTimeCalibrate.timeCalibrate(timeList1,factor1)
    list2=clockTimeCalibrate.timeCalibrate(timeList2,factor2)
    gpsTimeList1=clockTimeCalibrate.timeCalibrate(gpsTimeList1,factor1)
    gpsTimeList2=clockTimeCalibrate.timeCalibrate(gpsTimeList2,factor2)

    lenght=len(list1)
    Num=4
    result=[]

    for index in range(lenght):
        startNo=int(list1[index][0]/1000000000000)-1
        delayFun1,delayFun2=gpsOrbit.gpsLagInterFun(gpsTimeList1,gpsTimeList2,delayList,startNo,Num,shift)
        delay1=delayFun1(list1[index][0])
        delay2=delayFun2(list2[index][0])
        delay1=delayFun1(list1[index][0]-delay1)
        delay2=delayFun2(list2[index][0]-delay2)
        delay1 = delayFun1(list1[index][0] - delay1)
        delay2 = delayFun2(list2[index][0] - delay2)
        coinDelay=list1[index][0]-delay1-(list2[index][0]-delay2)
        result.append([timeList1[index][0],list1[index][0],coinDelay,delay1,delay2])
    print 'clock difference calculated by satellite distance'
    return result

def clockDiffByDistanceTest(date):
    shift=-19
    timeFile = unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\result\\synCoincidenceEM_0530-85-235_filtered.txt' % date,
                       'utf8')
    gpsFile1=unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\send_fixed_GPSTime.txt' % date,
                       'utf8')
    gpsFile2 = unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\recv_fixed_GPSTime.txt' % date,
                       'utf8')
    delayFile=unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\GPS_Recv_Precise_disDelay.txt' % date,
                       'utf8')
    saveFile=timeFile[:-4]+'_diffByDistance.txt'
    timeList = fileToList.fileToList(timeFile)
    gpsTimeList1=fileToList.fileToList(gpsFile1)
    gpsTimeList2=fileToList.fileToList(gpsFile2)
    delayList=fileToList.fileToList(delayFile)
    timeList1 = []
    timeList2 = []

    for i in range(len(timeList)):
        timeList1.append([timeList[i][0]])
        timeList2.append([timeList[i][1]])

    result=clockDiffByDistance(timeList1,timeList2,gpsTimeList1,gpsTimeList2,delayList,shift)
    fileToList.listToFile(result,saveFile)



def polyFitTest():

    order = 65
    timeFile = unicode('C:\Users\Levit\Experiment Data\双站数据\\20180109\\GPSJ2000.txt', 'utf8')
    timeList = fileToList.fileToList(timeFile)
    xa = []
    ya = []
    sec=[]
    residual=[]
    timeNormal = 100000000000

    for i in range(len(timeList)):
        xa.append(timeList[i][0]-timeList[0][0] )
        # ya.append((timeList[i][0] - timeList[i][1]))
        # xa.append(i)
        ya.append((timeList[i][5]*1000))
    # xa, ya, timeList, fitList, residual = filter.fitFilter(timeList, 3000 / 1000000000000.0, 1, 2)
    # for i in range(len(timeList)):
    #     ya[i]=(timeList[i][0] - timeList[i][1])
    startSec=int(xa[0]/ 1000000000000)
    endSec=int(xa[-1]/ 1000000000000)
    # print startSec,endSec
    # for i in range(startSec,endSec+1):
    #     sec.append(i* 1000000000000)

    mat = numpy.polyfit(xa, ya, order)
    Fx = numpy.poly1d(mat)
    y_fit = Fx(xa)
    # y_sec=Fx(sec)

    # for i in range(len(sec)):
    #     print sec[i]/ 1000000000000,y_sec[i]

    for i in range(len(y_fit)):
        residual.append([y_fit[i]-ya[i]])
    # filter.dotFilter(y,0,10000,3)
    # fileToList.listToFile(residual,timeFile[:-4]+'_%s_fit_residual.txt'%order)
    print numpy.std(residual,ddof=1)
    # xa, residual = filter.normalByTime(timeList, residual, timeNormal)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(xa, residual, color='g', linestyle='-', marker='*')
    # ax.plot(sec,y_sec,color='m',linestyle='',marker='.')
    # ax.plot(xa, ya, color='m', linestyle='', marker='.')
    ax.legend()
    plt.show()

def polyLeastFitSegmentTest(date):
    order =50
    timeNormal=50000000000
    timeFile = unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\Result\\synCoincidenceEM_0530-85-250-EM--18.txt' % date, 'utf8')
    # timeFile=unicode('E:\Experiment Data\时频传输数据处理\丽江测试\\4.14\\4.14-lzx-lj-400s_coinDiff_segment_search.txt','utf8')
    timeList = fileToList.fileToList(timeFile)
    xa = []
    ya = []
    x=[]

    for i in range(len(timeList)):
        xa.append(timeList[i][1])
        ya.append(timeList[i][0] - timeList[i][1])
        xa.append(timeList[i][0])
        ya.append(timeList[i][1])
    #
    xa = xa[50000:70000]
    ya = ya[50000:70000]
    #
    print len(xa), len(ya)
    xa,ya =filter.preFilter(timeList,2,100000)
    print len(xa),len(ya)
    fitList,residual=polyLeastFitSegment(xa,ya,10,1000)
    filter.dotFilter(residual, 0, 10000.0, 3)
    xa,ya,residual=filter.thresholdFilter(xa,ya,residual,0,4000)
    fitList, residual = polyLeastFitSegment(xa, ya, order, 100)
    xa, ya, residual = filter.thresholdFilter(xa, ya, residual, 0, 2500)
    # xa,ya,timeList,fitList,residual=filter.fitFilter(timeList,3000,2,order)
    #
    # print len(xa),len(timeList),len(residual)
    residualNormal=filter.normalByTime(timeList,residual,timeNormal)
    # residualSecUnit=filter.timeUnitConvert(residual,1000000000000)
    # fileToList.listToFileLong(residualSecUnit, timeFile[:-4] + '_%s_residual-0531-10-20000-ps.txt' % date)
    fileToList.listToFile(timeList,timeFile[:-4]+'_filtered.txt')
    # fig = plt.figure()
    # ax = fig.add_subplot(111)
    # ax.plot(xa, residual, color='g', linestyle='-', marker='')
    ax.plot(xa,ya,color='m',linestyle='',marker='.ux')
    # ax.legend()
    # plt.show()
#
def polyFitSegmentTest(date):
    order =2
    timeNormal=100000000000
    # timeFile = unicode('C:\Users\Levit\Experiment Data\德令哈测试\\20171226\零基线实验\\20171227015305-tdc2_4_filterN_coindence_filtered_250-350s.txt' , 'utf8')
    timeFile=unicode('C:\Users\Levit\Experiment Data\双站数据\\20180121\\result\\synCoincidence-124-216--17-1-Coin-紫台WGS84-atm-factor-haiji_laser改正_filtered.txt','utf8')
    timeList = fileToList.fileToList(timeFile)
    xa = []
    ya = []

    # for i in range(len(timeList)):
    #     xa.append(timeList[i][0]-timeList[i][4])
    #     # ya.append((timeList[i][0] - timeList[i][1]))
    #     ya.append([(timeList[i][2])/1000000000000.0])
    #
    xa,ya,timeList,fitList,residual=filter.fitFilter(timeList,2500/1000000000000.0,1,2)
    # fileToList.listToFile(timeList,timeFile[:-4] + '_filtered.txt')
    # xa,ya,fitList, residual = polyFitSegment(xa, ya, 1, 0.1)
    # xa, ya, filteredList, residual=filter.thresholdFilter(xa,ya,residual,timeList,0,0.000000002)
    xa,ya,fitList, residual = polyFitSegment(xa, ya, order,1000)
    # xa, ya, filteredList, residual = filter.thresholdFilter(xa, ya, residual, timeList, 0, 0.0000001)

    # residual=[]
    # for item in timeList:
    #     # residual.append([(item[0]-item[1])/1000000000000.0])
    #     residual.append([(item[2] ) / 1000000000000.0])
    print numpy.std(residual, ddof=1)
    xa,residual=filter.normalByTime(timeList,residual,timeNormal)

    fileToList.listToFileLong(residual, timeFile[:-4] + '_residual-%s-0.1s-ps.txt'%order)

    # fileToList.listToFile(filteredList,timeFile[:-4]+'_filtered.txt')
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    # ax2= fig.add_subplot(212)
    for i,item in enumerate(xa):
        xa[i]=item/1000000000000.0
        # fitList[i][0]=fitList[i][0]*1000000000000.0
        # ya[i]=[timeList[i][3]]
        residual[i][0]=residual[i][0]*1000000000000
        # print '%s\t%s'%(xa[i],residual[i][0])

    ax1.plot(xa,residual, color='g', linestyle='-', marker='*')
    # xa, ya = filter.normalByTime(timeList, ya, timeNormal)
    # ax1.plot(xa, ya, color='g', linestyle='-', marker='')
    ax1.xaxis.grid(True, which='major') #x坐标轴的网格使用主刻度
    ax1.yaxis.grid(True, which='major') #y坐标轴的网格使用次刻度show()
    ax1.set_ylabel('Difference(Residual after %s order fitting) (ps)'%order, fontsize=20)
    ax1.set_xlabel('Time (s)', fontsize=20)
    ax1.set_title('Time Compare', fontsize=24)
    # ax2.plot(xa,ya,color='m',linestyle='',marker='.')
    # ax2.plot(xa, fitList, color='g', linestyle='-', marker='')
    # ax.legend()
    plt.show()

    # fitSecList = filter.normalBySec(timeList, 1000000000000, 2, 0)
    # delayScan(timeList,0.00001,0.00001,0.02573,True)
    # delayScan(timeList, 0.00002, 0.00002, 0)

def Sine(y0,A,xc,w,x):
    return y0+A*math.sin(math.pi*(x-xc)/w)

def delayScan(timeList,step,scanRange,offset,plot):
    order=2
    order2=5
    time=1000000000000.0
    num=int(scanRange/step)
    for i in range(num):
        fitSecList=filter.normalBySec(timeList,time,order,i*step-scanRange/2+offset)
        x=[]
        d=[]
        for item in fitSecList:
            x.append(item[0])
            d.append(item[4])
        mat = numpy.polyfit(x, d, order2)
        Fx = numpy.poly1d(mat)
        residual = d-Fx(x)
        print i*step-scanRange/2+offset,numpy.std(residual, ddof=1)
        if plot:
            fig = plt.figure()
            ax = fig.add_subplot(121)
            ax2 = fig.add_subplot(122)
            ax.plot(x, d, color='g', linestyle='-', marker='*')
            ax2.plot(x, residual, color='r', linestyle='-', marker='*')
            ax.xaxis.grid(True, which='major')  # x坐标轴的网格使用主刻度
            ax.yaxis.grid(True, which='major')  # y坐标轴的网格使用次刻度show()
            ax.set_ylabel('Difference (ps)' , fontsize=20)
            ax.set_xlabel('Time (s)', fontsize=20)
            ax.set_title('Time Compare ,offset:%s'%(i*step-scanRange/2+offset), fontsize=20)
            ax2.xaxis.grid(True, which='major')  # x坐标轴的网格使用主刻度
            ax2.yaxis.grid(True, which='major')  # y坐标轴的网格使用次刻度show()
            ax2.set_ylabel('Residual  (ps)'  , fontsize=20)
            ax2.set_xlabel('Time (s)', fontsize=20)
            ax2.set_title('Residual after %s order fitting, offset:%s' % (order2,i * step - scanRange / 2 + offset), fontsize=20)
            plt.show()

# def delayScanTest(step,scanRange,offset):
#     dataFile=unicode('C:\Users\Levit\Experiment Data\双站数据\\20180108\\result\\符合时差与轨道延时差.txt' , 'utf8')
#     timeList=fileToList.fileToList(dataFile)
#     delayScan(timeList,step,scanRange,offset)

def sphere_point():
    pointFile=unicode('C:\Users\Levit\Experiment Data\望远镜相位中心测试\\丽江测试定点.txt','utf8')
    pointList=fileToList.fileToList(pointFile)
    X=[]
    Y=[]
    Z=[]
    count=4
    for i,point in enumerate(pointList):
        if i==count:
            break
        print point
        X.append(point[0])
        Y.append(point[1])
        Z.append(point[2])

    print X
    # P0=[-993546.7949,5617880.218,2849392.09,1.78]
    P0=[-993546.795 ,5617879.218 ,2849391.090,1.796 ]
    # P0=[-682620.013,	5030974.020, 	3852841.370 ,	1.087 ]
    minResi=1000
    minP0=[]
    for i in range(30):
        R=i*0.01+1.78-0.15
        detResi=1000
        P0[3]=R
        countX=0
        oldResi = 1000
        while detResi>0.05:
            countX+=1
            if countX==50:
                break

            result,order = leastsq(residual_fun,P0,args=(X,Y,Z))
            P0=result
            # print P0
            newResi=0
            for j in range(count):
                # print j,P0,X[j],Y[j],Z[j]
                # print sphere_fun(P0,X[j],Y[j],Z[j])
                # print (P0[0]-X[j])**2,(P0[1]-Y[j])**2,(P0[2]-Z[j])**2,P0[3]**2,P0[3]
                newResi+=residual_fun(P0,X[j],Y[j],Z[j])**2
            detResi=abs(oldResi-numpy.sqrt(newResi/count))
            oldResi=numpy.sqrt(newResi/count)
            print numpy.sqrt(newResi/count)

            print i,detResi
        # if residual<minResi:
        #     minResi=residual
        #     minP0=P0
        print R,P0,detResi
    # print result

def sphere_point_scan():
    pointFile=unicode('C:\Users\Levit\Experiment Data\望远镜相位中心测试\\丽江测试定点.txt','utf8')
    pointList=fileToList.fileToList(pointFile)
    X=[]
    Y=[]
    Z=[]
    count=4
    for i,point in enumerate(pointList):
        if i==count:
            break
        print point
        X.append(point[0])
        Y.append(point[1])
        Z.append(point[2])
    print X
    for xi in range(20):
        for yi in range(20):
            for zi in range(20):
                for ri in range(20):
                    # P0=[-993546.7949,5617880.218,2849392.09,2.8]
                    P0=[-993546.843-0.2+xi*0.02,	5617880.121-0.2+yi*0.02, 	2849392.069-0.2+zi*0.02 ,	1.796-0.2+ri*0.02]
                    result, order = leastsq(residual_fun, P0, args=(X, Y, Z))
                    newResi=0
                    for j in range(count):
                        # print j,P0,X[j],Y[j],Z[j]
                        # print sphere_fun(P0,X[j],Y[j],Z[j])
                        # print (P0[0]-X[j])**2,(P0[1]-Y[j])**2,(P0[2]-Z[j])**2,P0[3]**2,P0[3]
                        newResi += residual_fun(result, X[j], Y[j], Z[j]) ** 2
                    print result,numpy.sqrt(newResi / count)

if __name__=='__main__':
    polyFitSegmentTest('3.10')
    # polyFitTest()
    # delayScanTest(0.000001,0.000001,-0.000682)
    # sphere_point()
    # sphere_point_scan()