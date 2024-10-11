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

        X, Y = np.meshgrid(x_values, y_values)
        Z = func(X, Y)

        vertices = np.column_stack((X.flatten(), Y.flatten(), Z.flatten()))
        
        z_min = np.min(Z)
        z_max = np.max(Z)
        color_intensities = (Z - z_min) / (z_max - z_min)
        colors = np.column_stack((color_intensities.flatten(), 
                                np.zeros_like(color_intensities.flatten()), 
                                1.0 - color_intensities.flatten()))

        vertex_indices = np.arange(resolution * resolution).reshape((resolution, resolution))

        top_left_indices = vertex_indices[:-1, :-1].flatten()
        top_right_indices = vertex_indices[:-1, 1:].flatten()
        bottom_left_indices = vertex_indices[1:, :-1].flatten()
        bottom_right_indices = vertex_indices[1:, 1:].flatten()

        triangle_1 = np.column_stack((top_left_indices, bottom_left_indices, top_right_indices))
        triangle_2 = np.column_stack((top_right_indices, bottom_left_indices, bottom_right_indices))

        indices = np.vstack((triangle_1, triangle_2)).flatten()

        return np.asarray(vertices, dtype=np.float32), np.asarray(indices, dtype=np.int32), np.asarray(colors, dtype=np.float32)

    def setup(self):
        """
        Set up OpenGL buffers and shaders.
        """
        super().setup()

        # Setup vertex buffer
        self.vao.add_vbo(0, self.vertices, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None)

        # Setup color buffer
        self.vao.add_vbo(1, self.colors, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None)

        # Setup element buffer for indices
        self.vao.add_ebo(indices=self.indices)

        # Use shader program
        GL.glUseProgram(self.shader.render_idx)

    def draw(self, **kwargs):
        """
        Draw the mesh using OpenGL.
        """
        self.vao.activate()
        GL.glUseProgram(self.shader.render_idx)

        projection = T.perspective(fovy=kwargs["fovy"], aspect=kwargs["aspect"], near=kwargs["near"], far=kwargs["far"])
        self.uma.upload_uniform_matrix4fv(projection, "projection", True)

        # Create rotation matrix based on angles
        modelview = self.get_view_matrix(**kwargs)
        self.uma.upload_uniform_matrix4fv(modelview, "modelview", True)

        # Draw the mesh using triangles
        GL.glDrawElements(GL.GL_TRIANGLES, len(self.indices), GL.GL_UNSIGNED_INT, None)

        self.vao.deactivate()
