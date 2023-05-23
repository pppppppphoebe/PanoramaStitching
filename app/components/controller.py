from components.view import View
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer
from components.stitcher.panorama import Panorama
from components.stitcher.stitcher import Stitcher
from components.opengl.Scene import *
from PIL import ImageQt
from PIL import ImageOps
import os
import cv2
import glob
import time

class Controller:
    def mainloop(self):
        self.scene.startDraw()

    def __init__(self,MainWindow):
        self.view = View(MainWindow)
        self.stitcher = Stitcher()
        self.EventHandler()
        self.panorama = Panorama()
        self.scene = GLWidget(self.view.openGLWidget)

        timer = QTimer(MainWindow)
        timer.timeout.connect(self.mainloop)
        timer.start(1)

    def EventHandler(self):
        #Button Event
        self.view.btn_input.clicked.connect(self.showFileDialog)
        self.view.btn_export.clicked.connect(self.exportImg)
        self.view.btn_folder.clicked.connect(self.showFolderDialog)
        # self.view.btn_stitch.clicked.connect(self.stitchImg)
        self.view.resetRotation.clicked.connect(self.resetRotation)
        self.view.fov_slider.valueChanged.connect(self.value_changed)
        self.view.rotationSlider_L.valueChanged.connect(self.value_changed)
        self.view.rotationSlider_R.valueChanged.connect(self.value_changed)
        self.view.radioButton.toggled.connect(self.showLine)


    def showFileDialog(self):
        self.inputfile = self.view.inputFileOpen()

        if self.inputfile and os.path.exists(self.inputfile):
            self.panorama.loadImage(self.inputfile)
            self.scene.isPerpestive = 0;
            self.scene.addimg(self.panorama.frontImg,self.panorama.rightImg,self.panorama.backImg,self.panorama.leftImg)

            qImg = self.convertToQImg(self.panorama.image,False)
            self.view.img_input.setPixmap(QPixmap.fromImage(qImg))
        else: 
            print("path not exists!")
    
    def showFolderDialog(self):
        folderpath = self.view.inputFolderOpen();

        if folderpath and os.path.exists(folderpath):
            folder_name = os.path.basename(folderpath)

            output_path = "./output/" + folder_name
            os.makedirs(output_path,exist_ok=True);

            img_list = glob.glob(folderpath+"/*.png")
            img_list.extend(glob.glob(folderpath+"/*.jpg"))

            #dewarp180_path = output_path+"/Dewarp180/"
            #dewarp110_path = output_path+"/Dewarp110_v2/"
            dewarp_outputpath = output_path+"/dewarping/"

            #os.makedirs(dewarp180_path,exist_ok=True);
            #os.makedirs(dewarp110_path,exist_ok=True);
            os.makedirs(dewarp_outputpath,exist_ok=True);

            #os.makedirs(dewarp110_path+"front",exist_ok=True);
            #os.makedirs(dewarp110_path+"back",exist_ok=True);
            #os.makedirs(dewarp110_path+"left",exist_ok=True);
            #os.makedirs(dewarp110_path+"right",exist_ok=True);

            for img in img_list:
                starttime = time.time();
                self.panorama.loadImage(img)
                self.scene.isPerpestive = 0;
                self.scene.addimg(self.panorama.frontImg,self.panorama.rightImg,self.panorama.backImg,self.panorama.leftImg)
                qImg = self.convertToQImg(self.panorama.image,False)
                self.view.img_input.setPixmap(QPixmap.fromImage(qImg))
                self.scene.startDraw()
                self.scene.paintGL()

                self.saveImage(dewarp_outputpath+os.path.splitext(os.path.basename(img))[0])
                endtime = time.time();
                print("Total time : ",endtime - starttime);
                #self.scene.isPerpestive = 1;
                #self.scene.startDraw()
                #self.scene.paintGL()

                #self.savePerpestiveImage(dewarp110_path,os.path.splitext(os.path.basename(img))[0])


  

    def saveImage(self,dewarp_outputpath):
        data = self.scene.readPixels()
        img = data.convertToFormat(QImage.Format.Format_RGB32)
        width = img.width()
        height = img.height()


        ptr = img.bits()
        ptr.setsize(height * width * 4)
        arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))

        #crop image to left right
        frontimg = arr[0:int(height/2),0:int(width/2)]
        rightimg = arr[0:int(height/2),int(width/2):width]
        backimg = arr[int(height/2):height,0:int(width/2)]
        leftimg = arr[int(height/2):height,int(width/2):width]

        frontimg = frontimg[0:1520,152:1368]
        backimg = backimg[0:1520,152:1368]


        leftimg = leftimg[0:1520,152:1368]
        rightimg = rightimg[0:1520,152:1368]

        bl = backimg[0:1520,0:608]
        br = backimg[0:1520,608:1216]

        os.makedirs(dewarp_outputpath,exist_ok=True);
        print(dewarp_outputpath)
        cv2.imwrite("{}/0.jpg".format(dewarp_outputpath),br);
        cv2.imwrite("{}/1.jpg".format(dewarp_outputpath),leftimg);
        cv2.imwrite("{}/2.jpg".format(dewarp_outputpath),frontimg);
        cv2.imwrite("{}/3.jpg".format(dewarp_outputpath),rightimg);
        cv2.imwrite("{}/4.jpg".format(dewarp_outputpath),bl);

        print("Save Successful!")

    def savePerpestiveImage(self,path,img_name):
        data = self.scene.readPixels()
        img = data.convertToFormat(QImage.Format.Format_RGB32)
        width = img.width()
        height = img.height()



        ptr = img.bits()
        ptr.setsize(height * width * 4)
        arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))

        width = 1024*2
        height = 1024*2
        arr = cv2.resize(arr, (width, height), interpolation=cv2.INTER_AREA)

        #crop image to left right
        leftimg = arr[0:int(height/2),0:int(width/2)]
        rightimg = arr[0:int(height/2),int(width/2):width]
        frontimg = arr[int(height/2):height,0:int(width/2)]
        backimg = arr[int(height/2):height,int(width/2):width]

        lw = int(1024/2-642/2)
        up = int(1024/2+642/2);

        leftimg = leftimg[lw:up,0:1024]
        rightimg = rightimg[lw:up,0:1024]
        frontimg = frontimg[lw:up,0:1024]
        backimg = backimg[lw:up,0:1024]


        cv2.imwrite("{}/left/{}.jpg".format(path,img_name),leftimg);
        cv2.imwrite("{}/right/{}.jpg".format(path,img_name),rightimg);
        cv2.imwrite("{}/front/{}.jpg".format(path,img_name),frontimg);
        cv2.imwrite("{}/back/{}.jpg".format(path,img_name),backimg);
        print("Save Successful!")
    

    def exportImg(self):

        data = self.scene.readPixels()
        img = data.convertToFormat(QImage.Format.Format_RGB32)
        width = img.width()
        height = img.height()


        ptr = img.bits()
        ptr.setsize(height * width * 4)
        arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))

        #crop image to left right
        leftimg = arr[0:int(height/2),0:int(width/2)]
        rightimg = arr[0:int(height/2),int(width/2):width]
        frontimg = arr[int(height/2):height,0:int(width/2)]
        backimg = arr[int(height/2):height,int(width/2):width]

        cv2.imwrite("output/dewarp_left.jpg",leftimg);
        cv2.imwrite("output/dewarp_right.jpg",rightimg);
        cv2.imwrite("output/dewarp_front.jpg",frontimg);
        cv2.imwrite("output/dewarp_back.jpg",backimg);
        print("Save Successful!")

    def stitchImg(self):
        #convert to mat
        data = self.scene.readPixels()
        img = data.convertToFormat(QImage.Format.Format_RGB32)
        width = img.width()
        height = img.height()
       
        ptr = img.bits()
        ptr.setsize(height * width * 4)
        arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))

        #crop image to left right
        leftimg = arr[0:height,0:int(width/2)]
        rightimg = arr[0:height,int(width/2):width]

        #setting overlap region
        w, h = leftimg.shape[:2]
        overlap = leftimg[0:h,int(w/4)*3:w]
        overlap2 = rightimg[0:h,0:int(w/4)]

        self.stitcher.threshold = 0.47
        result = self.stitcher.stitch(leftimg,rightimg,overlap,overlap2)
        cv2.imwrite("output/stitch_result.jpg",result);

    def dewarpImg(self):
        #dewarping image from left/right fisheye lenses
        img_L = self.stitcher.dewarping(self.panorama.leftImg)
        view_L = self.convertToQImg(img_L,True)
        self.view.img_left.setPixmap(QPixmap.fromImage(view_L)) 

        img_R = self.stitcher.dewarping(self.panorama.rightImg)
        view_R = self.convertToQImg(img_R,True)
        self.view.img_right.setPixmap(QPixmap.fromImage(view_R))


        middle = int(img_L.shape[0]/2)
        img_LL = img_L[0:img_L.shape[0],0:middle]
        img_LR = img_L[0:img_L.shape[0],middle:img_L.shape[0]]

        img_RL = img_R[0:img_L.shape[0],0:middle]
        img_RR = img_R[0:img_L.shape[0],middle:img_L.shape[0]]

        #export Image
        img_L = cv2.cvtColor(img_L, cv2.COLOR_RGB2BGR)
        cv2.imwrite('./output/left_dewarp.jpg', img_L)

        img_R = cv2.cvtColor(img_R, cv2.COLOR_RGB2BGR)
        cv2.imwrite('./output/right_dewarp.jpg', img_R)


    def convertToQImg(self,image,to_byte):
        height, width, channel = image.shape

        if image.ndim == 1:
            image =  cv2.cvtColor(img,cv2.COLOR_GRAY2RGB)

        bytesPerline = 3 * width

        if to_byte:
            qImg = QImage(image.data.tobytes(), width, height,bytesPerline, QImage.Format_RGB888)
        else:
            qImg = QImage(image.data, width, height,bytesPerline, QImage.Format_RGB888)
        
        return qImg

    def value_changed(self):
        value = self.view.fov_slider.value()
        self.view.fov_label.setText("fov: "+str(value))
        self.scene.fov = value

        angle = -90 + self.view.rotationSlider_L.value()/2
        self.view.label_rotation_L.setText("angle: "+str(angle))
        self.scene.rotate_L = angle

        angle = -90 + self.view.rotationSlider_R.value()/2
        self.view.label_rotation_R.setText("angle: "+str(angle))
        self.scene.rotate_R = angle

    def showLine(self,enabled):
        self.scene.showLine = enabled

    def resetRotation(self):
        self.view.rotationSlider_L.setValue(180)
        self.view.rotationSlider_R.setValue(180)
        self.view.label_rotation_L.setText("angle: "+str(0))
        self.view.label_rotation_R.setText("angle: "+str(0))
        self.scene.rotate_L = 0
        self.scene.rotate_R = 0
