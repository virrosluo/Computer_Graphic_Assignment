import glfw
import numpy as np
import OpenGL.GL as GL

FRAME_PER_SECOND = 1 / 60.0

class MovingViewer:
    def __init__(self, move_speed, mouse_sentitive, width=640, height=480):

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

        self.camera_pos = np.array([0.0, 0.0, 3.0], dtype=np.float32)
        self.camera_front = np.array([0.0, 0.0, -1.0], dtype=np.float32)
        self.camera_up = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        self.yaw = -90.0  # Initialize facing forward (negative z-axis)
        self.pitch = 0.0

        self.aspect_ratio = width / height

        # Mouse state
        self.last_x = width // 2
        self.last_y = height // 2
        self.first_mouse = True

        self.move_speed = move_speed * FRAME_PER_SECOND
        self.mouse_sensitive = mouse_sentitive

        self.drawables = []

    def run(self):
        while not glfw.window_should_close(self.win):
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

            for drawable in self.drawables:
                drawable.draw(
                    camera_pos=self.camera_pos, 
                    camera_front=self.camera_front, 
                    camera_up=self.camera_up,
                    fovy=45,
                    aspect=self.aspect_ratio,
                    near=0.1,
                    far=100
                )

            glfw.swap_buffers(self.win)

            glfw.poll_events()

    def add(self, *drawables):
        glfw.make_context_current(self.win)
        for drawable in drawables:
            drawable.setup()

        self.drawables.extend(drawables)

    def move(self, key):
        if key == glfw.KEY_W:  # Move forward
            self.camera_pos += self.move_speed * self.camera_front
        elif key == glfw.KEY_S:  # Move backward
            self.camera_pos -= self.move_speed * self.camera_front
        elif key == glfw.KEY_A:  # Move left
            self.camera_pos -= np.cross(self.camera_front, self.camera_up) * self.move_speed
        elif key == glfw.KEY_D:  # Move right
            self.camera_pos += np.cross(self.camera_front, self.camera_up) * self.move_speed

    def on_mouse_move(self, _win, xpos, ypos):
        """ Handle mouse movement for changing camera direction """
        if self.first_mouse:
            self.last_x = xpos
            self.last_y = ypos
            self.first_mouse = False

        xoffset = xpos - self.last_x
        yoffset = self.last_y - ypos  # Reversed since y-coordinates go from bottom to top
        self.last_x = xpos
        self.last_y = ypos

        xoffset *= self.mouse_sensitive
        yoffset *= self.mouse_sensitive

        self.yaw += xoffset
        self.pitch += yoffset

        # Constrain pitch to avoid gimbal lock
        if self.pitch > 89.0:
            self.pitch = 89.0
        if self.pitch < -89.0:
            self.pitch = -89.0

        # Update front vector
        self.update_camera_vectors()

    def update_camera_vectors(self):
        """ Recalculate the camera front vector based on updated yaw and pitch """
        front = np.array([
            np.cos(np.radians(self.yaw)) * np.cos(np.radians(self.pitch)),
            np.sin(np.radians(self.pitch)),
            np.sin(np.radians(self.yaw)) * np.cos(np.radians(self.pitch))
        ], dtype=np.float32)
        
        self.camera_front = front / np.linalg.norm(front)

    def on_key(self, _win, key, _scancode, action, _mods):
        """ 'Q' or 'Escape' quits """
        if action == glfw.PRESS or action == glfw.REPEAT:
            if key == glfw.KEY_ESCAPE or key == glfw.KEY_Q:
                glfw.set_window_should_close(self.win, True)

            self.move(key=key)

            for drawable in self.drawables:
                if hasattr(drawable, 'key_handler'):
                    drawable.key_handler(key)