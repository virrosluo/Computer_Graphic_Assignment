from libs import transform as T
from libs.buffer import *
import OpenGL.GL as GL
from model_interface import ModelAbstract

class Point3D(ModelAbstract):
    def __init__(self, vert_shader, frag_shader):
        self.vertices = np.array([
            [0.5, 0.5, 1],
        ], dtype=np.float32)

        self.colors = np.array([
            [1, 0, 0],
        ], dtype=np.float32)

        super().__init__(vert_shader, frag_shader)

    def setup(self):
        self.vao.add_vbo(0, self.vertices, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None)
        self.vao.add_vbo(1, self.colors, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None)

        GL.glUseProgram(self.shader.render_idx)

        projection = T.ortho(-1, 1, -1, 1, -2, 2)        
        self.uma.upload_uniform_matrix4fv(projection, "projection", True)

    def draw(self, **kwargs):
        self.vao.activate()
        GL.glUseProgram(self.shader.render_idx)

        GL.glPointSize(20)

        modelview = self.get_view_matrix(**kwargs)
        self.uma.upload_uniform_matrix4fv(modelview, "modelview", True)

        GL.glDrawArrays(GL.GL_POINTS, 0, 1)
        self.vao.deactivate()