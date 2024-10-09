import glfw
import numpy as np
import OpenGL.GL as GL

ANGLE_PER_FRAME = 360 // 360

class RotatingViewer:
    def __init__(self, width=640, height=480):

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

        # useful message to check OpenGL renderer characteristics
        print('OpenGL', GL.glGetString(GL.GL_VERSION).decode() + ', GLSL',
              GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION).decode() +
              ', Renderer', GL.glGetString(GL.GL_RENDERER).decode())
        
        GL.glClearColor(1.0, 1.0, 1.0, 1.0)
        GL.glEnable(GL.GL_DEPTH_TEST)

        self.camera_pos = np.array([0.0, 0.0, -5.0], dtype=np.float32)
        self.camera_front = np.array([0.0, 0.0, -1.0], dtype=np.float32)
        self.camera_up = np.array([0.0, 1.0, 0.0], dtype=np.float32)

        self.aspect_ratio = width / height

        self.x_angle, self.y_angle, self.z_angle = 0, 0, 0

        self.drawables = []

    def run(self):
        while not glfw.window_should_close(self.win):
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

            for drawable in self.drawables:
                drawable.draw(
                    x_angle=self.x_angle,
                    y_angle=self.y_angle,
                    z_angle=self.z_angle,
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

    def on_key(self, _win, key, _scancode, action, _mods):
        """ 'Q' or 'Escape' quits """
        if action == glfw.PRESS or action == glfw.REPEAT:
            if key == glfw.KEY_ESCAPE:
                glfw.set_window_should_close(self.win, True)

            if key == glfw.KEY_Q:
                self.y_angle = (self.y_angle - ANGLE_PER_FRAME) % 360

            if key == glfw.KEY_E:
                self.y_angle = (self.y_angle + ANGLE_PER_FRAME) % 360

            for drawable in self.drawables:
                if hasattr(drawable, 'key_handler'):
                    drawable.key_handler(key)