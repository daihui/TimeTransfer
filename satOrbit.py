#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  根据星历提供的卫星轨道坐标信息计算星地之间的距离

__author__ = 'levitan'

import fileToList
import lagInterpolation
import numpy as np
import datetime
import jdutil
import math
import random


def satOrbSec(satFile, startTime, Num, shfit):
    if Num < shfit:
        print ' shfit must > Num'
    savefile = satFile[:-4] + '_Sec.txt'
    sec = 400
    satList = fileToList.fileToList(satFile)
    J = len(satList[0])
    silde = []
    satSecList = []
    for i in range(sec):
        moveOne = i / 16
        silde.append(i)
        print i, moveOne
        for j in range(1, J):
            satFun = satLagInterFun(satList, Num, j, shfit + moveOne)
            silde.append(satFun(startTime + i))
        satSecList.append(silde[i * (J):])
    fileToList.listToFile(satSecList, savefile)
    print 'satellte position interpolation calculate by second !'
    return satSecList

def groundStationSec(groundList, startTime, passSec, interNum):
    year, month, day, hour, minute, sec = startTime
    jd = jdutil.date_to_jd(year, month, day)
    mjd = jdutil.jd_to_mjd(jd)
    print jd,mjd
    J = len(groundList[0])
    silde = []
    groundSecList = []
    groundfun = range(J)
    index = 0
    found = False
    while not found:
        if int(groundList[index][0]) == int(mjd):
            found = True
        else:
            index += 1
    for j in range(1, J):
        x = [float(groundList[index + i - interNum][0]) for i in range(2 * interNum + 1)]
        fx = [groundList[index + ii - interNum][j] for ii in range(2 * interNum + 1)]
        groundfun[j] = lagInterpolation.get_Lxfunc(x, fx)
    for i in range(passSec):
        time = mjd + hour / 24. + minute / (24 * 60.) + (sec + i) / (24 * 60 * 60.)
        silde.append(i)
        for j in range(1, J):
            silde.append(groundfun[j](time))
        groundSecList.append(silde[i * J:])
    print 'ground station position interpolation calculated by second !'
    return groundSecList


def groSatDistance(groundList, satList):
    distanceList = []
    for i, groundItem in enumerate(groundList):
        distance1 = math.sqrt((groundItem[1] - satList[i][1] * 1000) ** 2 + (groundItem[2] - satList[i][2] * 1000) ** 2 \
                              + (groundItem[3] - satList[i][3] * 1000) ** 2)
        distance2 = math.sqrt((groundItem[4] - satList[i][1] * 1000) ** 2 + (groundItem[5] - satList[i][2] * 1000) ** 2 \
                              + (groundItem[6] - satList[i][3] * 1000) ** 2)
        delay = 1000000000000.0 * (distance2 - distance1) / 299792458
        distanceList.append([distance1, distance2, delay])
        print distance1,distance2,groundItem,satList[i]
    print 'distance between ground station 1,2 to satellte are calculated !'
    return distanceList


def satLagInterFun(satList, Num, j, shift):
    # x = [float(satList[i - Num + shift][0]/1000000.0+satList[i - Num + shift][1]) for i in range(2 * Num + 1)]
    x = [float( satList[i - Num + shift][0]) for i in range(2 * Num + 1)]
    fx = [satList[i - Num + shift][j] for i in range(2 * Num + 1)]
    satfun = lagInterpolation.get_Lxfunc(x, fx)
    return satfun


def satOrbSecTest():
    satFile = unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\3.2\\卫星过境实测坐标J2000.txt', 'utf8')
    satOrbSec(satFile, 163127535, 4, 8)


def groundSecTest():
    goundFile = unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\3.2\Result\\groundStationJ2000.txt', 'utf8')
    goundList = fileToList.fileToList(goundFile)
    startTime = (2017, 3, 2, 17, 12, 15)
    groundSecList = groundStationSec(goundList, startTime, 400, 2)
    saveFile = goundFile[:-4] + '_Sec-0717.txt'
    fileToList.listToFile(groundSecList, saveFile)

def distanceTest():
    goundFile = unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\3.2\Result\\groundStationJ2000-0717.txt', 'utf8')
    satFile = unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\3.2\Result\\satellite_Sec.txt', 'utf8')
    goundList = fileToList.fileToList(goundFile)
    satList=fileToList.fileToList(satFile)
    groSatDistance(goundList,satList)


#模拟计算定轨精度为X下，两地延时的误差范围
def disUncertain(X,groStation,satellite,staCount):
    distance=0
    delay=0
    for i in range(staCount):
        newSatellite=[satellite[1]*1000+0*random.uniform(-1,1),satellite[2]*1000+0*random.uniform(-1,1),satellite[3]*1000+X*random.uniform(-1,1)]
        distance= math.sqrt((newSatellite[0]-satellite[1]*1000)**2+(newSatellite[1]-satellite[2]*1000)**2+(newSatellite[2]-satellite[3]*1000)**2)
        newdistance1=math.sqrt((newSatellite[0]-groStation[1])**2+(newSatellite[1]-groStation[2])**2+(newSatellite[2]-groStation[3])**2)
        newdistance2 = math.sqrt((newSatellite[0] - groStation[4]) ** 2 + (newSatellite[1] - groStation[5]) ** 2 + (
        newSatellite[2] - groStation[6]) ** 2)
        olddistance1 = math.sqrt((satellite[1]*1000 - groStation[1]) ** 2 + (satellite[2]*1000 - groStation[2]) ** 2 + (
            satellite[3] * 1000 - groStation[3]) ** 2)
        olddistance2 = math.sqrt((satellite[1]*1000 - groStation[4]) ** 2 + (satellite[2]*1000 - groStation[5]) ** 2 + (
            satellite[3] * 1000 - groStation[6]) ** 2)
        delay= 1000000000000.0 * ((newdistance1-olddistance1) - (newdistance2-olddistance2)) / 299792458
        print '%s\t%s\t%s\t%s'%(distance,(newdistance1-olddistance1),(newdistance2-olddistance2),delay)
    #print '%s\t%s'%(distance/staCount,delay/staCount)

def disUncertainTest(X,staCount,i):
    goundFile = unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\3.2\Result\\groundStationJ2000_Sec.txt', 'utf8')
    satFile = unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\3.2\Result\\satellite_Sec.txt', 'utf8')
    goundList = fileToList.fileToList(goundFile)
    satList=fileToList.fileToList(satFile)
    #length=len(goundList)
    #for i in range(length):
    disUncertain(X,goundList[i],satList[i],staCount)

if __name__=='__main__':
    # distanceTest()
    groundSecTest()