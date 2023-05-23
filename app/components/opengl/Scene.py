
import numpy as np
import pyrr
from PIL import Image

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL import shaders

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QOpenGLWidget

import components.opengl.shader.shader as myshader
import components.opengl.shader.BasicShader as screenshader

from components.opengl.uniform import *
from components.opengl.Mesh import *
from components.opengl.material.BasicMaterial import *
from components.opengl.material.ShaderMaterial import *
from components.opengl.Texture import *
from components.opengl.geometry.plane import *
from components.opengl.geometry.screen import *
from components.opengl.Camera import *


class GLWidget(QOpenGLWidget):
    def __init__(self, openGLWidget):

        self.fov = 180.5 #fisheye fov
        self.rotate_L = 0;
        self.rotate_R = 0;
        self.isPerpestive = 1;

        #self.offScreenSize = [6460, 3040 ] #offscreen render window size
        self.offScreenSize = [3040, 3040 ] 
        self.showLine = False
        self.openGLWidget = openGLWidget

        self.openGLWidget.initializeGL = self.initializeGL
        self.openGLWidget.paintGL = self.paintGL
        self.openGLWidget.resizeGL = self.resizeGL

        self.mouseCoord = [0, 0]
        self.openGLWidget.mouseMoveEvent = self.mouseMoveEvent
        self.openGLWidget.mousePressEvent = self.mousePressEvent
        self.openGLWidget.mouseReleaseEvent = self.mouseReleaseEvent
        self.openGLWidget.wheelEvent = self.wheelEvent

        format = QSurfaceFormat()
        format.defaultFormat()
        format.setProfile(QSurfaceFormat.CoreProfile)
        self.openGLWidget.setFormat(format)

        self.meshes = []
        self.customRender = []
        size = self.openGLWidget.size()
        self.size = [size.width(), size.height()]

        view = pyrr.matrix44.create_look_at(np.array([2.0, 2.0, 3.0], dtype="float32"),
                                            np.array([0.0, 0.0, 0.0],dtype="float32"),
                                            np.array([0.0, 1.0, 0.0], dtype="float32"))
        projection = pyrr.matrix44.create_perspective_projection(60.0, self.size[0]/self.size[1], 0.1, 200.0)
        model = pyrr.matrix44.create_from_translation(pyrr.Vector3([0.0, 0.0, 0]))

        self.mvp = view * model * projection

    def _compile_shader(self, src, shader_type):
        shader = GL.glCreateShader(shader_type)
        OpenGL.GL.glShaderSource(shader, src)
        OpenGL.GL.glCompileShader(shader)
        return shader

    def initializeGL(self):
        self.openGLWidget.makeCurrent()

        # 設置畫布背景色
        glClearColor(0, 0, 0, 0)
        # 開啓深度測試，實現遮擋關係
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)                                      # 設置深度測試函數
        # GL_SMOOTH(光滑着色)/GL_FLAT(恆定着色)
        glShadeModel(GL_SMOOTH)
        glEnable(GL_BLEND)                                          # 開啓混合
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)           # 設置混合函數
        # 啓用 Alpha 測試
        glEnable(GL_ALPHA_TEST)
        # 設置 Alpha 測試條件爲大於 0.05 則通過
        glAlphaFunc(GL_GREATER, 0.05)
        # 設置逆時針索引爲正面（GL_CCW/GL_CW）
        glFrontFace(GL_CW)
        glEnable(GL_LINE_SMOOTH)                                    # 開啓線段反走樣
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

        # Creating Texture
        #self.texture = glGenTextures(1)
        self.fbo = QOpenGLFramebufferObject( self.offScreenSize[0], self.offScreenSize[1] )

        self.img_data = np.asarray([[]])
        self.img_data2 = np.asarray([[]])
        self.img_data3 = np.asarray([[]])
        self.img_data4 = np.asarray([[]])

        self.texture = Texture(self.img_data, 0)
        self.texture2 = Texture(self.img_data2, 1)
        self.texture3 = Texture(self.img_data3, 2)
        self.texture4 = Texture(self.img_data4, 3)

        self.uniform = Uniform()
        self.uniform.addInt('isPerpestive', 0)
        self.uniform.addFloat('Hd', self.size[1])
        self.uniform.addFloat('Wd', self.size[0])

        self.uniform.addFloat('Hs', self.size[1])
        self.uniform.addFloat('Ws', self.size[0])
        self.uniform.addMat4('mvp', self.mvp)
        # self.uniform.addTexture('texture',self.texture)

        self.uniform.addInt('line', 0)
        self.uniform.addFloat('fov_angle', self.fov)
        self.uniform.addFloat('rotation', 0)

        self.plane = PlaneGeometry(True,False,10,10)
        mat_LT = ShaderMaterial(myshader.vs, myshader.fs,self.uniform, self.texture)
        self.mesh1 = Mesh(mat_LT, self.plane)

        self.plane2 = PlaneGeometry(False,False,10,10)
        mat_RT = ShaderMaterial(myshader.vs, myshader.fs,self.uniform, self.texture2)
        self.mesh2 = Mesh(mat_RT, self.plane2)

        #plane BTM
        self.plane3 = PlaneGeometry(True,True,10,10)
        mat_LB = ShaderMaterial(myshader.vs, myshader.fs,self.uniform, self.texture3)
        self.meshLB = Mesh(mat_LB, self.plane3)

        self.plane4 = PlaneGeometry(False,True,10,10)
        mat_RB = ShaderMaterial(myshader.vs, myshader.fs,self.uniform, self.texture4)
        self.meshRB = Mesh(mat_RB, self.plane4)

        self.screen = ScreenGeometry()
        mat3 = BasicMaterial(screenshader.vs, screenshader.fs)
        self.mesh3 = Mesh(mat3, self.screen)

        self.openGLWidget.doneCurrent()


    def addimg(self, leftimg, rightImg,BL,BR):
        self.img_data = np.asarray(leftimg)
        self.texture.update(self.img_data)

        self.img_data2 = np.asarray(rightImg)
        self.texture2.update(self.img_data2)

        self.img_data3 = np.asarray(BL)
        self.texture3.update(self.img_data3)

        self.img_data4 = np.asarray(BR)
        self.texture4.update(self.img_data4)

    def add(self, mesh):
        self.openGLWidget.makeCurrent()
        mesh.init()
        self.meshes.append(mesh)
        self.openGLWidget.doneCurrent()

    def paintGL(self):
        #draw on frame buffer
        glViewport( 0, 0,self.offScreenSize[0], self.offScreenSize[1] )
        self.fbo.bind()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glDisable(GL_DEPTH_TEST) 

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        self.uniform.setValue('isPerpestive',self.isPerpestive)
        self.uniform.setValue('Hd', self.offScreenSize[1])
        self.uniform.setValue('Wd', self.offScreenSize[0])
        self.uniform.setValue('Hs', self.img_data.shape[1])
        self.uniform.setValue('Ws', self.img_data.shape[0])
        self.uniform.setValue('fov_angle', self.fov)
        self.uniform.setValue('line',0)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        self.uniform.setValue('rotation',self.rotate_R)
        self.mesh2.draw()

        self.uniform.setValue('rotation',self.rotate_L)
        self.mesh1.draw()

        self.meshLB.draw()
        self.meshRB.draw()

        # # Draw line
        if(self.showLine):
            self.uniform.setValue('line',1)
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            self.mesh2.draw()
            self.mesh1.draw()
            self.meshLB.draw()
            self.meshRB.draw()

        for mesh in self.meshes:
            mesh.draw()
        self.fbo.release()

        #bind frame buffer texture and draw on screen
        glViewport( 0, 0,self.size[0] , self.size[1] )
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glBindTexture(GL_TEXTURE_2D,self.fbo.texture())
        self.mesh3.draw()
    
    def resizeGL(self, width, height):
        size = self.openGLWidget.size()
        self.size = [size.width(), size.height()]
        self.openGLWidget.makeCurrent()
        #self.camera.setViewport(self.size[0], self.size[1])

    def startDraw(self):
        self.openGLWidget.makeCurrent()
        self.openGLWidget.update()

    def endDraw(self):
        self.openGLWidget.doneCurrent()

    def wheelEvent(self, evt):
        print()
        # self.camera.zoom(evt.angleDelta().y())

    def mouseReleaseEvent(self, evt):
        if(evt.button() == Qt.LeftButton):
            self.mouseCoord = [0, 0]

    def mousePressEvent(self, evt):
        if(evt.button() == Qt.LeftButton):
            x = evt.localPos().x()
            y = evt.localPos().y()
            self.mouseCoord = (x, y)

    def mouseMoveEvent(self, evt):
        if(self.mouseCoord != None):
            x = evt.localPos().x()
            y = evt.localPos().y()

            deltaX = x-self.mouseCoord[0]
            deltaY = self.mouseCoord[1]-y

            #self.camera.dragCamera(deltaX, deltaY)

            self.mouseCoord = (x, y)

    def readPixels(self):
        #read pixel from frame buffer
        self.openGLWidget.makeCurrent()
        return self.fbo.toImage() 
