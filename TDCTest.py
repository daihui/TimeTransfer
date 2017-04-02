#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'levitan'

import fileToList


def classifyData(dataFile):
    filename=dataFile[:-4] + '_classified.txt'
    dataClassify = open(filename, 'w')
    try:
        with open(dataFile) as f:
            for line in f:
                dataline = line.split()
                if dataline[0] == '0':
                    dataClassify.write(dataline[1] + '\t')
                elif dataline[0] == '1':
                    dataClassify.write(dataline[1] + '\n')
            dataClassify.flush()
            dataClassify.close()
    finally:
        print 'data classify successfully !'
    return filename


def timeAnalysis(timeList):
    diffList = []
    for i, item in enumerate(timeList):
        diffList.append([float(i), float(item[0]) - float(item[1])])
    print 'get the diffList.'
    return diffList


if __name__ == '__main__':
    dataFile = unicode('E:\Experiment Data\时频传输数据处理\本地TDC测试\\4.1\解析\\recv_time-10k-100s-1.txt', 'utf8')
    dataClassify = classifyData(dataFile)
    timeList = fileToList.fileToList(dataClassify)
    diffList = timeAnalysis(timeList)
    fileToList.listToFile(diffList, dataClassify[:-4] + '_diff.txt')
