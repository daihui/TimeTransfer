#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'levitan'

import lagInterpolation
import matplotlib.pyplot as plt
import fileToList


def gpsLagInterFun(gpsTimeList, disList, startNo, Num, shift):  # gps距离list，插值秒数中点，前后各Num秒
    if startNo < Num:
        print startNo + 'Must >= ' + Num
    x = [float(gpsTimeList[i + startNo - Num][0]) / 1000000000000.0 for i in range(2 * Num + 1)]
    fx = [disList[i + startNo - Num + shift][0] for i in range(2 * Num + 1)]
    gpsfun = lagInterpolation.get_Lxfunc(x, fx)
    return gpsfun

def gpsLagInter(gpsTimeList1,gpsTimeList2,gpsDelList,interNum):
    N=len(gpsDelList)
    interGpsDel=[]
    for i in range(N-2):
        x = [i,i+1,i+2]
        fx = [gpsDelList[i][2],gpsDelList[i+1][2],gpsDelList[i+2][2]]
        gpsfun = lagInterpolation.get_Lxfunc(x, fx)
        for j in range(interNum):
            t1=gpsTimeList1[i][0]+1000000000000.0*j/interNum
            t2 = gpsTimeList2[i][0] + 1000000000000.0*j / interNum
            delay=gpsfun(i+float(j)/interNum)
            interGpsDel.append([t1,t2,delay])
    print 'gps delay have interpolation %s times'%interNum
    return interGpsDel

def gpsLagInterTest():
    gpsTimeList1 = fileToList.fileToList(
        unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\12.12\\send_fixed_GPSTime.txt', 'utf8'))
    gpsTimeList2 = fileToList.fileToList(
        unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\12.12\\recv_fixed_GPSTime.txt', 'utf8'))
    List2Delay = fileToList.fileToList(
        unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\12.12\\GPS_disDelay.txt', 'utf8'))
    file=unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\12.12\\result\GPS_disDelay_inter10.txt', 'utf8')
    gpsdelList=gpsLagInter(gpsTimeList1,gpsTimeList2,List2Delay,10)
    fileToList.listToFile(gpsdelList,file)

def gpsLagInterFunTest():
    gpsTimeFile = unicode('G:\\时频传输数据处理\\双站数据处理\\3.2\\DLH\\recv_fixed_GPSTime.txt', 'utf8')
    gpsDisFile = unicode('G:\\时频传输数据处理\\双站数据处理\\3.2\\DLH\\GPS_Recv.txt', 'utf8')
    gpsTimeList = []
    gpsDisList = []
    startNo = 7
    Num = 5
    with open(gpsTimeFile) as gpstime:
        for line in gpstime:
            gpsTimeList.append(float(line.strip()))
        print 'gps time list load finished!'
    with open(gpsDisFile) as gpsdis:
        for line in gpsdis:
            gpsDisList.append(float(line.strip()))
        print 'gps distance list load finished!'
    Lx = gpsLagInterFun(gpsTimeList, gpsDisList, startNo, Num)  # 获得插值函数
    tmp_x = [float(startNo + i / 10.0) for i in range(startNo, startNo + 100)]  # 测试用例
    tmp_y = [Lx(float(i)) for i in tmp_x]  # 根据插值函数获得测试用例的纵坐标
    print tmp_x, tmp_y
    print tmp_y
    x = [gpsTimeList[i] / 1000000000000.0 for i in range(startNo, startNo + 10)]
    y = [gpsDisList[i] for i in range(startNo, startNo + 10)]
    print x, y
    ''' 画图 '''
    plt.figure("play")
    ax1 = plt.subplot(111)
    plt.sca(ax1)
    plt.plot(x, y, linestyle=' ', marker='o', color='b')
    plt.plot(tmp_x, tmp_y, linestyle='--', color='r')
    plt.show()


if __name__ == '__main__':
    gpsLagInterFunTest()
