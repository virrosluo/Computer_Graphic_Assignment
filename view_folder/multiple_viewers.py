import glfw
import copy
import glfw.GLFW
import numpy as np
import OpenGL.GL as GL
import glfw.GLFW as GLFW_CONSTANTS
from typing import List
from model_interface import ModelAbstract
from libs.transform import perspective, lookat, normalized, vec, ortho

FRAME_PER_SECOND = 1 / 60.0
3
class Camera:
    def __init__(
            self, 
            aspect_ratio,
            move_speed = 5,
            mouse_sentitive = 0.1,
            position=[0, 0, 1], 
            target=[0, 0, 0],
            up_vector=[0, 1, 0],
            fov=45, 
            near=0.1, 
            far=100,
            yaw = -90,
            pitch = 0.0
        ):
        self.position = np.array(position, dtype=np.float32)
        self.up = np.array(up_vector, dtype=np.float32)
        self.fov = fov
        self.aspect_ratio = aspect_ratio
        self.near = near
        self.far = far

        self.yaw = yaw
        self.pitch = pitch

        self.move_speed = move_speed
        self.mouse_sentitive = mouse_sentitive

        self.initialize_camera_status(target=target)

    def initialize_camera_status(self, target):
        self.front = normalized(vec(target)[:3] - vec(self.position)[:3])

    def update_camera_status(self):
        self.front = np.array([
            np.cos(np.radians(self.yaw)) * np.cos(np.radians(self.pitch)),
            np.sin(np.radians(self.pitch)),
            np.sin(np.radians(self.yaw)) * np.cos(np.radians(self.pitch))
        ], dtype=np.float32)
    
    def forward(self):
        self.position += self.move_speed * self.front * FRAME_PER_SECOND
    
    def backward(self):
        self.position -= self.move_speed * self.front * FRAME_PER_SECOND

    def go_left(self):
        self.position -= np.cross(self.front, self.up) * self.move_speed * FRAME_PER_SECOND

    def go_right(self):
        self.position += np.cross(self.front, self.up) * self.move_speed * FRAME_PER_SECOND

    def rotate_x(self, xoffset):
        self.yaw += xoffset * self.mouse_sentitive
        self.yaw = 89.0 if self.yaw > 89.0 else self.yaw

    def rotate_y(self, yoffset):
        self.pitch += yoffset * self.mouse_sentitive
        self.pitch = -89.0 if self.pitch < -89.0 else self.pitch


class CameraViewObj(ModelAbstract):
    def __init__(self, vert_shader, frag_shader, camera_info: Camera):
        super().__init__(vert_shader, frag_shader)
        self.camera_info = camera_info

        self.colors = np.array([[1, 0, 0] for _ in range(5)], dtype=np.float32)
        self.indices = np.array([
            0, 1, 2, 
            0, 1, 4,
            0, 3, 4,
            0, 2, 3,
            1, 3, 2,
            1, 4, 3
        ], dtype=np.int32)

    def update_view_object(self):
        vertices = self.get_pyramid_vertices()
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vao.vbo[0])
        GL.glBufferSubData(GL.GL_ARRAY_BUFFER, 0, vertices.nbytes, vertices)


    def setup(self):
        super().setup()

        vertices = self.get_pyramid_vertices()
        self.vao.add_vbo(0, vertices, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None, draw_type=GL.GL_DYNAMIC_DRAW)
        self.vao.add_vbo(1, self.colors[self.indices], ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None)
        self.vao.add_ebo(indices=self.indices)

    def draw(self, **kwargs):
        self.vao.activate()
        GL.glUseProgram(self.shader.render_idx)

        projection = perspective(fovy=kwargs["fovy"], aspect=kwargs["aspect"], near=kwargs["near"], far=kwargs["far"])
        self.uma.upload_uniform_matrix4fv(projection, "projection", True)

        modelview = self.get_view_matrix(**kwargs)
        self.uma.upload_uniform_matrix4fv(modelview, "modelview", True)

        GL.glDrawElements(GL.GL_TRIANGLES, len(self.indices), GL.GL_UNSIGNED_INT, None)
        self.vao.deactivate()

    def get_pyramid_vertices(self):
        distance = self.camera_info.far - self.camera_info.near

        camera_right = np.cross(self.camera_info.front, self.camera_info.up)
        camera_right /= np.linalg.norm(camera_right)

        camera_up = np.cross(camera_right, self.camera_info.front)
        camera_up /= np.linalg.norm(camera_up)

        base_height = np.tan(np.radians(self.camera_info.fov)) * distance
        base_width = base_height * self.camera_info.aspect_ratio

        apex = self.camera_info.position + self.camera_info.front * self.camera_info.near
        base_center = apex + self.camera_info.front * distance
        
        half_width = base_width / 2
        half_height = base_height / 2

        base_top_right = base_center + camera_right * half_width + camera_up * half_height
        base_top_left = base_center - camera_right * half_width + camera_up * half_height
        base_bottom_left = base_center - camera_right * half_width - camera_up * half_height
        base_bottom_right = base_center + camera_right * half_width - camera_up * half_height

        return np.asarray([
            apex,
            base_top_right,
            base_top_left,
            base_bottom_left,
            base_bottom_right
        ], dtype=np.float32)

class MultiplesView:
    def __init__(
            self, 
            vert_shader,
            frag_shader,
            move_speed=5, 
            mouse_sentitive=0.1, 
            cameras = [], 
            width=640, 
            height=480,
            generate_default_camera=True
        ):

        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MAJOR, 4)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_OPENGL_PROFILE, GLFW_CONSTANTS.GLFW_OPENGL_CORE_PROFILE)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
        # glfw.window_hint(glfw.DECORATED, GL.GL_TRUE)
        # glfw.window_hint(glfw.RESIZABLE, GL.GL_FALSE)
        
        self.main_win = glfw.create_window(width, height, "Main View", None, None)
        self.camera_win = glfw.create_window(width, height, "Camera View", None, None)

        if not self.main_win or not self.camera_win:
            raise Exception("Failed to create GLFW Window")

        glfw.make_context_current(self.main_win)
        print('Main View OpenGL', GL.glGetString(GL.GL_VERSION).decode() + ', GLSL', GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION).decode() + ', Renderer', GL.glGetString(GL.GL_RENDERER).decode())
        GL.glClearColor(1.0, 1.0, 1.0, 1.0)
        GL.glEnable(GL.GL_DEPTH_TEST)

        glfw.make_context_current(self.camera_win)
        print('Camera View OpenGL', GL.glGetString(GL.GL_VERSION).decode() + ', GLSL', GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION).decode() + ', Renderer', GL.glGetString(GL.GL_RENDERER).decode())
        GL.glClearColor(1.0, 1.0, 1.0, 1.0)
        GL.glEnable(GL.GL_DEPTH_TEST)
        
        # register event handlers
        glfw.set_key_callback(self.main_win, self.on_key)
        glfw.set_cursor_pos_callback(self.main_win, self.on_mouse_move)
        glfw.set_input_mode(self.main_win, glfw.CURSOR, glfw.CURSOR_DISABLED)

        self.aspect_ratio = width / height
        self.active_camera_idx = 0

        if generate_default_camera:
            self.cameras: List[Camera] = [Camera(
                aspect_ratio=self.aspect_ratio,
                move_speed=move_speed,
                mouse_sentitive=mouse_sentitive
            )] + cameras
        else:
            self.cameras: List[Camera] = cameras

        glfw.make_context_current(self.main_win)
        self.view_objs = [CameraViewObj(vert_shader=vert_shader, frag_shader=frag_shader, camera_info=camera) for camera in self.cameras]
        for view_obj in self.view_objs:
            view_obj.setup()
        
        self.main_drawables = []
        self.camera_drawables = []

        # Mouse state
        self.last_x = width // 2
        self.last_y = height // 2
        self.first_mouse = True

        self.move_speed = move_speed * FRAME_PER_SECOND
        self.mouse_sensitive = mouse_sentitive

    def run(self):
        while not glfw.window_should_close(self.main_win) and not glfw.window_should_close(self.camera_win):
# --------------------------------------------------------------- MAIN VIEW
            glfw.make_context_current(self.main_win)            
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

            active_camera = self.cameras[0]
            active_camera.update_camera_status()

            GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)
            for drawable in self.main_drawables:
                drawable.draw(
                    camera_pos=active_camera.position,
                    camera_front=active_camera.front, 
                    camera_up=active_camera.up,
                    fovy=active_camera.fov,
                    aspect=active_camera.aspect_ratio,
                    near=active_camera.near,
                    far=active_camera.far
                )

            GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)
            for view_obj in self.view_objs[1:]:
                view_obj.draw(
                    camera_pos=active_camera.position,
                    camera_front=active_camera.front, 
                    camera_up=active_camera.up,
                    fovy=active_camera.fov,
                    aspect=active_camera.aspect_ratio,
                    near=active_camera.near,
                    far=active_camera.far
                )

            glfw.swap_buffers(self.main_win)

# --------------------------------------------------------------- CAMERA VIEW
            glfw.make_context_current(self.camera_win)            
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

            active_camera = self.cameras[self.active_camera_idx]
            active_camera.update_camera_status()

            GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)
            for drawable in self.camera_drawables:
                drawable.draw(
                    camera_pos=active_camera.position,
                    camera_front=active_camera.front, 
                    camera_up=active_camera.up,
                    fovy=active_camera.fov,
                    aspect=active_camera.aspect_ratio,
                    near=active_camera.near,
                    far=active_camera.far
                )
            glfw.swap_buffers(self.camera_win)

# --------------------------------------------------------------- POLL EVENT
            glfw.poll_events()

    def add(self, *drawables):
        main_drawables = copy.deepcopy(drawables)
        glfw.make_context_current(self.main_win)
        for obj in main_drawables:
            obj.setup()

        glfw.make_context_current(self.camera_win)
        for obj in drawables:
            obj.setup()

        self.main_drawables.extend(main_drawables)
        self.camera_drawables.extend(drawables)

    def update_camview_obj(self):
        glfw.make_context_current(self.main_win)
        for view_obj in self.view_objs:
            view_obj.update_view_object()

    def move(self, key):
        current_camera = self.cameras[self.active_camera_idx]
        if key == glfw.KEY_W:  # Move forward
            current_camera.forward()
        elif key == glfw.KEY_S:  # Move backward
            current_camera.backward()
        elif key == glfw.KEY_A:  # Move left
            current_camera.go_left()
        elif key == glfw.KEY_D:  # Move right
            current_camera.go_right()
        
        self.update_camview_obj()

    def on_mouse_move(self, _win, xpos, ypos):
        if self.first_mouse:
            self.last_x = xpos
            self.last_y = ypos
            self.first_mouse = False

        xoffset = xpos - self.last_x
        yoffset = self.last_y - ypos
        self.last_x = xpos
        self.last_y = ypos

        current_camera = self.cameras[self.active_camera_idx]
        current_camera.rotate_x(xoffset)
        current_camera.rotate_y(yoffset)

        self.update_camview_obj()

    def swap_camera(self, key):
        if key >= glfw.KEY_0 and key <= glfw.KEY_9:
            self.active_camera_idx = key - 48

    def on_key(self, _win, key, _scancode, action, _mods):
        """ 'Q' or 'Escape' quits """
        if action == glfw.PRESS or action == glfw.REPEAT:
            if key == glfw.KEY_ESCAPE or key == glfw.KEY_Q:
                glfw.set_window_should_close(self.main_win, True)
                glfw.set_window_should_close(self.camera_win, True)

            self.move(key=key)
            self.swap_camera(key=key)

            for drawable in self.main_drawables + self.camera_drawables:
                if hasattr(drawable, 'key_handler'):
                    drawable.key_handler(key)