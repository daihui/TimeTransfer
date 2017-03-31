#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'levitan'

import gpsOrbit
import fileToList
from scipy import optimize
import numpy as np

def gpsDisDelay(dataFile2, gpsTimeFile1, gpsTimeFile2, gpsDisFile1, gpsDisFile2, startSec, endSec, shift):
    Num = 5
    Count = startSec
    gpsDisList1 = fileToList.fileToList(gpsDisFile1)
    gpsDisList2 = fileToList.fileToList(gpsDisFile2)
    gpsTimeList1 = fileToList.fileToList(gpsTimeFile1)
    gpsTimeList2 = fileToList.fileToList(gpsTimeFile2)
    gpsDelList = []
    s = dataFile2[:-4] + '_disDelay.txt'
    delayFile = open(s, 'w')
    with open(dataFile2) as datafile:
        for line in datafile:
            sec = float(line.strip()) / 1000000000000.0
            intSec = int(sec)
            print intSec
            if intSec < startSec:
                delayFile.write('0.0\n')
                gpsDelList.append(0.0)
            elif intSec < endSec:
                if intSec >= Count:
                    gpsDisFun1 = gpsOrbit.gpsLagInterFun(gpsTimeList1, gpsDisList1, intSec, Num, shift)
                    gpsDisFun2 = gpsOrbit.gpsLagInterFun(gpsTimeList2, gpsDisList2, intSec, Num, shift)
                    Count += 2
                    delayTime = 1000000000000.0 * (gpsDisFun2(sec) - gpsDisFun1(sec)) / 299792.458
                    gpsDelList.append(delayTime)
                    delayFile.write('%.3f\n' % delayTime)
                else:
                    delayTime = 1000000000000.0 * (gpsDisFun2(sec) - gpsDisFun1(sec)) / 299792.458
                    gpsDelList.append(delayTime)
                    delayFile.write('%.3f\n' % delayTime)
            elif intSec >= endSec:
                delayFile.flush()
                delayFile.close()
                break
    return gpsDelList


def gpsDisDelayEasyMode(gpsDisFile1, gpsDisFile2):
    gpsDisList1 = fileToList.fileToList(gpsDisFile1)
    gpsDisList2 = fileToList.fileToList(gpsDisFile2)
    gpsDelList = []
    s = gpsDisFile2[:-8] + 'disDelay.txt'
    delayFile = open(s, 'w')
    if len(gpsDisList1) < len(gpsDisList2):
        item = len(gpsDisList1)
    else:
        item = len(gpsDisList2)
    for i in range(item):
        t1 = 1000000000000.0 * gpsDisList1[i][0] / 299792.458
        t2 = 1000000000000.0 * gpsDisList2[i][0] / 299792.458
        gpsDelList.append([t1, t2, t1 - t2])
        delayFile.write(str(t1) + '\t' + str(t2) +'\t'+ str(t1 - t2) + '\n')
    print 'GPS distance delay have finished !'
    return gpsDelList


def delayOrbitFit(timeList, tau):
    lenght=len(timeList)
    count=0
    step=500
    X = np.zeros(step)
    Y = np.zeros(step)
    r=range(lenght/step)
    p=np.zeros((lenght/step+1,4))
    R = []

    def residuals(p):
        a, b, c, d= p
        return (Y - (a * X**3 + b * X **2+ c * X + d))**2


    # for i in range(step):
    #     #print item
    #     X[i]=timeList[i*step][0] / tau
    #     Y[i]=timeList[i*step][0] - timeList[i*step][1]
    #     # X[i]=i*1.0
    #     # Y[i]=2*i**3+i**2+3*i+5.0
    #
    # r = optimize.leastsq(residuals, [1.0, 1.0, 1.0, 1.0])
    # a, b, c, d = r[0]
    # print a, b, c, d

    for index in range(lenght):
        #count=0
        if int(index/step)==count:
            X[index%step]=timeList[index][0] / tau
            Y[index%step]=timeList[index][0] - timeList[index][1]
        else:
            r[count] = optimize.leastsq(residuals, [1.0, 1.0, 1.0, 1.0])
            p[count]= r[count][0]
            count+=1

    for index in range(lenght):
        #print index/step
        if index/step<lenght/step:
            x=timeList[index][0]/tau
            t=p[index/step][0] * x** 3 + p[index/step][1] *  x ** 2 + p[index/step][2] *  x + p[index/step][3]
            R.append([x,t])
            print timeList[index][0]-timeList[index][1]-t
    #print p

    # for i in range(100):
    #     t = a * X[i] ** 3 + b *  X[i] ** 2 + c *  X[i] + d
    #     R.append([ X[i], t, Y[i] - t])
    #     print  Y[i],'\t', t

    print 'the delay fit have finished !'
    return R


def timeCorrectByGpsTest(startSec, endSec, shift):
    datafile2 = unicode('G:\\时频传输数据处理\\双站数据处理\\3.2\\DLH\\recv_fixed_850Time.txt', 'utf8')
    gpsTimeFile1 = unicode('G:\\时频传输数据处理\\双站数据处理\\3.2\\LJ\\recv_fixed_GPSTime.txt', 'utf8')
    gpsTimeFile2 = unicode('G:\\时频传输数据处理\\双站数据处理\\3.2\\DLH\\recv_fixed_GPSTime.txt', 'utf8')
    gpsdisfile1 = unicode('G:\\时频传输数据处理\\双站数据处理\\3.2\\LJ\\GPS_Send.txt', 'utf8')
    gpsdisfile2 = unicode('G:\\时频传输数据处理\\双站数据处理\\3.2\\DLH\\GPS_Recv.txt', 'utf8')
    gpsDisDelay(datafile2, gpsTimeFile1, gpsTimeFile2, gpsdisfile1, gpsdisfile2, startSec, endSec, shift)


def gpsDisDelayEasyModeTest():
    gpsdisfile1 = unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\3.2\GPS_Send.txt', 'utf8')
    gpsdisfile2 = unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\3.2\GPS_Recv.txt', 'utf8')
    gpsDisDelayEasyMode(gpsdisfile1, gpsdisfile2)


def delayOrbitFitTest():
    timeFile = unicode('G:\时频传输数据处理\双站数据处理\\3.2\\result\\synCoincidenceEM_adjacentNear5.txt', 'utf8')
    timeList = fileToList.fileToList(timeFile)
    tau = 1000000000000
    delayOrbitFit(timeList, tau)
