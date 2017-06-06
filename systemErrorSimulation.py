#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'levitan'

import random
import matplotlib.pyplot as plt
import math
import filter
import fileToList

def sineError(samplingRate,period,amplitude,dataLenght,sigma):
    x=[float(i)/samplingRate for i in range(dataLenght)]
    sineY=[amplitude*math.sin(2*math.pi*i/(period)) for i in x]
    sineNormalError=[i+random.normalvariate(i,sigma) for i in sineY]

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(x, sineNormalError, color='g', linestyle='-', marker='.')
    plt.show()
    return sineNormalError


if __name__=='__main__':
    errorList=sineError(2000,0.1,100,200,10)
    # errorListCovert=[[item] for item in errorList]
    # errorListPSec=filter.timeUnitConvert(errorListCovert,1000000000000)
    # fileName=unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\3.2\\Result\\sineError-100s.txt' , 'utf8')
    #
    # fileToList.listToFileLong(errorListPSec,fileName)