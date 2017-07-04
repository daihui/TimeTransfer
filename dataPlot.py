#!/usr/bin/env python
#-*- coding: utf-8 -*-
__author__ = 'levitan'

# 数据分析画图

import matplotlib.pyplot as plt
import fileToList

def logPlotAx(List,fig,c,l,m,lab):
    x=[]
    y=[]
    for item in List:
        x.append(item[0])
        y.append(item[1])
    ax=fig.add_subplot(111)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim((0.0001,100))
    ax.set_ylim((1E-13,1E-9))
    ax.plot(x,y,color=c, linestyle=l, marker=m, label=lab)
    ax.xaxis.grid(True, which='minor') #x坐标轴的网格使用主刻度
    ax.yaxis.grid(True, which='minor') #y坐标轴的网格使用次刻度show()
    ax.xaxis.grid(True, which='major') #x坐标轴的网格使用主刻度
    ax.yaxis.grid(True, which='major') #y坐标轴的网格使用次刻度show()
    ax.set_ylabel('TDEV (s)')
    ax.set_xlabel('Averaging Time (s)')
    ax.set_title('Stability Comparison')
    ax.legend()

def logPlotAxTest():
    dataFile1=unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\6.27NS\\6.27NS-1900-2080-nofit.txt','utf8')
    dataFile2=unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\6.27NS\\6.27NS-2-3-1pulse-1900-2060-nofit.txt','utf8')
    dataFile3=unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\6.27NS\\6.27NS-2-3-2pulse-1-1900-2060-nofit.txt','utf8')
    dataFile4=unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\6.27NS\\6.27NS-2-3-2pulse-2-1900-2060-nofit.txt','utf8')
    # dataFile5=unicode('E:\Experiment Data\时频传输数据处理\本地光路系统测试\\6.13\\tdc-5k-100s-nofit.txt','utf8')

    List1=fileToList.fileToList(dataFile1)
    List2=fileToList.fileToList(dataFile2)
    List3=fileToList.fileToList(dataFile3)
    List4=fileToList.fileToList(dataFile4)
    # List5=fileToList.fileToList(dataFile5)
    fig=plt.figure()
    logPlotAx(List1,fig,'g','--','o','6.27NS 0-1')
    logPlotAx(List2,fig,'r','--','s','6.27NS 2-3-onepulse')
    logPlotAx(List3,fig,'y','--','v','6.27NS 2-3-twopulse-1')
    logPlotAx(List4,fig,'c','--','^','6.27NS 2-3-twopulse-2')
    # logPlotAx(List5,fig,'b','--','v','one TDC')

    plt.show()

if __name__=='__main__':
    logPlotAxTest()