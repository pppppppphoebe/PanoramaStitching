import cv2
import numpy as np
import math
import time

class Stitcher:
    def __init__(self):
        self.model = "Insta360 ONE X2"
        self.fov = 195  # not sure
        self.focal = 7.2  # mm
        self.aperture = 1.12
        self.xmap = []
        self.ymap = []
        self.threshold = 0.4

    def update_mapping(self, Ws, Hs):
        #update mapping from de-warped images to fisheyye image
        time_start=time.time()

        Hd = Hs
        Wd = Ws

        fov = self.fov * np.pi / 180.0

        # cartesian coordinates of the de-warped rectangular image
        yd, xd = np.indices((Hd, Wd), np.float32)

        y_proj = Hd / 2.0 - yd
        x_proj = xd - Wd / 2.0

        # spherical coordinates
        theta, phi = self.equirect_proj(x_proj, y_proj, Ws, Hs, fov)

        # polar coordinates (of the fisheye image)
        p = Hd * phi / fov

        # cartesian coordinates of the fisheye image
        y_fish = p * np.sin(theta)
        x_fish = p * np.cos(theta)

        self.ymap = Hs / 2.0 - y_fish
        self.xmap = ((Ws) / 2.0 + x_fish)
        time_end=time.time()

        print('Estimate mapping time cost',time_end-time_start,'s')

    def equirect_proj(self, x_proj, y_proj, W, H, fov):
        theta_alt = x_proj * fov / W
        phi_alt = y_proj * np.pi / H

        x = np.sin(theta_alt) * np.cos(phi_alt)
        y = np.sin(phi_alt)
        z = np.cos(theta_alt) * np.cos(phi_alt)
        return np.arctan2(y, x), np.arctan2(np.sqrt(x**2 + y**2), z)

    def dewarping(self, img):
        time_start=time.time()
        result = cv2.remap(img, self.xmap, self.ymap, cv2.INTER_LINEAR, cv2.BORDER_CONSTANT)
        time_end=time.time()
        print('Remap time cost',time_end-time_start,'s')
        return result

    def feature_extract(self,img):
        #use SIFT algorithm to extract feature
        sift = cv2.SIFT_create()
        gray= cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        kp = sift.detect(gray,None)
        return kp

    def warp(self,img1,img2,H):
        h1,w1 = img1.shape[:2]
        h2,w2 = img2.shape[:2]

        pts1 = np.float32([[0,0],[0,h1],[w1,h1],[w1,0]]).reshape(-1,1,2)
        pts2 = np.float32([[0,0],[0,h2],[w2,h2],[w2,0]]).reshape(-1,1,2)
        pts2_ = cv2.perspectiveTransform(pts2, H)

        pts =  np.concatenate((pts1, pts2_), axis=0)
        [xmin, ymin] =  np.int32(pts.min(axis=0).ravel() - 0.5)
        [xmax, ymax] =  np.int32(pts.max(axis=0).ravel() + 0.5)
        t = [-xmin,-ymin]

        Ht =  np.array([[1,0,t[0]],[0,1,t[1]],[0,0,1]]) # translate
        #warp image
        img_warp2 = cv2.warpPerspective(img2, Ht.dot(H), (xmax-xmin, ymax-ymin))
        img_warp2[t[1]:h1+t[1], t[0]:w1+t[0]] = img1
        return img_warp2


    def stitch(self,img1,img2,overlap,overlap2):
        
        height,width = img1.shape[:2]
        height_overlap,width_overlap = overlap.shape[:2]

        gray= cv2.cvtColor(overlap,cv2.COLOR_BGR2GRAY)
        gray2= cv2.cvtColor(overlap2,cv2.COLOR_BGR2GRAY)

        sift = cv2.SIFT_create()
        kp1, des1 = sift.detectAndCompute(gray,None)
        kp2, des2 = sift.detectAndCompute(gray2,None)

        for kp in kp1:
            coor = list(kp.pt)
            coor[0] += width - width_overlap
            kp.pt = tuple(coor)

        # BFMatcher with default params
        bf = cv2.BFMatcher()
        matches = bf.knnMatch(des1,des2,k=2)

        # Apply ratio test
               # Apply ratio test
        good = []
        for m,n in matches:
            if m.distance < self.threshold*n.distance:
                good.append([m])

        # cv.drawMatchesKnn expects list of lists as matches.
        img3 = cv2.drawMatchesKnn(img1,kp1,img2,kp2,good,None,flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
        cv2.imwrite("feature_Match.jpg",img3)
        # Array to store matching points
        img1_pts = []
        img2_pts = []


		# Add matching points to array
        for match in good:
            img1_pts.append(kp1[match[0].queryIdx].pt)
            img2_pts.append(kp2[match[0].trainIdx].pt)
        img1_pts = np.float32(img1_pts).reshape(-1,1,2)
        img2_pts = np.float32(img2_pts).reshape(-1,1,2)
        M, mask = cv2.findHomography(img2_pts, img1_pts, cv2.RANSAC,3.5)    

        result = self.warp(img1,img2,M)
        return result
