vs = """
 
      #version 330

        in vec3 position;
        in vec2 InTexCoords;

        out vec3 newColor;
        out vec2 OutTexCoords;

        varying vec4 Vertex_UV;
        void main() {
                gl_Position =  vec4(position,1.0);
                OutTexCoords = InTexCoords;
        }
"""
fs = """
         #version 330
         in vec2 OutTexCoords;
         
         out vec4 outColor;
         uniform sampler2D samplerTex;
 
        void main() {
 
           outColor = texture(samplerTex,OutTexCoords);
 
        }
"""