vs ="""
    #version 330

    in vec3 position;
    //in vec3 color;
    in vec2 InTexCoords;

    out vec3 newColor;
    out vec2 OutTexCoords;
    uniform mat4 mvp;

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
    uniform float Wd;
    uniform float Hd;

    uniform float Ws;
    uniform float Hs;

    uniform float rotation;

    uniform int line;

    uniform float fov_angle;
    uniform int isPerpestive;

    #define M_PI 3.14159265358979323846


    vec2 equirect_proj(float u, float v,float W,float H,float fov){
        float theta_alt = 2.0 * M_PI * (u - 0.5);
        float phi_alt =  M_PI * (v - 0.5);

        float x = sin(theta_alt) * cos(phi_alt);
        float y = cos(theta_alt) * cos(phi_alt);
        float z = sin(phi_alt);

        float theta = atan(z, x);
        float phi = atan(sqrt(x*x+z*z),y);
        float r = ( W ) * phi / fov;

        return vec2( 0.5 * ( W ) + r * cos(theta) ,  0.5 * ( W ) + r * sin(theta));
    }

    
    vec2 persp_proj(float nx, float ny,float fov){
        //convert to sphere
        const float ftu = 0;
        const float ftv = 0;

        float an = sin(fov / 2);
        float ak = cos(fov / 2);

        nx *= an; 
        ny *= an; 

        float u = atan(nx, ak);
        float v = atan(ny * cos(u), ak);
        u += ftu; 

        u = u / (M_PI); 
        v = v / (M_PI / 2);

        // Map from [-1, 1] to in texture space
        u = u / 2.0f+0.5;
        v = v / 2.0f+0.5;

        return vec2(u,v);
    }

    vec2 rotate_point(vec2 center,vec2 point,float angle){
        angle = angle/180*M_PI;
        float s = sin(angle);
        float c = cos(angle);

        // translate point back to origin:
        point.x -= center.x;
        point.y -= center.y;

        // rotate point
        float xnew = point.x * c - point.y * s;
        float ynew = point.x * s + point.y * c;

        // translate point back:
        point.x = xnew + center.x;
        point.y = ynew + center.y;
    
        return point;
    }

    void main() {
        float u,v =0;

        //float width = 0.5 * (fov_angle / 180);
        float width = 0.5 * (180 / 180);
        float offset = (1 - width)/2;


        if(isPerpestive==1){
            
            float nx = OutTexCoords.x-0.5;
            float ny = OutTexCoords.y-0.5;
            nx *= 2;
            ny *= 2;

            float fov = fov_angle /180 * M_PI;
            vec2 tmp = persp_proj(nx,ny,fov);

            u = tmp.x;
            v = tmp.y;
        
            //outColor = texture(samplerTex,vec2(u,v));
        }
        else{
            u = OutTexCoords.x*width + offset;
            v = OutTexCoords.y;
        }


        //convert to fisheye coordinate


        //float width = 2 * (((fov_angle - 180) / 10 ) * 0.01) + 0.5;
        //float offset = 0.25 - (((fov_angle - 180) / 10 ) * 0.01);


        float fov = fov_angle /180 * M_PI;
        //float fov = (fov_angle+0.5) /180 * M_PI;


        vec2 uv = equirect_proj(u,v,Ws,Hs,fov);

        uv.x = (uv.x / Ws);
        uv.y = (uv.y / Hs);

        vec2 center = vec2(0.5,0.5);
        vec2 uv2 = rotate_point(center,uv,rotation);

        if(line==1){
            outColor = vec4(1.0,0.0,0.0,1.0);
        }
        else{
            outColor = texture(samplerTex,uv2);
        }


    }
"""