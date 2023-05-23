from OpenGL.GL import *

class Mesh():
    def __init__(self, mat, geo):
        self.material = mat
        self.geometry = geo
        self.visible = True
        self.wireframe = False

    def init(self):
        shader = self.material.init()
        self.geometry.shader = shader
        self.geometry.init()

    def draw(self):
        self.material.activate()
        self.geometry.draw()
        self.material.deactivate()

