#!/usr/bin/env python
#-*- coding: utf-8 -*-
__author__ = 'levitan'

def fileToList(filename):
    List=[]
    with open(filename) as file:
        for line in file:
            N=len(line.split())
            L=[]
            for i in range(N):
                L+=[float(line.split()[i])]
                #print L
            List.append(L)
    file.close()
    print filename + ' converted to List !'
    return List

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
