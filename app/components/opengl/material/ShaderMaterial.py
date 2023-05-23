from OpenGL.GL import *
from OpenGL.GL import shaders


class ShaderMaterial():
    def __init__(self, vert, frag, uniform,texture):
        self.vertShader = vert
        self.fragShader = frag
        self.uniform = uniform
        self.texture = texture
        self.init()

    def init(self):

        VERTEX_SHADER = shaders.compileShader(
            self.vertShader, GL_VERTEX_SHADER)
        FRAGMENT_SHADER = shaders.compileShader(
            self.fragShader, GL_FRAGMENT_SHADER)
        self.shader = shaders.compileProgram(
            VERTEX_SHADER, FRAGMENT_SHADER)

        self.uniform.init()

        return self.shader

    def activate(self):
        # use shader
        glUseProgram(self.shader)

        position = 0
        texCoords = 1
        glBindAttribLocation(self.shader, position, 'position')
        glBindAttribLocation(self.shader, texCoords, 'InTexCoords')

        glVertexAttribPointer(position, 3, GL_FLOAT,
                              GL_FALSE, 20, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

        glVertexAttribPointer(texCoords, 2, GL_FLOAT,
                              GL_FALSE, 20, ctypes.c_void_p(12))
        glEnableVertexAttribArray(texCoords)

        self.texture.activate()
        self.uniform.update(self.shader)

    def deactivate(self):
        glUseProgram(0)
