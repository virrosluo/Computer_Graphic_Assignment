import tinyobjloader
import numpy as np
import OpenGL.GL as GL
from libs import transform as T
from libs.buffer import *
from model_interface import ModelAbstract

class ObjModel(ModelAbstract):
    def __init__(self, vert_shader, frag_shader, model_path):
        # Load the obj file using tinyobjloader
        self.vertices, self.colors = self.load_obj(model_path)

        # Setup shader, VAO, and UManager
        super().__init__(vert_shader, frag_shader)

    def load_obj(self, obj_file):
        reader = tinyobjloader.ObjReader()
        config = tinyobjloader.ObjReaderConfig()

        if not reader.ParseFromFile(obj_file, config):
            raise Exception(f"Failed to load {obj_file}: {reader.Warning() + reader.Error()}")

        attrib = reader.GetAttrib()
        shapes = reader.GetShapes()

        vertices = []
        colors = []  # Assign default colors for now
        for shape in shapes:
            for idx in shape.mesh.indices:
                vertex_idx = idx.vertex_index
                vertex = attrib.vertices[3 * vertex_idx: 3 * (vertex_idx + 1)]
                vertices.append(vertex)

                # Placeholder color (use white for now)
                colors.append([1.0, 0.0, 1.0])

        return np.array(vertices, dtype=np.float32), np.array(colors, dtype=np.float32)

    def setup(self):
        super().setup()
        
        self.vao.add_vbo(0, self.vertices, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None)
        self.vao.add_vbo(1, self.colors, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None)

        GL.glUseProgram(self.shader.render_idx)

    def draw(self, **kwargs):
        self.vao.activate()
        GL.glUseProgram(self.shader.render_idx)

        projection = T.perspective(fovy=kwargs["fovy"], aspect=kwargs["aspect"], near=kwargs["near"], far=kwargs["far"])
        self.uma.upload_uniform_matrix4fv(projection, "projection", True)

        # Apply rotation transformations
        modelview = self.get_view_matrix(**kwargs)
        self.uma.upload_uniform_matrix4fv(modelview, "modelview", True)

        GL.glDrawArrays(GL.GL_TRIANGLES, 0, len(self.vertices))
        self.vao.deactivate()
