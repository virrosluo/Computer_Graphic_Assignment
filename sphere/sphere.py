import numpy as np
from model_interface import ModelAbstract

from libs import transform as T
from libs.buffer import *

class Sphere(ModelAbstract):
    def __init__(self, vert_shader, frag_shader, r=1, N=15):
        super().__init__(vert_shader, frag_shader)
        self.N = N
        self.r = r
        
        self.vertices = self.generate_vertices() / 2
        self.colors = np.ones(shape=(self.vertices.shape[0], 3)).astype(np.float32) * np.array([[1, 0, 1]])
        self.indices = self.generate_triangle_strip_indices(N)

    def generate_vertices(self):
        theta_step = 2 * np.pi / self.N
        phi_step = np.pi / self.N

        vertices = []
        for i in range(self.N + 1):
            phi = np.pi / 2 - i * phi_step
            z = np.sin(phi)
            for j in range(self.N + 1):
                theta = j * theta_step
                x = np.cos(phi) * np.cos(theta)
                y = np.cos(phi) * np.sin(theta)
                vertices.append([x, y, z])

        return np.array(vertices, dtype=np.float32)

    
    def generate_triangle_strip_indices(self, N):
        indices = []
        k1, k2 = 0, 0

        for i in range(self.N):
            k1 = i * (self.N + 1)  # beginning of current stack
            k2 = k1 + self.N + 1   # beginning of next stack

            for j in range(self.N):
                # 2 triangles per sector excluding first and last stacks
                # k1 => k2 => k1+1
                if i != 0:
                    indices.append(k1)
                    indices.append(k2)
                    indices.append(k1 + 1)

                # k1+1 => k2 => k2+1
                if i != (self.N - 1):
                    indices.append(k1 + 1)
                    indices.append(k2)
                    indices.append(k2 + 1)

                k1 += 1
                k2 += 1

        return np.array(indices, dtype=np.int32)
    
    def setup(self):
        self.vao.add_vbo(0, self.vertices, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None)
        self.vao.add_vbo(1, self.colors, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None)

        self.vao.add_ebo(self.indices)

        GL.glUseProgram(self.shader.render_idx)
        
        projection = T.ortho(-1, 1, -1, 1, -10, 10)
        self.uma.upload_uniform_matrix4fv(projection, 'projection', True)

    def draw(self, **kwargs):
        self.vao.activate()
        GL.glUseProgram(self.shader.render_idx)

        modelview = self.get_view_matrix(**kwargs)
        self.uma.upload_uniform_matrix4fv(modelview, "modelview", True)

        GL.glDrawElements(GL.GL_TRIANGLE_STRIP, len(self.indices) * 2, GL.GL_UNSIGNED_INT, None)