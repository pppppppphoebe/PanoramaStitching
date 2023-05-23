from OpenGL.GL import *
from OpenGL.arrays import vbo
import numpy as np

indices = [0,1,2,
    2,3,0]
indices = np.array(indices, dtype = np.uint32)

class ScreenGeometry():
    def __init__(self):

        self.mesh = None
        self.vertices = []
        self.indice = []

        self.ymin = -1
        self.ymax = 1

        self.xmin = -1
        self.xmax = 1

        self.genGrid(1,1)
        self.genMeshVAO()
        self.genMeshEBO()


        self.genMeshVAO()
        self.genMeshEBO()



    def genGrid(self,N,M):

        uvmin = 0
        uvmax = 1

        wd = (self.xmax-self.xmin) / float(M)
        hd = (self.ymax-self.ymin)  / float(N)

        w = 1 / float(M)
        h = 1 / float(N)
        
        count = 0
        for i in range(N+1):
            for j in range(M+1):
                self.vertices.extend( [self.xmin+j*wd,self.ymin+i*hd,0] )
                self.vertices.extend([uvmin+j*w,i*h])
        
        self.vertices = np.array(self.vertices, dtype=np.float32)
        for i in range(N):
            for j in range(M):
            
                bot_L = i*(M+1) + j 
                bot_R  = bot_L +1 
                up_R = (i+1)*(M+1) + (j+1) 
                up_L = (i+1) * (M+1) + j

                self.indice.extend([bot_L, bot_R, up_R])
                self.indice.extend([up_R,up_L,bot_L])
        self.indice = np.array(self.indice, dtype=np.uint32)
        self.indice = np.array(self.indice, dtype=np.uint32)
    
    def genMeshVAO(self):
        self.VAO = glGenVertexArrays(1) 
        glBindVertexArray(self.VAO)


    def genMeshEBO(self):

        self.VBO = glGenBuffers(1)
        glEnableVertexAttribArray(0);
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, len(self.vertices)*5*4,self.vertices, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, 0);

        self.EBO = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER,  self.indice, GL_STATIC_DRAW)


    def draw(self):
        # TODO Draw
        glBindVertexArray(self.VAO)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glDrawElements(GL_TRIANGLES,len(self.indice)*3, GL_UNSIGNED_INT,  None)

