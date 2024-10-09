from model_interface import ModelAbstract
import OpenGL.GL as GL
import numpy as np
import libs.transform as T

class Tetrahedron(ModelAbstract):
    def __init__(self, vert_shader, frag_shader):
        super().__init__(vert_shader, frag_shader)

        # Define vertices for the tetrahedron
        self.vertices = np.array([
            [0, 0, 0],      # Vertex 0
            [0, 0, 1],    # Vertex 1
            [1, 0, 0],    # Vertex 2
            [0, 1, 0],    # Vertex 3
        ], dtype=np.float32)

        # Define the color for each vertex
        self.colors = np.array([
            [1.0, 0.0, 0.0],  # Color for Vertex 0 (red)
            [0.0, 1.0, 0.0],  # Color for Vertex 1 (green)
            [0.0, 0.0, 1.0],  # Color for Vertex 2 (blue)
            [1.0, 1.0, 0.0],  # Color for Vertex 3 (yellow)
        ], dtype=np.float32)

        # Define indices for the triangular faces
        self.indices = np.array([0, 1, 2, 0, 1, 3, 0, 3, 2, 1, 2, 3], dtype=np.int32)

    def setup(self):
        super().setup()

        # Setup vertex buffer for the tetrahedron vertices
        self.vao.add_vbo(0, self.vertices, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None)

        # Setup color buffer for each vertex
        self.vao.add_vbo(1, self.colors[self.indices], ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None)

        # Setup the element buffer for the indices of the faces
        self.vao.add_ebo(indices=self.indices)

    def draw(self, **kwargs):
        self.vao.activate()
        GL.glUseProgram(self.shader.render_idx)

        projection = T.perspective(fovy=kwargs["fovy"], aspect=kwargs["aspect"], near=kwargs["near"], far=kwargs["far"])
        self.uma.upload_uniform_matrix4fv(projection, "projection", True)

        modelview = self.get_view_matrix(**kwargs)
        self.uma.upload_uniform_matrix4fv(modelview, "modelview", True)

        GL.glDrawElements(GL.GL_TRIANGLES, len(self.indices), GL.GL_UNSIGNED_INT, None)
        self.vao.deactivate()