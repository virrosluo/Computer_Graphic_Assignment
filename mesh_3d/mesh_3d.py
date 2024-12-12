import numpy as np
import OpenGL.GL as GL
from sphere.sphere import Sphere
from libs import transform as T
from model_interface import ModelAbstract

import torch
import random

class SphereObj(Sphere):
    def __init__(self, vert, frag, r=0.5, N=20):
        super().__init__(vert, frag, r = r, N=N)

    def setup(self):
        ModelAbstract.setup(self)

        self.vao.add_vbo(0, self.vertices, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None, draw_type=GL.GL_DYNAMIC_DRAW)
        self.vao.add_vbo(1, self.colors, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None)
        self.vao.add_ebo(self.indices)

    def update_position(self, current_position):
        vertices = self.vertices + np.asarray([current_position], dtype=np.float32) + np.asarray([[0, 0, self.r]], dtype=np.float32)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vao.vbo[0])
        GL.glBufferSubData(GL.GL_ARRAY_BUFFER, 0, vertices.nbytes, vertices)
    
    def draw(self, **kwargs):
        self.vao.activate()
        GL.glUseProgram(self.shader.render_idx)

        self.update_position(current_position=kwargs["position"])

        projection = T.perspective(fovy=kwargs["fovy"], aspect=kwargs["aspect"], near=kwargs["near"], far=kwargs["far"])
        self.uma.upload_uniform_matrix4fv(projection, "projection", True)

        modelview = self.get_view_matrix(**kwargs)
        self.uma.upload_uniform_matrix4fv(modelview, "modelview", True)

        GL.glDrawElements(GL.GL_TRIANGLE_STRIP, len(self.indices) * 2, GL.GL_UNSIGNED_INT, None)

class Mesh3D(ModelAbstract):
    def __init__(self, vert_shader, frag_shader, func, x_range, y_range, resolution, lr=0.0001):
        """
        :param vert_shader: The vertex shader source
        :param frag_shader: The fragment shader source
        :param func: The function f(x, y) to visualize
        :param x_range: The range of x values (tuple: (x_min, x_max))
        :param y_range: The range of y values (tuple: (y_min, y_max))
        :param resolution: The number of points along x and y axis
        """
        # Compile shader
        super().__init__(vert_shader, frag_shader)

        self.vertices, self.indices, self.colors = self.generate_mesh(func, x_range, y_range, resolution)

        self.sphere_obj = SphereObj(vert=vert_shader, frag=frag_shader, r=0.2, N=20)

        self.func = func
        self.lr = lr

        # init_vars = [random.uniform(-1, 1), random.uniform(-1, 1)]
        init_vars = [0.5, 0]
        self.positions = [init_vars]
        self.variables = torch.tensor(
            init_vars, 
            requires_grad=True,
            dtype=torch.float32
        )

    def generate_mesh(self, func, x_range, y_range, resolution):
        """
        Generate the vertices, indices, and colors for the mesh based on a given function using PyTorch tensors.
        :param func: The function f(x, y) to generate the mesh for
        :param x_range: Range of x values
        :param y_range: Range of y values
        :param resolution: Number of divisions in the mesh grid
        :return: vertices, indices, and color tensors
        """
        x_min, x_max = x_range
        y_min, y_max = y_range

        x_values = torch.linspace(x_min, x_max, resolution)
        y_values = torch.linspace(y_min, y_max, resolution)

        X, Y = torch.meshgrid(x_values, y_values, indexing='ij')
        Z = func(X, Y)

        vertices = torch.column_stack((X.flatten(), Y.flatten(), Z.flatten()))

        z_min = torch.min(Z)
        z_max = torch.max(Z)
        color_intensities = (Z - z_min) / (z_max - z_min)

        colors = torch.column_stack((
            color_intensities.flatten(), 
            torch.zeros_like(color_intensities.flatten()), 
            1.0 - color_intensities.flatten()
        ))

        vertex_indices = torch.arange(resolution * resolution, dtype=torch.int32).reshape((resolution, resolution))

        top_left_indices = vertex_indices[:-1, :-1].flatten()
        top_right_indices = vertex_indices[:-1, 1:].flatten()
        bottom_left_indices = vertex_indices[1:, :-1].flatten()
        bottom_right_indices = vertex_indices[1:, 1:].flatten()

        triangle_1 = torch.column_stack((top_left_indices, bottom_left_indices, top_right_indices))
        triangle_2 = torch.column_stack((top_right_indices, bottom_left_indices, bottom_right_indices))

        indices = torch.vstack((triangle_1, triangle_2)).flatten()
        return np.asarray(vertices.to(torch.float32)), np.asarray(indices.to(torch.int32)), np.asarray(colors.to(torch.float32))

    def setup(self):
        """
        Set up OpenGL buffers and shaders.
        """
        super().setup()

        self.vao.add_vbo(0, self.vertices, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None)
        self.vao.add_vbo(1, self.colors, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None)
        self.vao.add_ebo(indices=self.indices)

        self.sphere_obj.setup()

    def draw(self, **kwargs):
        """
        Draw the mesh using OpenGL.
        """
        self.variables.grad = None
        z = self.func(self.variables[0], self.variables[1])
        z.backward()

        with torch.no_grad():
            self.variables -= self.lr * self.variables.grad

            self.sphere_obj.draw(position=[
                self.variables[0].tolist(), 
                self.variables[1].tolist(), 
                self.func(self.variables[0], self.variables[1])
            ], **kwargs)

        self.vao.activate()
        GL.glUseProgram(self.shader.render_idx)

        projection = T.perspective(fovy=kwargs["fovy"], aspect=kwargs["aspect"], near=kwargs["near"], far=kwargs["far"])
        self.uma.upload_uniform_matrix4fv(projection, "projection", True)

        # Create rotation matrix based on angles
        modelview = self.get_view_matrix(**kwargs)
        self.uma.upload_uniform_matrix4fv(modelview, "modelview", True)
        
        self.uma.upload_uniform_vector3fv(kwargs["camera_pos"], "cameraPos")
        self.uma.upload_uniform_scalar1f(kwargs["far"], "maxDistance")

        # Draw the mesh using triangles
        GL.glDrawElements(GL.GL_TRIANGLES, len(self.indices), GL.GL_UNSIGNED_INT, None)

        self.vao.deactivate()
