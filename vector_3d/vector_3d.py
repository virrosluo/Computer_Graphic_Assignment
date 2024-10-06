from libs import transform as T
from libs.buffer import *
import OpenGL.GL as GL

class Vector3D:
    def __init__(self, vert_shader, frag_shader):
        self.vertices = np.array([
            [0, 0, 0],
            [0.5, 0.5, 0]
        ], dtype=np.float32)

        self.colors = np.array([
            [1, 0, 0],
            [0, 1, 0]
        ], dtype=np.float32)

        self.vao = VAO()

        self.shader = Shader(vertex_source=vert_shader, fragment_source=frag_shader)
        self.uma = UManager(self.shader)

    def setup(self):
        self.vao.add_vbo(0, self.vertices, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None)
        self.vao.add_vbo(1, self.colors, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None)

        GL.glUseProgram(self.shader.render_idx)

        projection = T.ortho(-1, 1, -1, 1, -1, 1)        
        self.uma.upload_uniform_matrix4fv(projection, "projection", True)

    def draw(self, x_angle, y_angle, z_angle):
        self.vao.activate()
        GL.glUseProgram(self.shader.render_idx)

        modelview = T.rotate(axis=(1, 0, 0), angle=x_angle) @ T.rotate(axis=(0, 1, 0), angle=y_angle) @ T.rotate(axis=(0, 0, 1), angle=z_angle)
        self.uma.upload_uniform_matrix4fv(modelview, "modelview", True)

        GL.glDrawArrays(GL.GL_LINES, 0, 2)