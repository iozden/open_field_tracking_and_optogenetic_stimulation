

import matplotlib.pyplot as plt
import scipy as sp
import numpy as np
import copy
import pickle
import os
import cv2
import Tkinter, tkFileDialog
from time import sleep
import pylab
from matplotlib.widgets import Slider
import time

root = Tkinter.Tk()
root.withdraw()

filepath = tkFileDialog.askopenfilename()

#%%

f=open(filepath,"r")
data=pickle.load(f)
f.close()

#%%

pos=data[0]
mapImage=data[1]
refFrame=data[2]
#mov=data[3]

del data

#%%

plt.figure(1)
plt.imshow(refFrame,cmap='gray')

plt.figure(2)
plt.imshow(0.5*refFrame+0.5*np.multiply(refFrame,mapImage),cmap='gray')


#%%
#nFrames,x,y=mov.shape
#nFrames=int(nFrames)
#
#ax = pylab.subplot(111)
#pylab.subplots_adjust(left=0.25, bottom=0.25)
#frame=0
#fig=pylab.imshow(mov[frame,:,:],cmap='gray')
#
#axframe = pylab.axes([0.25, 0.1, 0.65, 0.03])
#sframe = Slider(axframe, 'Frame', 0, nFrames, valinit=0, valstep=1)
#
#def update(val):
#	frame = int(sframe.val)
#	cfr=mov[frame,:,:]
#	x=int(pos[frame,0])
#	y=int(pos[frame,1])
#	cfr[x-10:x+10,y-10:y+10]=255
#	fig.set_data(cfr)
#
#sframe.on_changed(update)
#pylab.show()

#%%

nFrames=len(pos)
x,y=refFrame.shape
nFrames=int(nFrames)


ax = pylab.subplot(111)
pylab.subplots_adjust(left=0.25, bottom=0.25)
fig=pylab.imshow(refFrame,cmap='gray')

axframe = pylab.axes([0.25, 0.1, 0.65, 0.03])
sframe = Slider(axframe, 'Frame', 0, nFrames, valinit=0, valstep=1)
cfr=0.5*refFrame+0.5*np.multiply(refFrame,mapImage)
def update(val):
	frame = int(sframe.val)
	x=int(pos[frame,0])
	y=int(pos[frame,1])
	cfr[x-5:x+5,y-5:y+5]=255
	fig.set_data(cfr)

sframe.on_changed(update)
pylab.show()

#%%

nFrames=len(pos)
x,y=refFrame.shape
nFrames=int(nFrames)


ax = pylab.subplot(111)
pylab.subplots_adjust(left=0.25, bottom=0.25)
fig=pylab.imshow(refFrame,cmap='gray')

axframe = pylab.axes([0.25, 0.1, 0.65, 0.03])
sframe = Slider(axframe, 'Frame', 0, nFrames, valinit=0, valstep=1)
cfr=0.5*refFrame+0.5*np.multiply(refFrame,mapImage)

def update(val):
	sframe.val=sframe.val+1
	frame = int(sframe.val)
	x=int(pos[frame,0])
	y=int(pos[frame,1])
	cfr[x-5:x+5,y-5:y+5]=255
	fig.set_data(cfr)

sframe.on_changed(update)
pylab.show()

