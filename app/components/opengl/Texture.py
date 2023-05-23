from OpenGL.GL import *
import numpy as np

class Texture:
    def __init__(self, input=None,texid=0):
        self.image = input
        self.ix = input.shape[1]
        self.iy = input.shape[0]
        self.texid = texid
        self.init()

    def activate(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, (self.id))

    def init(self):
        # make it current
        self.id = glGenTextures(1)
        self.activate()
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        # copy the texture into the current texture ID
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.ix, self.iy, 0,
                     GL_RGB, GL_UNSIGNED_BYTE, self.image)

    def update(self, input):
        self.image = input
        self.ix = input.shape[1]
        self.iy = input.shape[0]
        glDeleteTextures([self.id])
        self.init()