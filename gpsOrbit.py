#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'levitan'

import lagInterpolation
import matplotlib.pyplot as plt
import fileToList


def gpsLagInterFun(gpsTimeList1,gpsTimeList2, disDelayList, startNo, Num, shift,sec):  # gps距离list，插值秒数中点，前后各Num秒
    if startNo < Num:
        print 'startNo should bigger than Num'
    x1 = [float(gpsTimeList1[i + startNo - Num][0]/sec)  for i in range(2 * Num + 1)]
    fx1 = [float(disDelayList[i + startNo - Num + shift][0]) for i in range(2 * Num + 1)]
    x2 = [float(gpsTimeList2[i + startNo - Num][0]/sec)  for i in range(2 * Num + 1)]
    fx2 = [float(disDelayList[i + startNo - Num + shift][1]) for i in range(2 * Num + 1)]
    #print x1,fx1
    delayX= [float(i+1)  for i in range(startNo-Num,startNo+Num+1)]
    delayY = [float(disDelayList[i + startNo - Num + shift][2]) for i in range(2 * Num + 1)]
    delayfunc=lagInterpolation.get_Lxfunc(delayX,delayY)
    gpsfunc1 = lagInterpolation.get_Lxfunc(x1, fx1)
    gpsfunc2 = lagInterpolation.get_Lxfunc(x2, fx2)
    #print gpsfunc1(gpsTimeList1[startNo][0]/sec)
    return gpsfunc1,gpsfunc2,delayfunc

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
    date='12.12'
    gpsTimeList1 = fileToList.fileToList(
        unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\send_fixed_GPSTime.txt'%date, 'utf8'))
    gpsTimeList2 = fileToList.fileToList(
        unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\recv_fixed_GPSTime.txt'%date, 'utf8'))
    List2Delay = fileToList.fileToList(
        unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\GPS_disDelay.txt'%date, 'utf8'))
    file=unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\result\GPS_disDelay_inter1.txt'%date, 'utf8')
    gpsdelList=gpsLagInter(gpsTimeList1,gpsTimeList2,List2Delay,1)
    fileToList.listToFile(gpsdelList,file)

def gpsLagInterFunTest():
    gpsTimeList1 = fileToList.fileToList(
        unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\3.2\\send_fixed_GPSTime.txt', 'utf8'))
    gpsTimeList2 = fileToList.fileToList(unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\3.2\\recv_fixed_GPSTime.txt', 'utf8'))
    gpsDisList =fileToList.fileToList(unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\3.2\\GPS_Recv_Precise_disDelay.txt', 'utf8'))
    startNo = 7
    Num = 5
    tmp_x=[]
    tmp_y=[]
    x=[]
    y=[]
    for sec in range(100):
        Lx1,Lx2 = gpsLagInterFun(gpsTimeList1,gpsTimeList2, gpsDisList, startNo+sec, Num,0)  # 获得插值函数
        tmp_x += [float(startNo +sec+ i / 10.0)*1000000000000 for i in range(10)]  # 测试用例
        tmp_y += [Lx1(float(startNo +sec+ i / 10.0)*1000000000000) for i in range(10)]  # 根据插值函数获得测试用例的纵坐标
        x += [gpsTimeList1[startNo+sec][0] ]
        y += [gpsDisList[startNo+sec][0]]
    ''' 画图 '''
    plt.figure("play")
    ax1 = plt.subplot(111)
    plt.sca(ax1)
    plt.plot(x, y, linestyle=' ', marker='o', color='b')
    plt.plot(tmp_x, tmp_y, linestyle='--', color='r')
    plt.show()


if __name__ == '__main__':
    gpsLagInterFunTest()
