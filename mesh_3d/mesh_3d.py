import numpy as np
import OpenGL.GL as GL
from libs import transform as T
from libs.buffer import VAO, UManager, Shader
from model_interface import ModelAbstract

class Mesh3D(ModelAbstract):
    def __init__(self, vert_shader, frag_shader, func, x_range, y_range, resolution):
        """
        :param vert_shader: The vertex shader source
        :param frag_shader: The fragment shader source
        :param func: The function f(x, y) to visualize
        :param x_range: The range of x values (tuple: (x_min, x_max))
        :param y_range: The range of y values (tuple: (y_min, y_max))
        :param resolution: The number of points along x and y axis
        """
        self.vertices, self.indices, self.colors = self.generate_mesh(func, x_range, y_range, resolution)

        # Compile shader
        super().__init__(vert_shader, frag_shader)

    def generate_mesh(self, func, x_range, y_range, resolution):
        """
        Generate the vertices, indices, and colors for the mesh based on a given function.
        :param func: The function f(x, y) to generate the mesh for
        :param x_range: Range of x values
        :param y_range: Range of y values
        :param resolution: Number of divisions in the mesh grid
        :return: vertices, indices, and color arrays
        """
        x_min, x_max = x_range
        y_min, y_max = y_range
        x_values = np.linspace(x_min, x_max, resolution)
        y_values = np.linspace(y_min, y_max, resolution)

        vertices = []
        colors = []
        indices = []

        # Generate vertices and colors based on function
        for i, x in enumerate(x_values):
            for j, y in enumerate(y_values):
                z = func(x, y)  # Get z value from function
                vertices.append([x, y, z])
                
                # Color based on the height (z value)
                color_intensity = (z - min(x_values)) / (max(x_values) - min(x_values))
                colors.append([color_intensity, 0.0, 1.0 - color_intensity])

        for i in range(resolution - 1):
            for j in range(resolution - 1):
                top_left = i * resolution + j
                top_right = top_left + 1
                bottom_left = (i + 1) * resolution + j
                bottom_right = bottom_left + 1

                # Add two triangles to form a quad
                indices.extend([top_left, bottom_left, top_right])
                indices.extend([top_right, bottom_left, bottom_right])

        return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.int32), np.array(colors, dtype=np.float32)

    def setup(self):
        """
        Set up OpenGL buffers and shaders.
        """
        # Setup vertex buffer
        self.vao.add_vbo(0, self.vertices, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None)

        # Setup color buffer
        self.vao.add_vbo(1, self.colors, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None)

        # Setup element buffer for indices
        self.vao.add_ebo(indices=self.indices)

        # Use shader program
        GL.glUseProgram(self.shader.render_idx)

        # Upload orthogonal projection matrix
        projection = T.ortho(-2, 2, -2, 2, -2, 2)
        self.uma.upload_uniform_matrix4fv(projection, "projection", True)

    def draw(self, **kwargs):
        """
        Draw the mesh using OpenGL.
        """
        self.vao.activate()
        GL.glUseProgram(self.shader.render_idx)

        # Create rotation matrix based on angles
        modelview = self.get_view_matrix(**kwargs)

        # Upload modelview matrix to shader
        self.uma.upload_uniform_matrix4fv(modelview, "modelview", True)

        # Draw the mesh using triangles
        GL.glDrawElements(GL.GL_TRIANGLES, len(self.indices), GL.GL_UNSIGNED_INT, None)

        self.vao.deactivate()
