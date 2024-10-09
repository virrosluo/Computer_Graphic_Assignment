from model_interface import ModelAbstract
import numpy as np
import OpenGL.GL as GL
import libs.transform as T

class Vector3D(ModelAbstract):
    def __init__(self, vert_shader, frag_shader):
        super().__init__(vert_shader, frag_shader)

        self.vertices = np.array([
            [0, 0, 0],
            [0.5, 0.5, 0]
        ], dtype=np.float32)

        self.colors = np.array([
            [1, 0, 0],
            [0, 1, 0]
        ], dtype=np.float32)

    def setup(self):
        super().setup()

        self.vao.add_vbo(0, self.vertices, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None)
        self.vao.add_vbo(1, self.colors, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None)

        GL.glUseProgram(self.shader.render_idx)

    def draw(self, **kwargs):
        self.vao.activate()
        GL.glUseProgram(self.shader.render_idx)

        projection = T.perspective(fovy=kwargs["fovy"], aspect=kwargs["aspect"], near=kwargs["near"], far=kwargs["far"])
        self.uma.upload_uniform_matrix4fv(projection, "projection", True)
        
        modelview = self.get_view_matrix(**kwargs)
        self.uma.upload_uniform_matrix4fv(modelview, "modelview", True)

        GL.glDrawArrays(GL.GL_LINES, 0, 2)
        self.vao.deactivate()