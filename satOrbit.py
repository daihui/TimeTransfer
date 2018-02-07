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
import timeDataCoincidence
import gpsOrbit
import clockTimeCalibrate

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
def disUncertain(X,groStation,satellite,staCount,sec):
    distance=0
    delay=0
    for i in range(staCount):
        newSatellite=[satellite[1]+X[0]*random.uniform(-1,1),satellite[2]+X[1]*random.uniform(-1,1),satellite[3]+X[2]*random.uniform(-1,1)]
        distance= math.sqrt((newSatellite[0]-satellite[1])**2+(newSatellite[1]-satellite[2])**2+(newSatellite[2]-satellite[3])**2)
        newdistance1=math.sqrt((newSatellite[0]-groStation[0][1])**2+(newSatellite[1]-groStation[0][2])**2+(newSatellite[2]-groStation[0][3])**2)
        newdistance2 = math.sqrt((newSatellite[0] - groStation[1][1]) ** 2 + (newSatellite[1] - groStation[1][2]) ** 2 + (
        newSatellite[2] - groStation[1][2]) ** 2)
        olddistance1 = math.sqrt((satellite[1] - groStation[0][1]) ** 2 + (satellite[2] - groStation[0][2]) ** 2 + (
            satellite[3]  - groStation[0][3]) ** 2)
        olddistance2 = math.sqrt((satellite[1] - groStation[1][1]) ** 2 + (satellite[2] - groStation[1][2]) ** 2 + (
            satellite[3]  - groStation[1][2]) ** 2)
        delay= 1000000000000.0 * ((newdistance1-olddistance1) - (newdistance2-olddistance2)) / 299792458
        # delay=((newdistance1-olddistance1) - (newdistance2-olddistance2))
        print '%s\t%s\t%s\t%s\t%s'%(sec,distance,(newdistance1-olddistance1),(newdistance2-olddistance2),delay)
    #print '%s\t%s'%(distance/staCount,delay/staCount)

def disUncertainTest(X,staCount):
    goundFile = unicode('C:\Users\Levit\Experiment Data\双站数据\\20180109\\groundStationWGS84.txt', 'utf8')
    satFile = unicode('C:\Users\Levit\Experiment Data\双站数据\\20180109\\satelliteWGS84_Sec.txt', 'utf8')
    goundList = fileToList.fileToList(goundFile)
    satList=fileToList.fileToList(satFile)
    length=len(satList)
    for i in range(250):
        disUncertain(X,goundList,satList[i],staCount,i)

def J2000_Select():
    dataFile=unicode('C:\Users\Levit\Experiment Data\双站数据\\20180109\\FTP星历J2000.txt', 'utf8')
    GPSFile=unicode('C:\Users\Levit\Experiment Data\双站数据\\20180109\\KX02_1C_ED_044D_20180109T000000_0055_003_000.txt', 'utf8')
    dataList= fileToList.fileToList(dataFile)
    GPSList=fileToList.fileToList(GPSFile)
    saveFile=dataFile[:-4]+'_coin.txt'
    indexd=0
    lend=len(dataList)
    coinList=[]
    for item in GPSList:
        Find = False
        timeG=item[0]*3600+item[1]*60+item[2]-2
        while not Find:
            if indexd<lend-1:
                timeD=dataList[indexd][3]*3600+dataList[indexd][4]*60+dataList[indexd][5]
                if timeG>timeD:
                    indexd+=1
                elif timeG==timeD:
                    new=[timeG]+item+dataList[indexd]+[dataList[indexd][6]-item[4]*1000,dataList[indexd][7]-item[5]*1000,dataList[indexd][8]-item[6]*1000]
                    print [dataList[indexd][6],item[4]*1000,dataList[indexd][7],item[5]*1000,dataList[indexd][8],item[6]*1000]
                    coinList.append(new)
                    Find=True
                else:
                    break
            else:
                break
    fileToList.listToFile(coinList,saveFile)

def sat_move(satList,move):
    moveList=[]
    for item in satList:
        moveList.append([item[0],item[1]+move[0],item[2]+move[1],item[3]+move[2]])
    return moveList

def ground_move(groundList,move):
    moveList=[]
    moveList.append([groundList[0][0],groundList[0][1]+move[0],groundList[0][2]+move[1],groundList[0][3]+move[2]])
    moveList.append([groundList[1][0],groundList[1][1] + move[3], groundList[1][2] + move[4], groundList[1][3] + move[5]])
    # print moveList
    # print groundList
    return moveList

def dataReduce(dataList,factor):
    reduceList1=[]
    reduceList2 = []
    index=0
    for i in range(len(dataList)):
        if index==factor:
            reduceList1.append([dataList[i][0]])
            reduceList2.append([dataList[i][1]])
            index=0
        else:
            index+=1
    print len(reduceList1)
    return reduceList1,reduceList2


def satMoveSimulation(List1,List2,groundXYZList,satelliteXYZList,atmosphereList,gpsTimeList1,newgpsTimeList2,info):
    [date,  startSec, endSec, gpsShift,move]=info
    List2Delay = gpsOrbit.delayCalWGS84(groundXYZList, 0, 1, satelliteXYZList, 0, 5, atmosphereList)
    coinfile = unicode(
            'C:\Users\Levit\Experiment Data\双站数据\\%s\\result\\satellite_move-%s-%s-%s-Coin.txt' % (
                date,move[0], move[1], move[2] ), 'utf8')
    coindenceList,std = timeDataCoincidence.timeCoincidence(List1, List2, List2Delay, gpsTimeList1, newgpsTimeList2, startSec, endSec,
                                        gpsShift , coinfile)
    del coindenceList
    return std


def satMoveScan():
    step=[1,1,1]
    scanRange=[1,1,1]
    offset=[10,-12,-20]
    date = '20180109'
    dataLJ = '20180110012855'
    dataDLH = '20180110012854'
    startSec = 137
    endSec = 230
    gpsShift = -22
    tdcShift = 1
    groundXYZList = fileToList.fileToList(
        unicode('C:\Users\Levit\Experiment Data\双站数据\\3.10\\groundStationWGS84.txt', 'utf8'))
    satelliteXYZList = fileToList.fileToList(
        unicode('C:\Users\Levit\Experiment Data\双站数据\\%s\\satelliteWGS84_Sec_new.txt' % date, 'utf8'))
    atmosphereList = fileToList.fileToList(
        unicode('C:\Users\Levit\Experiment Data\双站数据\\%s\\天气参数.txt' % date, 'utf8'))
    gpsTimeList1 = fileToList.fileToList(
        unicode('C:\Users\Levit\Experiment Data\双站数据\\%s\共视数据\\%s-tdc2_channel_1.txt' % (date, dataLJ), 'utf8'))
    gpsTimeList2 = fileToList.fileToList(
        unicode('C:\Users\Levit\Experiment Data\双站数据\\%s\共视数据\\%s-tdc13_channel_1.txt' % (date, dataDLH), 'utf8'))
    dataList = fileToList.fileToList(unicode(
        'C:\Users\Levit\Experiment Data\双站数据\\%s\\result\\synCoincidence-137-240--21-1-Coin-紫台WGS84-atm-factor-neworbit-0120_filtered.txt' % (
        date), 'utf8'))
    List1,List2=dataReduce(dataList,100)
    newgpsTimeList2 = []
    if tdcShift >= 0:
        for i in range(tdcShift):
            newgpsTimeList2.append([gpsTimeList2[i][0]])
        for i in range(len(gpsTimeList2)):
            newgpsTimeList2.append([gpsTimeList2[i][0] + tdcShift * 1000000000000])
    else:
        for i in range(len(gpsTimeList2)):
            gpsTime = gpsTimeList2[i][0] + tdcShift * 1000000000000
            if gpsTime > 0:
                newgpsTimeList2.append([gpsTime])

    timeFactor1, offset1 = clockTimeCalibrate.clockTimeFactorFit(gpsTimeList1)
    timeFactor2, offset2 = clockTimeCalibrate.clockTimeFactorFit(newgpsTimeList2)
    gpsTimeList1 = clockTimeCalibrate.timeCalibrate(gpsTimeList1, timeFactor1, offset1)
    newgpsTimeList2 = clockTimeCalibrate.timeCalibrate(newgpsTimeList2, timeFactor2, offset2)

    for i in range(scanRange[0]/step[0]):
        for j in range(scanRange[1]/step[1]):
            for k in range(scanRange[2]/step[2]):
                move=[i*step[0]-scanRange[0]/2+offset[0],j*step[1]-scanRange[1]/2+offset[1],k*step[2]-scanRange[2]/2+offset[2]]
                info=[date,  startSec, endSec, gpsShift,move]
                satelliteXYZListMove = sat_move(satelliteXYZList, move)
                std=satMoveSimulation(List1,List2,groundXYZList,satelliteXYZListMove,atmosphereList,gpsTimeList1,newgpsTimeList2,info)
                [x,y,z]=move
                print '%s\t%s\t%s\t%s'%(x,y,z,std)

def groundMoveScan():
    # step=[3,3,3,2,2,2]
    # scanRange=[9,9,9,4,4,6]
    step = [1, 1, 1, 1, 1, 1]
    scanRange = [1, 1, 1, 1, 1, 1]
    offset=[-29,-32,15,-26,-42,9]
    date = '20180121'
    dataLJ = '20180122014609'
    dataDLH = '20180122014608'
    startSec = 120
    endSec = 215
    gpsShift = -17
    tdcShift = 1
    groundXYZList = fileToList.fileToList(
        unicode('C:\Users\Levit\Experiment Data\双站数据\\3.10\\groundStationWGS84.txt', 'utf8'))
    satelliteXYZList = fileToList.fileToList(
        unicode('C:\Users\Levit\Experiment Data\双站数据\\%s\\satelliteWGS84_Sec.txt' % date, 'utf8'))
    atmosphereList = fileToList.fileToList(
        unicode('C:\Users\Levit\Experiment Data\双站数据\\%s\\天气参数.txt' % date, 'utf8'))
    gpsTimeList1 = fileToList.fileToList(
        unicode('C:\Users\Levit\Experiment Data\双站数据\\%s\共视数据\\%s-tdc2_channel_1.txt' % (date, dataLJ), 'utf8'))
    gpsTimeList2 = fileToList.fileToList(
        unicode('C:\Users\Levit\Experiment Data\双站数据\\%s\共视数据\\%s-tdc13_channel_1.txt' % (date, dataDLH), 'utf8'))
    dataList = fileToList.fileToList(unicode(
        'C:\Users\Levit\Experiment Data\双站数据\\%s\\result\\synCoincidence-120-220--16-1-Coin-紫台WGS84-atm-factor_filtered.txt' % (
        date), 'utf8'))
    List1,List2=dataReduce(dataList,100)
    newgpsTimeList2 = []
    if tdcShift >= 0:
        for i in range(tdcShift):
            newgpsTimeList2.append([gpsTimeList2[i][0]])
        for i in range(len(gpsTimeList2)):
            newgpsTimeList2.append([gpsTimeList2[i][0] + tdcShift * 1000000000000])
    else:
        for i in range(len(gpsTimeList2)):
            gpsTime = gpsTimeList2[i][0] + tdcShift * 1000000000000
            if gpsTime > 0:
                newgpsTimeList2.append([gpsTime])

    timeFactor1, offset1 = clockTimeCalibrate.clockTimeFactorFit(gpsTimeList1)
    timeFactor2, offset2 = clockTimeCalibrate.clockTimeFactorFit(newgpsTimeList2)
    gpsTimeList1 = clockTimeCalibrate.timeCalibrate(gpsTimeList1, timeFactor1, offset1)
    newgpsTimeList2 = clockTimeCalibrate.timeCalibrate(newgpsTimeList2, timeFactor2, offset2)
    minSTD=100000000
    for i in range(scanRange[0]/step[0]):
        for j in range(scanRange[1]/step[1]):
            for k in range(scanRange[2]/step[2]):
                for ii in range(scanRange[3]/step[3]):
                    for jj in range(scanRange[4]/step[4]):
                        for kk in range(scanRange[5]/step[5]):
                            move=[i*step[0]-scanRange[0]/2+offset[0],j*step[1]-scanRange[1]/2+offset[1],k*step[2]-scanRange[2]/2+offset[2],
                                  ii * step[3] - scanRange[3] / 2 + offset[3], jj * step[4] - scanRange[4] / 2 + offset[4], kk * step[5] - scanRange[5] / 2 + offset[5]]
                            info=[date,  startSec, endSec, gpsShift,move]
                            groundXYZListMove = ground_move(groundXYZList,move)
                            std=satMoveSimulation(List1,List2,groundXYZListMove,satelliteXYZList,atmosphereList,gpsTimeList1,newgpsTimeList2,info)
                            [x1, y1, z1, x2, y2, z2] = move
                            print '%s\t%s\t%s\t%s\t%s\t%s\t%s'%(x1,y1,z1,x2,y2,z2,std)
                            if std<minSTD:
                                minSTD=std
                                minMove=move
    print 'best move: %s, std: %s'%(minMove,minSTD)


if __name__=='__main__':
    # distanceTest()
    # groundSecTest()
    # J2000_Select()
    # disUncertainTest([10,10,10], 80)
    # satMoveScan()
    groundMoveScan()