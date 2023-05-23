import cv2
import numpy as np
from PyQt5.QtGui import QImage, QPixmap

class Panorama(object):
    def __init__(self):
        self.cols = 0
        self.rows = 0
        self.image = None
        self.leftImg = None
        self.rightImg = None
        self.frontImg = None
        self.backImg = None

    def loadImage(self,image_path):
        img = cv2.imread(image_path)
        print(image_path)
        self.image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        h,w = self.image.shape[:2]

        self.frontImg = self.image[0:int(h/2),0:int(w/2) ]
        self.backImg = self.image[0:int(h/2),int(w/2):w ]

        self.leftImg = self.image[int(h/2):h,0:int(w/2) ]
        self.rightImg = self.image[int(h/2):h,int(w/2):w ]

        tmp = cv2.cvtColor(self.frontImg , cv2.COLOR_RGB2BGR)
        tmp2 = cv2.cvtColor(self.backImg , cv2.COLOR_RGB2BGR)
        tmp3 = cv2.cvtColor(self.leftImg , cv2.COLOR_RGB2BGR)
        tmp4 = cv2.cvtColor(self.rightImg , cv2.COLOR_RGB2BGR)

        cv2.imwrite("output/ori_F.jpg",tmp);
        cv2.imwrite("output/ori_B.jpg",tmp2);
        cv2.imwrite("output/ori_L.jpg",tmp3);
        cv2.imwrite("output/ori_R.jpg",tmp4);

        self.cols = self.image.shape[1]
        self.rows = self.image.shape[0]

    def rotate_image(self,image, angle):
        """
        Rotates an image (angle in degrees) and expands image to avoid cropping
        """
        
        height, width = image.shape[:2] # image shape has 3 dimensions
        image_center = (width/2, height/2) # getRotationMatrix2D needs coordinates in reverse order (width, height) compared to shape

        rotation_mat = cv2.getRotationMatrix2D(image_center, angle, 1.)

        # rotation calculates the cos and sin, taking absolutes of those.
        abs_cos = abs(rotation_mat[0,0]) 
        abs_sin = abs(rotation_mat[0,1])

        # find the new width and height bounds
        bound_w = int(height * abs_sin + width * abs_cos)
        bound_h = int(height * abs_cos + width * abs_sin)

        # subtract old image center (bringing image back to origo) and adding the new image center coordinates
        rotation_mat[0, 2] += bound_w/2 - image_center[0]
        rotation_mat[1, 2] += bound_h/2 - image_center[1]

        # rotate image with the new bounds and translated rotation matrix
        rotated_mat = cv2.warpAffine(image, rotation_mat, (bound_w, bound_h))
        return rotated_mat
    
    def save_img(self):
        cv2.imwrite('./output/left_dewarp.jpg', self.leftImg)