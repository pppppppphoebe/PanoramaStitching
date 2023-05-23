img_path1 = "./input/001.jpg"
img_path2 = "./input/002.jpg"

import cv2
from components.stitcher.stitcher import Stitcher

img = cv2.imread(img_path2)
img2 = cv2.imread(img_path1)

stitcher = Stitcher()
stitcher.threshold = 0.4
result = stitcher.stitch(img2,img,img2,img)
cv2.imshow("result",result)
cv2.waitKey()   