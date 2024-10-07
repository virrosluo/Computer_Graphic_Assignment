import glfw
import numpy as np
import OpenGL.GL as GL
from typing import List
from libs.transform import perspective, lookat, normalized, vec

FRAME_PER_SECOND = 1 / 60.0

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

class MultiplesView:
    def __init__(
            self, 
            move_speed=5, 
            mouse_sentitive=0.1, 
            cameras = [], 
            width=640, 
            height=480,
            generate_default_camera=True
        ):

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.RESIZABLE, False)
        
        self.win = glfw.create_window(width, height, "Viewer", None, None)

        if not self.win:
            raise Exception("Failed to create GLFW Window")
        
        # make win's OpenGL context current; no OpenGL calls can happen before
        glfw.make_context_current(self.win)

        # register event handlers
        glfw.set_key_callback(self.win, self.on_key)
        glfw.set_cursor_pos_callback(self.win, self.on_mouse_move)
        glfw.set_input_mode(self.win, glfw.CURSOR, glfw.CURSOR_DISABLED)

        # useful message to check OpenGL renderer characteristics
        print('OpenGL', GL.glGetString(GL.GL_VERSION).decode() + ', GLSL',
              GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION).decode() +
              ', Renderer', GL.glGetString(GL.GL_RENDERER).decode())
        
        GL.glClearColor(1.0, 1.0, 1.0, 1.0)
        GL.glEnable(GL.GL_DEPTH_TEST)

        self.drawables = []

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

        print(len(self.cameras))

        # Mouse state
        self.last_x = width // 2
        self.last_y = height // 2
        self.first_mouse = True

        self.move_speed = move_speed * FRAME_PER_SECOND
        self.mouse_sensitive = mouse_sentitive

    def run(self):
        while not glfw.window_should_close(self.win):
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

            active_camera = self.cameras[self.active_camera_idx]
            active_camera.update_camera_status()

            for drawable in self.drawables:
                drawable.draw(
                    camera_pos=active_camera.position,
                    camera_front=active_camera.front, 
                    camera_up=active_camera.up
                )

            glfw.swap_buffers(self.win)
            glfw.poll_events()

    def add(self, *drawables):
        self.drawables.extend(drawables)

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

    def swap_camera(self, key):
        if key >= glfw.KEY_0 and key <= glfw.KEY_9:
            self.active_camera_idx = key - 48

    def on_key(self, _win, key, _scancode, action, _mods):
        """ 'Q' or 'Escape' quits """
        if action == glfw.PRESS or action == glfw.REPEAT:
            if key == glfw.KEY_ESCAPE or key == glfw.KEY_Q:
                glfw.set_window_should_close(self.win, True)

            self.move(key=key)
            self.swap_camera(key=key)

            for drawable in self.drawables:
                if hasattr(drawable, 'key_handler'):
                    drawable.key_handler(key)