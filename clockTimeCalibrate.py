#!/usr/bin/env python
#-*- coding: utf-8 -*-
__author__ = 'levitan'

import fileToList

def clockTimeFactor(timeList):
    N=len(timeList)-1
    print N
    factor=(timeList[N][0]-timeList[0][0])/(N*1000000000000.0000)
    print 'time factor is '+str(factor)
    return factor

def timeCalibrate(timeList,factor):
    for item in timeList:
        item[0]=item[0]/factor
    print 'time calibrate finished !'
    return timeList


