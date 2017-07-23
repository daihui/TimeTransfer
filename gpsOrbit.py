#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'levitan'

import lagInterpolation
import matplotlib.pyplot as plt
import fileToList
import math


## 以时间为变量，距离延时列表为目标值，输入需求插值函数的时间点，采用前后各Num秒的数据来计算返回插值函数
def gpsLagInterFun(gpsTimeList1, gpsTimeList2, disDelayList, startNo, Num, shift, sec):
    if startNo < Num:
        print 'startNo should bigger than Num'
    x1 = [float(gpsTimeList1[i + startNo - Num][0] / sec) for i in range(2 * Num + 1)]
    fx1 = [float(disDelayList[i + startNo - Num + shift][0]) for i in range(2 * Num + 1)]
    x2 = [float(gpsTimeList2[i + startNo - Num][0] / sec) for i in range(2 * Num + 1)]
    fx2 = [float(disDelayList[i + startNo - Num + shift][1]) for i in range(2 * Num + 1)]
    # print x1,fx1
    delayX = [float(i + 1) for i in range(startNo - Num, startNo + Num + 1)]
    delayY = [float(disDelayList[i + startNo - Num + shift][2]) for i in range(2 * Num + 1)]
    delayfunc = lagInterpolation.get_Lxfunc(delayX, delayY)
    gpsfunc1 = lagInterpolation.get_Lxfunc(x1, fx1)
    gpsfunc2 = lagInterpolation.get_Lxfunc(x2, fx2)
    # print gpsfunc1(gpsTimeList1[startNo][0]/sec)
    # return gpsfunc1,gpsfunc2,delayfunc
    return gpsfunc1, gpsfunc2


##根据地面站置位J2000和卫星位置J2000坐标，插值计算距离延时
def delayCalJ2000(groundXYZList, satelliteXYZList, detTime, Num):
    delayList = []
    lenght = len(satelliteXYZList)
    for i in range(Num):
        distance1 = math.sqrt(
            (groundXYZList[i][1] - satelliteXYZList[i][1]) ** 2 + (groundXYZList[i][2] - satelliteXYZList[i][2]) ** 2 \
            + (groundXYZList[i][3] - satelliteXYZList[i][3]) ** 2)
        distance2 = math.sqrt(
            (groundXYZList[i][4] - satelliteXYZList[i][1]) ** 2 + (groundXYZList[i][5] - satelliteXYZList[i][2]) ** 2 \
            + (groundXYZList[i][6] - satelliteXYZList[i][3]) ** 2)
        delay1 = 1000000000000.0 * distance1 / 299792458
        delay2 = 1000000000000.0 * distance2 / 299792458
        delayList.append([delay1, delay2, delay1 - delay2])
        # print distance1,distance2
    for i in range(Num, lenght - Num):
        sec = [float(i + j - Num) for j in range(2 * Num + 1)]
        satelliteFx = [satelliteXYZList[i + j - Num][1] for j in range(2 * Num + 1)]
        satelliteFy = [satelliteXYZList[i + j - Num][2] for j in range(2 * Num + 1)]
        satelliteFz = [satelliteXYZList[i + j - Num][3] for j in range(2 * Num + 1)]
        satelliteFuncX = lagInterpolation.get_Lxfunc(sec, satelliteFx)
        satelliteFuncY = lagInterpolation.get_Lxfunc(sec, satelliteFy)
        satelliteFuncZ = lagInterpolation.get_Lxfunc(sec, satelliteFz)
        delay1 = 0.0
        delay2 = 0.0
        for ii in range(3):
            satelliteX1 = satelliteFuncX(i + detTime - delay1)
            satelliteY1 = satelliteFuncY(i + detTime - delay1)
            satelliteZ1 = satelliteFuncZ(i + detTime - delay1)
            satelliteX2 = satelliteFuncX(i + detTime - delay2)
            satelliteY2 = satelliteFuncY(i + detTime - delay2)
            satelliteZ2 = satelliteFuncZ(i + detTime - delay2)
            distance1 = math.sqrt(
                    (groundXYZList[i][1] - satelliteX1) ** 2 + (groundXYZList[i][2] - satelliteY1) ** 2 \
                    + (groundXYZList[i][3] - satelliteZ1) ** 2)
            distance2 = math.sqrt(
                    (groundXYZList[i][4] - satelliteX2) ** 2 + (groundXYZList[i][5] - satelliteY2) ** 2 \
                    + (groundXYZList[i][6] - satelliteZ2) ** 2)
            delay1 = distance1 / 299792458
            delay2 = distance2 / 299792458
            # print ii,delay1,delay2,distance1,distance2
        delayList.append([1000000000000.0 * delay1, 1000000000000.0 * delay2, 1000000000000.0 * (delay1 - delay2)])
        # print distance1,distance2
    return delayList


##根据地面站置位WGS84和卫星位置WGS84坐标，插值计算距离延时
def delayCalWGS84(groundXYZList, ground1, ground2, satelliteXYZList, detTime, Num):
    delayList = []
    lenght = len(satelliteXYZList)
    for i in range(Num):
        distance1 = math.sqrt((groundXYZList[ground1][1] - satelliteXYZList[i][1]) ** 2 + (
        groundXYZList[ground1][2] - satelliteXYZList[i][2]) ** 2 \
                              + (groundXYZList[ground1][3] - satelliteXYZList[i][3]) ** 2)
        distance2 = math.sqrt((groundXYZList[ground2][1] - satelliteXYZList[i][1]) ** 2 + (
        groundXYZList[ground2][2] - satelliteXYZList[i][2]) ** 2 \
                              + (groundXYZList[ground2][3] - satelliteXYZList[i][3]) ** 2)
        delay1 = 1000000000000.0 * distance1 / 299792458
        delay2 = 1000000000000.0 * distance2 / 299792458
        delayList.append([delay1, delay2, delay1 - delay2])
        # print distance1,distance2
    for i in range(Num, lenght - Num):
        sec = [float(i + j - Num) for j in range(2 * Num + 1)]
        satelliteFx = [satelliteXYZList[i + j - Num][1] for j in range(2 * Num + 1)]
        satelliteFy = [satelliteXYZList[i + j - Num][2] for j in range(2 * Num + 1)]
        satelliteFz = [satelliteXYZList[i + j - Num][3] for j in range(2 * Num + 1)]
        satelliteFuncX = lagInterpolation.get_Lxfunc(sec, satelliteFx)
        satelliteFuncY = lagInterpolation.get_Lxfunc(sec, satelliteFy)
        satelliteFuncZ = lagInterpolation.get_Lxfunc(sec, satelliteFz)
        delay1 = 0.0
        delay2 = 0.0
        for ii in range(3):
            satelliteX1 = satelliteFuncX(i + detTime - delay1)
            satelliteY1 = satelliteFuncY(i + detTime - delay1)
            satelliteZ1 = satelliteFuncZ(i + detTime - delay1)
            satelliteX2 = satelliteFuncX(i + detTime - delay2)
            satelliteY2 = satelliteFuncY(i + detTime - delay2)
            satelliteZ2 = satelliteFuncZ(i + detTime - delay2)
            distance1 = math.sqrt(
                    (groundXYZList[ground1][1] - satelliteX1) ** 2 + (groundXYZList[ground1][2] - satelliteY1) ** 2 \
                    + (groundXYZList[ground1][3] - satelliteZ1) ** 2)
            distance2 = math.sqrt(
                    (groundXYZList[ground2][1] - satelliteX2) ** 2 + (groundXYZList[ground2][2] - satelliteY2) ** 2 \
                    + (groundXYZList[ground2][3] - satelliteZ2) ** 2)
            delay1 = distance1 / 299792458
            delay2 = distance2 / 299792458
            #print delay1, delay2
        delayList.append([1000000000000.0 * delay1, 1000000000000.0 * delay2, 1000000000000.0 * (delay1 - delay2)])
        # print distance1,distance2
    return delayList


def gpsLagInter(gpsTimeList1, gpsTimeList2, gpsDelList, interNum):
    N = len(gpsDelList)
    interGpsDel = []
    for i in range(N - 2):
        x = [i, i + 1, i + 2]
        fx = [gpsDelList[i][2], gpsDelList[i + 1][2], gpsDelList[i + 2][2]]
        gpsfun = lagInterpolation.get_Lxfunc(x, fx)
        for j in range(interNum):
            t1 = gpsTimeList1[i][0] + 1000000000000.0 * j / interNum
            t2 = gpsTimeList2[i][0] + 1000000000000.0 * j / interNum
            delay = gpsfun(i + float(j) / interNum)
            interGpsDel.append([t1, t2, delay])
    print 'gps delay have interpolation %s times' % interNum
    return interGpsDel


def gpsLagInterTest():
    date = '12.12'
    gpsTimeList1 = fileToList.fileToList(
            unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\send_fixed_GPSTime.txt' % date, 'utf8'))
    gpsTimeList2 = fileToList.fileToList(
            unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\recv_fixed_GPSTime.txt' % date, 'utf8'))
    List2Delay = fileToList.fileToList(
            unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\GPS_disDelay.txt' % date, 'utf8'))
    file = unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\result\GPS_disDelay_inter1.txt' % date, 'utf8')
    gpsdelList = gpsLagInter(gpsTimeList1, gpsTimeList2, List2Delay, 1)
    fileToList.listToFile(gpsdelList, file)


def gpsLagInterFunTest():
    gpsTimeList1 = fileToList.fileToList(
            unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\3.2\\send_fixed_GPSTime.txt', 'utf8'))
    gpsTimeList2 = fileToList.fileToList(
        unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\3.2\\recv_fixed_GPSTime.txt', 'utf8'))
    gpsDisList = fileToList.fileToList(
        unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\3.2\\GPS_Recv_Precise_disDelay.txt', 'utf8'))
    startNo = 7
    Num = 5
    tmp_x = []
    tmp_y = []
    x = []
    y = []
    for sec in range(100):
        Lx1, Lx2 = gpsLagInterFun(gpsTimeList1, gpsTimeList2, gpsDisList, startNo + sec, Num, 0)  # 获得插值函数
        tmp_x += [float(startNo + sec + i / 10.0) * 1000000000000 for i in range(10)]  # 测试用例
        tmp_y += [Lx1(float(startNo + sec + i / 10.0) * 1000000000000) for i in range(10)]  # 根据插值函数获得测试用例的纵坐标
        x += [gpsTimeList1[startNo + sec][0]]
        y += [gpsDisList[startNo + sec][0]]
    ''' 画图 '''
    plt.figure("play")
    ax1 = plt.subplot(111)
    plt.sca(ax1)
    plt.plot(x, y, linestyle=' ', marker='o', color='b')
    plt.plot(tmp_x, tmp_y, linestyle='--', color='r')
    plt.show()


def delayCalJ2000Test():
    groundXYZList = fileToList.fileToList(
            unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\3.2\\groundStationJ2000_Sec.txt', 'utf8'))
    satelliteXYZList = fileToList.fileToList(
            unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\3.2\\satelliteJ2000_Sec.txt', 'utf8'))
    delayCal(groundXYZList, satelliteXYZList, 2, 5)


def delayCalWGS84Test():
    groundXYZList = fileToList.fileToList(
            unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\3.2\\groundStationWGS84.txt', 'utf8'))
    satelliteXYZList = fileToList.fileToList(
            unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\3.2\\satelliteWGS84_Sec.txt', 'utf8'))
    delayCalWGS84(groundXYZList, 0, 1, satelliteXYZList, 0, 5)


if __name__ == '__main__':
    # gpsLagInterFunTest()
    delayCalWGS84Test()
