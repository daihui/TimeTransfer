#!/usr/bin/env python
#-*- coding: utf-8 -*-
__author__ = 'levitan'

def fileToList(filename):
    List=[]
    count=0
    file= open(filename,'r')
    for line in file:
        List.append([])
        N=len(line.split())
        for i in range(N):
            List[count]+=[float(line.split()[i])]
        count+=1
    file.close()
    print filename + ' converted to List !'
    return List

def fileLong(filename):
    List=fileToList(filename)
    saveFile=filename[:-4]+'_long.txt'
    listToFile(List,saveFile)
    print 'file convert to float long file'

def listToFileFloat(List,filename):
    file=open(filename,'w')
    N=len(List)
    for i in xrange(N):
        J=len(List[i])
        for j in range(J):
            file.write('%s\t'%List[i][j])
        file.write('\n')
    file.flush()
    file.close()
    print 'List save to file !'

def listToFile(List,filename):
    file=open(filename,'w')
    N=len(List)
    for i in xrange(N):
        J=len(List[i])
        for j in range(J):
            file.write('%.3f\t'%List[i][j])
        file.write('\n')
    file.flush()
    file.close()
    print 'List save to file !'

def listToFileLong(List,filename):
    file=open(filename,'w')
    N=len(List)
    for i in xrange(N):
        J=len(List[i])
        for j in range(J):
            file.write('%.13f\t'%List[i][j])
        file.write('\n')
    file.flush()
    file.close()
    print 'List save to file !'

