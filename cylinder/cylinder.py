import numpy as np
import OpenGL.GL as GL
from libs import transform as T
from libs.buffer import VAO, UManager, Shader
from model_interface import ModelAbstract

class Cylinder(ModelAbstract):
    def __init__(self, vert_shader, frag_shader, N, R=1, height=2):
        """
        Initialize the cylinder.
        :param vert_shader: The vertex shader source
        :param frag_shader: The fragment shader source
        :param N: Number of subdivisions (slices)
        :param R: Radius of the cylinder
        :param height: Height of the cylinder
        """
        self.N = N
        self.R = R
        self.height = height

        # Generate vertices
        self.vertices, self.top_vertices, self.bottom_vertices = self.generate_vertices()

        # Generate colors (optional, can be modified)
        self.colors = np.linspace(
            start=(0, 0, 0),  # Start color (blue)
            stop=(1, 1, 1),   # End color (red)
            num=len(self.vertices),
        ).reshape((-1, 3))

        self.top_colors = np.ones(shape=(len(self.top_vertices), 3), dtype=np.float32) * np.array([[1, 0, 1]])
        self.bottom_colors = np.ones(shape=(len(self.bottom_vertices), 3), dtype=np.float32) * np.array([[1, 0, 1]])

        # Generate indices for the cylinder
        self.indices = self.generate_indices()

        # Initialize VAO and shader
        super().__init__(vert_shader, frag_shader)
        self.vao_top = VAO()
        self.vao_bottom = VAO()

    def generate_vertices(self):
        """
        Generate vertices for the top and bottom circles, and the side of the cylinder.
        :return: A flattened list of vertices for the cylinder.
        """
        top_center = [0, self.height / 2, 0]  # Center of the top circle
        bottom_center = [0, -self.height / 2, 0]  # Center of the bottom circle

        vertices = [top_center, bottom_center]  # Starting with the top and bottom centers
        top_vertices = [top_center]
        bottom_vertices = [bottom_center]
        

        # Create the vertices for the top and bottom circles and the sides
        theta_list = np.linspace(0, 2 * np.pi, self.N)

        for theta in theta_list:
            # Top circle
            x_top = self.R * np.cos(theta)
            z_top = self.R * np.sin(theta)
            vertices.append([x_top, self.height / 2, z_top])
            top_vertices.append([x_top, self.height / 2, z_top])

            # Bottom circle
            x_bottom = self.R * np.cos(theta)
            z_bottom = self.R * np.sin(theta)
            vertices.append([x_bottom, -self.height / 2, z_bottom])
            bottom_vertices.append([x_bottom, -self.height / 2, z_bottom])

        return np.array(vertices, dtype=np.float32), np.array(top_vertices, dtype=np.float32), np.array(bottom_vertices, dtype=np.float32)

    def generate_indices(self):
        """
        Generate indices for drawing the cylinder with GL_TRIANGLE_STRIP.
        :return: Indices for rendering the cylinder.
        """
        indices = []

        # Triangle strip for the side of the cylinder
        for i in range(2, len(self.vertices) - 2, 2):
            indices.append(i)       # Top vertex
            indices.append(i + 1)   # Bottom vertex

        # Closing the cylinder
        indices.append(2)       # Close the top vertex
        indices.append(3)       # Close the bottom vertex

        return np.array(indices, dtype=np.int32)

    def setup(self):
        """
        Set up the OpenGL buffers and shaders.
        """
        # Setup vertex buffer for the cylinder vertices
        self.vao.add_vbo(0, self.vertices, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None)
        self.vao_top.add_vbo(0, self.top_vertices, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None)
        self.vao_bottom.add_vbo(0, self.bottom_vertices, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None)

        # Setup color buffer for each vertex
        self.vao.add_vbo(1, self.colors, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None)
        self.vao_top.add_vbo(1, self.top_colors, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None)
        self.vao_bottom.add_vbo(1, self.bottom_colors, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None)

        # Setup the element buffer for the triangle strip indices
        self.vao.add_ebo(indices=self.indices)

        # Use the shader program
        GL.glUseProgram(self.shader.render_idx)

        # Upload orthogonal projection matrix
        projection = T.ortho(-2, 2, -2, 2, -2, 2)
        self.uma.upload_uniform_matrix4fv(projection, "projection", True)

    def draw(self, **kwargs):
        """
        Draw the cylinder using OpenGL.
        :param x_angle: Rotation angle around the x-axis
        :param y_angle: Rotation angle around the y-axis
        :param z_angle: Rotation angle around the z-axis
        """
        self.vao.activate()
        GL.glUseProgram(self.shader.render_idx)

        # Create a rotation matrix based on angles
        modelview = self.get_view_matrix(**kwargs)
        self.uma.upload_uniform_matrix4fv(modelview, "modelview", True)

        # Draw the cylinder using element buffer and triangle strip
        GL.glDrawElements(GL.GL_TRIANGLE_STRIP, len(self.indices), GL.GL_UNSIGNED_INT, None)

        self.vao.deactivate()

        self.vao_top.activate()
        GL.glUseProgram(self.shader.render_idx)
        GL.glDrawArrays(GL.GL_TRIANGLE_FAN, 0, len(self.top_vertices))
        self.vao_top.deactivate()

        self.vao_bottom.activate()
        GL.glUseProgram(self.shader.render_idx)
        GL.glDrawArrays(GL.GL_TRIANGLE_FAN, 0, len(self.bottom_vertices))
        self.vao_bottom.deactivate()
