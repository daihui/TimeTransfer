#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  根据星历提供的卫星轨道坐标信息计算星地之间的距离

__author__ = 'levitan'

import fileToList
import lagInterpolation
import numpy as np


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
        satSecList.append(silde[i * J:])
    print satSecList
    fileToList.listToFile(satSecList, savefile)
    print 'satellte position interpolation calculate by second !'
    return satSecList


def satLagInterFun(satList, Num, j, shift):
    x = [float(satList[i - Num + shift][0]) for i in range(2 * Num + 1)]
    fx = [satList[i - Num + shift][j] for i in range(2 * Num + 1)]
    satfun = lagInterpolation.get_Lxfunc(x, fx)
    return satfun


def satOrbSecTest():
    satFile = unicode('G:\时频传输数据处理\双站数据处理\\3.2\\satellite.txt', 'utf8')
    satOrbSec(satFile, 163127533, 4, 7)
