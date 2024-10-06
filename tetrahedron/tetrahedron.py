from libs import transform as T
from libs.buffer import *
import OpenGL.GL as GL
import numpy as np

class Tetrahedron:
    def __init__(self, vert_shader, frag_shader):
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

        self.vao = VAO()

        # Compile the shader
        self.shader = Shader(vertex_source=vert_shader, fragment_source=frag_shader)
        self.uma = UManager(self.shader)

    def setup(self):
        # Setup vertex buffer for the tetrahedron vertices
        self.vao.add_vbo(0, self.vertices, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None)

        # Setup color buffer for each vertex
        self.vao.add_vbo(1, self.colors[self.indices], ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None)

        # Setup the element buffer for the indices of the faces
        self.vao.add_ebo(indices=self.indices)

        # Use the shader program
        GL.glUseProgram(self.shader.render_idx)

        # Upload orthogonal projection matrix
        projection = T.ortho(-2, 2, -2, 2, -2, 2)
        self.uma.upload_uniform_matrix4fv(projection, "projection", True)

    def draw(self, x_angle, y_angle, z_angle):
        self.vao.activate()
        GL.glUseProgram(self.shader.render_idx)

        # Create a rotation matrix based on angles
        modelview = T.rotate(axis=(1, 0, 0), angle=x_angle) @ \
                    T.rotate(axis=(0, 1, 0), angle=y_angle) @ \
                    T.rotate(axis=(0, 0, 1), angle=z_angle)

        # Upload modelview matrix to the shader
        self.uma.upload_uniform_matrix4fv(modelview, "modelview", True)

        # Draw the tetrahedron using element buffer
        GL.glDrawElements(GL.GL_TRIANGLES, len(self.indices), GL.GL_UNSIGNED_INT, None)

        self.vao.deactivate()
