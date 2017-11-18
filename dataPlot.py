#!/usr/bin/env python
#-*- coding: utf-8 -*-
__author__ = 'levitan'

# 数据分析画图

import matplotlib.pyplot as plt
import fileToList

# plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
# plt.rcParams['axes.unicode_minus']=False #用来正常显示负号

def logPlotAx(List,fig,c,l,m,lab):
    x=[]
    y=[]
    for item in List:
        x.append(item[0])
        y.append(item[1])
    ax=fig.add_subplot(111)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim((0.005,120))
    ax.set_ylim((1E-13,5E-8))
    ax.plot(x,y,color=c, linestyle=l, marker=m, label=lab)
    ax.xaxis.grid(True, which='minor') #x坐标轴的网格使用主刻度
    ax.yaxis.grid(True, which='minor') #y坐标轴的网格使用次刻度show()
    ax.xaxis.grid(True, which='major') #x坐标轴的网格使用主刻度
    ax.yaxis.grid(True, which='major') #y坐标轴的网格使用次刻度show()
    ax.set_ylabel('TDEV (s)',fontsize=16)
    ax.set_xlabel('Averaging Time (s)',fontsize=16)
    ax.set_title('Stability',fontsize=20)
    # ax.legend()
    plt.legend(loc=0, numpoints=1)
    leg = plt.gca().get_legend()
    ltext = leg.get_texts()
    plt.setp(ltext, fontsize='large')

def logPlotAxTest():
    # dataFile1=unicode('C:\Users\Levit\Experiment Data\Rakon晶振测试数据\两TDC测试\\6.13-2k-0.01s-all.txt','utf8')
    # dataFile2=unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\6.14NS\\6.14-60-170-timeWalkLinear.txt','utf8')
    # dataFile3=unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\6.27NS\\6.27NS-1900-2080-nofit.txt','utf8')
    # dataFile4=unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\6.30NS\\6.30NS-180-340.txt','utf8')
    # dataFile2=unicode('C:\Users\Levit\Experiment Data\Rakon晶振测试数据\两TDC测试\\7.6-2k-500s-1-0.01-TDEV.txt','utf8')
    dataFile3 = unicode('C:\Users\Levit\Experiment Data\Rakon晶振测试数据\两TDC测试\\20171114200130-tdc2-13-2k-500s-3_residual-1-0.01s-ps_TDEV.txt', 'utf8')

    # List1=fileToList.fileToList(dataFile1)
    # List2=fileToList.fileToList(dataFile2)
    List3=fileToList.fileToList(dataFile3)
    # List4=fileToList.fileToList(dataFile4)
    # List5=fileToList.fileToList(dataFile5)
    fig=plt.figure()
    # logPlotAx(List1,fig,'g','--','o','TDC Crystal Oscillator')
    # logPlotAx(List2,fig,'r','--','s','Rb Clock')
    logPlotAx(List3,fig,'y','--','v','Ultra Stable Crystal Oscillator')
    # logPlotAx(List4,fig,'c','--','^','6.30NS')
    # logPlotAx(List5,fig,'b','--','v','one TDC')

    plt.show()

if __name__=='__main__':
    logPlotAxTest()