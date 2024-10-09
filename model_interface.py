from libs import transform as T
from libs.buffer import *
import OpenGL.GL as GL

class ModelAbstract:
    def __init__(self, vert_shader, frag_shader):
        self.vert_shader = vert_shader
        self.frag_shader = frag_shader

    def setup(self):
        self.vao = VAO()
        self.shader = Shader(vertex_source=self.vert_shader, fragment_source=self.frag_shader)
        self.uma = UManager(self.shader)

    def get_view_matrix(self, **kwargs):
        modelview = T.lookat(eye=kwargs["camera_pos"], target=kwargs["camera_front"], up=kwargs["camera_up"])
        return modelview
    
    # def get_view_matrix(self, **kwargs):
    #     return T.rotate(axis=(1, 0, 0), angle=kwargs["x_angle"]) @ \
    #            T.rotate(axis=(0, 1, 0), angle=kwargs["y_angle"]) @ \
    #             T.rotate(axis=(0, 0, 1), angle=kwargs["z_angle"])


    def draw(self, **kwargs):
        pass