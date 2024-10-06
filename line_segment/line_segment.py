from libs import transform as T
from libs.buffer import *
import OpenGL.GL as GL
import numpy as np

class LineSegments:
    def __init__(self, vert_shader, frag_shader):
        # Define vertices for line segments: pairs of points
        self.vertices = np.array([
            [0.0, 0.0, 0.0],  # Segment 1 start
            [1.0, 1.0, 1.0],  # Segment 1 end

            [-0.5, -0.5, -0.5],  # Segment 2 start
            [0.5, 0.5, 0.5],  # Segment 2 end
        ], dtype=np.float32)

        # Define colors for each point (optional)
        self.colors = np.array([
            [0.0, 1.0, 0.0],  # Color for Segment 1 start (green)
            [1.0, 0.0, 0.0],  # Color for Segment 1 end (red)

            [0.0, 0.0, 1.0],  # Color for Segment 2 start (blue)
            [1.0, 1.0, 0.0],  # Color for Segment 2 end (yellow)
        ], dtype=np.float32)

        self.vao = VAO()

        # Compile the shader
        self.shader = Shader(vertex_source=vert_shader, fragment_source=frag_shader)
        self.uma = UManager(self.shader)

    def setup(self):
        # Setup vertex buffer for points of the line segments
        self.vao.add_vbo(0, self.vertices, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None)

        # Setup color buffer for each point
        self.vao.add_vbo(1, self.colors, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None)

        # Use shader program
        GL.glUseProgram(self.shader.render_idx)

        # Upload orthogonal projection matrix
        projection = T.ortho(-1, 1, -1, 1, -1, 1)
        self.uma.upload_uniform_matrix4fv(projection, "projection", True)

    def draw(self, x_angle, y_angle, z_angle):
        self.vao.activate()
        GL.glUseProgram(self.shader.render_idx)

        # Create rotation matrix based on angles
        modelview = T.rotate(axis=(1, 0, 0), angle=x_angle) @ \
                    T.rotate(axis=(0, 1, 0), angle=y_angle) @ \
                    T.rotate(axis=(0, 0, 1), angle=z_angle)

        # Upload modelview matrix to the shader
        self.uma.upload_uniform_matrix4fv(modelview, "modelview", True)

        # Draw the line segments (4 vertices, forming 2 segments)
        GL.glDrawArrays(GL.GL_LINES, 0, len(self.vertices))

        self.vao.deactivate()