# -*- coding: utf-8 -*-
"""
Created on Thu Oct 08 23:27:50 2015

@author: humblercoder
"""
import sys
import _pymass
from _pymass import MZXML
from matplotlib.pylab import plot, show, figure
#_pymass.testMZXML()



mzfile=u"D:/workspace/pymass/python/标2-方法5-正负离子_Seg1Ev1.mzXML"

#_pymass.testMZXML()

mz1=MZXML()
mz1.parseFile(mzfile.encode(sys.getfilesystemencoding()))
rt=mz1.getRT()
bic=mz1.getBIC()
tic=mz1.getTIC()
plot(rt,bic,'r')
plot(rt,tic,'g')



mz=mz1.getMS(0)
val=mz1.getVal(0)

figure()
plot(mz,val)
show()

