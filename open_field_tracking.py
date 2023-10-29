import matplotlib
# matplotlib.use('tkagg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import  tkinter
from tkinter import *

import cv2
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.patches as patches
import scipy as sp
import scipy.io
import numpy as np
from skimage import morphology
from skimage.measure import regionprops
import datetime
import copy
from serial import Serial
import pickle
import os
from os.path import isfile, join

#%%

root=tkinter.Tk()
root.title("Test GUI")
root.geometry('{}x{}'.format(1200,800))

class my_class:
    def __init__(self, master):
        self.master = master

        self.fig = Figure()
        ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig,master=master)
        self.canvas.draw()
        self.canvas.get_tk_widget().place(relx=.4, rely=.4, width=800, height=600, anchor="c")

        self.button_refFrame=Button(master,text='Get RefFrame',width=10, command=self.getRefFrame)
        self.button_refFrame.place(relx=.2, rely=.8, anchor="c")

        self.button_select_region=Button(master,text='Select region',width=10, command=self.select_region)
        self.button_select_region.place(relx=.3, rely=.8, anchor="c")

        self.button_start = Button(master, text="Start", width=10, command=self.start)
        self.button_start.place(relx=.5, rely=.85, anchor="c")

        self.button_save=Button(master,text='save',width=10, command=self.save_data)
        self.button_save.place(relx=.6, rely=.85, anchor="c")

        self.button_quit = Button(master, text="QUIT", width=10, command=self.close)
        self.button_quit.place(relx=.7, rely=.85, anchor="c")

        self.reference_flag = IntVar(value=1)
        self.reference = Checkbutton(master,text="reference",variable=self.reference_flag,command=self.reg).place(relx=0.35,rely=0.78)

        self.region1_flag = IntVar(value=0)
        self.region1 = Checkbutton(master,text="Region 1",variable=self.region1_flag,command=self.reg1).place(relx=0.35,rely=0.82)

        self.region2_flag = IntVar(value=0)
        self.region2 = Checkbutton(master,text="Region 2",variable=self.region2_flag,command=self.reg2).place(relx=0.35,rely=0.86)

        Label(master, text="filename").place(relx=0.1,rely=0.837)
        self.filename = Entry(master,text='filename')
        self.filename.place(relx=.2, rely=.85, width=120, height=20, anchor="c")
        
        fname='mouse_ID'        
        self.filename.insert(10,fname)

        Label(master, text="filepath").place(relx=0.1,rely=0.887)
        self.filepath = Entry(master,text='filepath')
        self.filepath.place(relx=.2, rely=.9, width=200, height=20, anchor="c")
        self.filepath.insert(10,'C:\\Users\\S2c_cengrozden\\Desktop\\data\\open_field')

        Label(master, text="number of frames").place(relx=0.46,rely=0.78)
        self.frame_number= Entry(master,text='number of frames')
        self.frame_number.place(relx=.56, rely=.795, width=40, height=20, anchor="c")
        self.frame_number.insert(10,'3000')

        Label(master, text="arduino port").place(relx=0.46,rely=0.88)
        self.port_num= Entry(master,text='arduino port')
        self.port_num.place(relx=.54, rely=.895, width=40, height=20, anchor="c")
        self.port_num.insert(10,'COM4')
        
        self.record_movie_flag = IntVar(value=1)
        self.record_movie = Checkbutton(master,text="record movie",variable=self.record_movie_flag).place(relx=0.60,rely=0.88)  
        
        self.autosave_flag = IntVar(value=1)
        self.autosave = Checkbutton(master,text="autosave",variable=self.autosave_flag).place(relx=0.70,rely=0.88)         

    def getRefFrame (self):
        global refFrame
        global x
        global y
        global vc
        

        cv2.namedWindow("Cam")
        vc = cv2.VideoCapture(0,cv2.CAP_DSHOW)
        vc.set(3, 960)
        vc.set(4, 720)
        vc.set(cv2.CAP_PROP_AUTOFOCUS, 0)

        if vc.isOpened(): # try to get the first frame
            rval, refFrame = vc.read()
        else:
            rval = False

        while rval:
            t0=datetime.datetime.now()
            cv2.imshow("Cam", refFrame)
            rval, refFrame = vc.read()
            refFrame = cv2.cvtColor(refFrame, cv2.COLOR_BGR2GRAY)
            key = cv2.waitKey(20)
            t1=datetime.datetime.now()
            t=t1-t0
            #print(t.microseconds/1000)
            if key == 27: # exit on ESC
                break

        sRef=refFrame.shape
        x=int(sRef[0])
        y=int(sRef[1])

        cv2.destroyWindow("Cam")
        ax = self.canvas.figure.axes[0]
        ax.imshow(refFrame,cmap='gray')
        self.canvas.draw()
        #vc.release()

    def select_region (self):
        global mapImage
        key=1;
        while key!=27:
            img=copy.deepcopy(refFrame)
            cv2.destroyAllWindows()
            reg1=cv2.selectROI(img)
            cv2.destroyAllWindows()
            cv2.rectangle(img,(reg1[0],reg1[1]),(reg1[0]+reg1[2],reg1[1]+reg1[3]),255,2)
            cv2.imshow('roi',img)
            key = cv2.waitKey(0)

        img=np.zeros((x,y))
        img[reg1[1]:(reg1[1]+reg1[3]),reg1[0]:(reg1[0]+reg1[2])]=refFrame[reg1[1]:(reg1[1]+reg1[3]),reg1[0]:(reg1[0]+reg1[2])]
        img=0.5*img+0.5*refFrame

        plt.figure(0)
        plt.imshow(img,cmap='gray')
        plt.show()

        mapImage=np.zeros((x,y))
        mapImage[reg1[1]:(reg1[1]+reg1[3]),reg1[0]:(reg1[0]+reg1[2])]=1
        plt.figure(1)
        plt.imshow(mapImage,cmap='gray')
        plt.show()

    def reg(self):
        self.region1_flag.set(0)
        self.region2_flag.set(0)
        ax = self.canvas.figure.axes[0]
        ax.imshow(refFrame,cmap='gray')
        self.canvas.draw()

    def reg1(self):
        self.reference_flag.set(0)
        self.region2_flag.set(0)
        ax = self.canvas.figure.axes[0]
        ax.imshow(0.5*refFrame+0.5*np.multiply(refFrame,mapImage),cmap='gray')
        self.canvas.draw()

    def reg2(self):
        self.reference_flag.set(0)
        self.region1_flag.set(0)
        ax = self.canvas.figure.axes[0]
        ax.imshow(refFrame-0.5*np.multiply(refFrame,mapImage),cmap='gray')
        self.canvas.draw()

    def start(self):
        global mov
        global target_position
        global ser
        global fileTime
        global movout
        global selreg
        now=datetime.datetime.now()
        fileTime='_'+ now.strftime("%Y_%m_%d_%H%M")
        nFrames=int(self.frame_number.get())
        if self.record_movie_flag.get():
            #mov=np.zeros((nFrames,x,y),dtype=np.uint8)
            pname=self.filepath.get()
            fname=pname+'\\'+self.filename.get()+fileTime+'.mp4'
            fname=fname.replace('\\','/')
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            movout=cv2.VideoWriter(fname, fourcc, 15, (960, 720))
        #else:
            #mov=[]
        target_position=np.zeros((nFrames,4))
        font = cv2.FONT_HERSHEY_SIMPLEX

        nPort=self.port_num.get()
        ser=Serial(port=nPort,baudrate=115200)
        ser.write("1".encode())
        ser.write("0".encode())
        vc = cv2.VideoCapture(0,cv2.CAP_DSHOW)
        vc.set(3, 960)
        vc.set(4, 720)
        cv2.imshow('mov',refFrame)
        #cv2.waitKey(1)
        r1=self.reference_flag.get()
        r2=self.region1_flag.get()
        r3=self.region2_flag.get()
        if r1:
            stim='2'
            nostim='2'
            selreg='ref'
        if r2:
            stim='1'
            nostim='0'
            selreg='reg1'
        if r3:
            stim='0'
            nostim='1'
            selreg='reg2'

        key=1
        
        inreg=0
        t0=datetime.datetime.now()
        for i in range(nFrames):
            rval,frame = vc.read()
            if self.record_movie_flag.get():
                #mov[i,:,:]=frame
                movout.write(frame)
            frame=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            dfr= cv2.absdiff(refFrame,frame)
            dfr=cv2.blur(dfr,(3,3))
            thresh=0.18*255
            dfr = cv2.threshold(dfr,thresh,255,cv2.THRESH_BINARY)[1]
            dfr=morphology.remove_small_objects(dfr, min_size=30, connectivity=4)
            bw=sp.ndimage.label(dfr)
            stats = regionprops(bw[0])
            n=np.size(stats)
            if n!=0:
                maxArea=0
                ind=0
                for j in range(n):
                    if maxArea<stats[j].area:
                        maxArea=stats[j].area
                        ind=j
                c=stats[ind].centroid
            else:
                c=(0,0)
            target_position[i][0]=c[0]
            target_position[i][1]=c[1]
            t=datetime.datetime.now()-t0
            target_position[i][2]=t.microseconds/1000
            #print(t.microseconds/1000)
            t0=datetime.datetime.now()
            cv2.putText(frame,'*',(int(c[1]), int(c[0])), font, 4,255,2,cv2.LINE_AA)
            if mapImage[int(c[0]),int(c[1])]==1:
                target_position[i][3]=int(stim)
                if i==1:
                    ser.write(stim.encode())
                    inreg=1
                if inreg==0:
                    #print(inreg)
                    inreg=1
                    ser.write(stim.encode())
            else:
                target_position[i,3]=int(nostim)
                if i==1:
                    ser.write(nostim.encode())
                    inreg=0
                if inreg==1:
                    #print(inreg)
                    inreg=0
                    ser.write(nostim.encode())
            cv2.imshow('mov',frame)
            key=cv2.waitKey(1)
            if key==27:
                ser.write('0'.encode())
                ser.close()
                #mov=mov[0:i,:,:]
                if self.autosave_flag.get():
                    self.save_data()
                break
        if self.autosave_flag.get():
            self.save_data()        
        ser.write('0'.encode())
        ser.close()

    def save_data(self):
        pname=self.filepath.get()
        fname=pname+'\\'+self.filename.get() + fileTime+ '_' + selreg
        fname=fname.replace('\\','/')
        scipy.io.savemat(fname+'.mat', mdict={'target_position': target_position,'mapImage': mapImage, 'refFrame': refFrame})
        fname=fname+'.pkl'
        if self.record_movie_flag.get():
            movout and movout.release()
        with open(fname, 'wb') as f:
            #pickle.dump([target_position,mapImage,refFrame, mov],f)
            pickle.dump([target_position,mapImage,refFrame],f)
            
    def close(self):
        self.master.destroy()
        vc.release()
        ser.close()


mygui=my_class(root)
root.mainloop()

