import tinyobjloader
import numpy as np
import OpenGL.GL as GL
from libs import transform as T
from libs.buffer import *
from PIL import Image
from model_interface import ModelAbstract

class ObjModel1(ModelAbstract):
    def __init__(self, vert_shader, frag_shader, model_path, texture_path):
        # Load the obj file using tinyobjloader
        self.vertices, self.texcoords, self.colors = self.load_obj(model_path)

        self.texture_path = texture_path

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
        texcoords = []
        colors = []  # Placeholder colors
        for shape in shapes:
            for idx in shape.mesh.indices:
                vertex_idx = idx.vertex_index
                texcoord_idx = idx.texcoord_index
                
                # Get vertex coordinates
                vertex = attrib.vertices[3 * vertex_idx: 3 * (vertex_idx + 1)]
                vertices.append(vertex)

                # Get texture coordinates if available
                if texcoord_idx >= 0:
                    texcoord = attrib.texcoords[2 * texcoord_idx: 2 * (texcoord_idx + 1)]
                    texcoords.append(texcoord)
                else:
                    texcoords.append([0.0, 0.0])  # Default texture coord if none provided

                colors.append([1.0, 1.0, 1.0])  # Assign default white color

        return np.array(vertices, dtype=np.float32), np.array(texcoords, dtype=np.float32), np.array(colors, dtype=np.float32)
    
    def load_texture(self, texture_file):
        # Load the image file
        img = Image.open(texture_file)
        img_data = np.array(img.convert("RGB"), dtype=np.uint8)

        # Generate and bind the texture in OpenGL
        texture_id = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, texture_id)

        # Set texture parameters
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_REPEAT)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_REPEAT)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)

        # Upload texture data
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGB, img.width, img.height, 0, GL.GL_RGB, GL.GL_UNSIGNED_BYTE, img_data)
        GL.glGenerateMipmap(GL.GL_TEXTURE_2D)

        return texture_id

    def setup(self):
        super().setup()

        self.vao.add_vbo(0, self.vertices, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None)
        self.vao.add_vbo(1, self.colors, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None)
        self.vao.add_vbo(2, self.texcoords, ncomponents=2, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None)

        GL.glUseProgram(self.shader.render_idx)

        # Bind the texture
        self.texture_id = self.load_texture(self.texture_path)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture_id)

    def draw(self, **kwargs):
        self.vao.activate()
        GL.glUseProgram(self.shader.render_idx)

        projection = T.perspective(fovy=kwargs["fovy"], aspect=kwargs["aspect"], near=kwargs["near"], far=kwargs["far"])
        self.uma.upload_uniform_matrix4fv(projection, "projection", True)

        # Apply rotation transformations
        modelview = self.get_view_matrix(**kwargs)
        self.uma.upload_uniform_matrix4fv(modelview, "modelview", True)

        # Bind the texture before drawing
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture_id)
        GL.glUniform1i(GL.glGetUniformLocation(self.shader.render_idx, "textureSampler"), 0)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, len(self.vertices))
