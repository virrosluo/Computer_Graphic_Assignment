from libs import transform as T
from libs.buffer import *
import OpenGL.GL as GL
import numpy as np
from model_interface import ModelAbstract

class Cube(ModelAbstract):
    def __init__(self, vert_shader, frag_shader):
        # Define vertices for the cube
        self.vertices = np.array([
            [-1.0, -1.0, -1.0],  # Vertex 0
            [ 1.0, -1.0, -1.0],  # Vertex 1
            [ 1.0,  1.0, -1.0],  # Vertex 2
            [-1.0,  1.0, -1.0],  # Vertex 3
            [-1.0, -1.0,  1.0],  # Vertex 4
            [ 1.0, -1.0,  1.0],  # Vertex 5
            [ 1.0,  1.0,  1.0],  # Vertex 6
            [-1.0,  1.0,  1.0],  # Vertex 7
        ], dtype=np.float32)

        # Define the color for each vertex (optional)
        self.colors = np.array([
            [1.0, 0.0, 0.0],  # Color for Vertex 0 (red)
            [0.0, 1.0, 0.0],  # Color for Vertex 1 (green)
            [0.0, 0.0, 1.0],  # Color for Vertex 2 (blue)
            [1.0, 1.0, 0.0],  # Color for Vertex 3 (yellow)
            [1.0, 0.0, 1.0],  # Color for Vertex 4 (magenta)
            [0.0, 1.0, 1.0],  # Color for Vertex 5 (cyan)
            [1.0, 1.0, 1.0],  # Color for Vertex 6 (white)
            [0.5, 0.5, 0.5],  # Color for Vertex 7 (gray)
        ], dtype=np.float32)

        # Define indices for the triangular faces
        self.indices = np.array([
            0, 1, 2, 0, 2, 3,  # Back face
            4, 5, 6, 4, 6, 7,  # Front face
            0, 3, 7, 0, 7, 4,  # Left face
            1, 5, 6, 1, 6, 2,  # Right face
            3, 2, 6, 3, 6, 7,  # Top face
            0, 1, 5, 0, 5, 4,  # Bottom face
        ], dtype=np.int32)

        super().__init__(vert_shader, frag_shader)

    def setup(self):
        # Setup vertex buffer for the cube vertices
        self.vao.add_vbo(0, self.vertices, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None)

        # Setup color buffer for each vertex
        self.vao.add_vbo(1, self.colors, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None)

        # Setup the element buffer for the indices of the faces
        self.vao.add_ebo(indices=self.indices)

        # Use the shader program
        GL.glUseProgram(self.shader.render_idx)

        # Upload orthogonal projection matrix
        projection = T.ortho(-2, 2, -2, 2, -2, 2)
        self.uma.upload_uniform_matrix4fv(projection, "projection", True)

    def draw(self, **kwargs):
        self.vao.activate()
        GL.glUseProgram(self.shader.render_idx)

        # Create a rotation matrix based on angles
        modelview = self.get_view_matrix(**kwargs)
        self.uma.upload_uniform_matrix4fv(modelview, "modelview", True)

        # Draw the cube using element buffer
        GL.glDrawElements(GL.GL_TRIANGLES, len(self.indices), GL.GL_UNSIGNED_INT, None)

        self.vao.deactivate()
