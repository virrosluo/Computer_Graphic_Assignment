import OpenGL.GL as GL
import glfw
import numpy as np

class Pyramid:
    def __init__(self, vertices):
        self.vertices = vertices
        self.vao = GL.glGenVertexArrays(1)
        self.vbo = GL.glGenBuffers(1)

        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL.GL_STATIC_DRAW)

        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, None)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

    def draw(self):
        GL.glBindVertexArray(self.vao)
        GL.glDrawArrays(GL.GL_TRIANGLE_FAN, 0, len(self.vertices) // 3)
        GL.glBindVertexArray(0)


def setup_window(width, height, title):
    """Helper function to create a window with OpenGL context"""
    window = glfw.create_window(width, height, title, None, None)
    if not window:
        glfw.terminate()
        raise Exception(f"Failed to create {title} window.")
    
    glfw.make_context_current(window)
    GL.glClearColor(0.1, 0.1, 0.1, 1.0)
    return window

def main():
    if not glfw.init():
        return

    # Create two windows
    window_main = setup_window(640, 480, "Main Camera View")
    window_specific = setup_window(640, 480, "Specific Camera View")

    # Create a simple pyramid shape
    vertices = np.array([
        0.0,  0.5,  0.0,  # Apex
       -0.5, -0.5,  0.5,  # Base vertex 1
        0.5, -0.5,  0.5,  # Base vertex 2
        0.5, -0.5, -0.5,  # Base vertex 3
       -0.5, -0.5, -0.5   # Base vertex 4
    ], dtype=np.float32)

    glfw.make_context_current(window_main)
    pyramid1 = Pyramid(vertices)

    glfw.make_context_current(window_specific)
    pyramid2 = Pyramid(vertices)

    while not glfw.window_should_close(window_main) and not glfw.window_should_close(window_specific):
        # ----- Render main window (Main Camera) -----
        glfw.make_context_current(window_main)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        # Set up camera transformation for the main camera (e.g., looking at the specific camera)
        # Setup your main camera view matrix here
        # For simplicity, you can use an orthographic or perspective projection matrix.
        # Render pyramid (or the object representing the second camera)
        pyramid1.draw()

        glfw.swap_buffers(window_main)

        # ----- Render specific camera window -----
        glfw.make_context_current(window_specific)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        # Set up camera transformation for the specific camera (e.g., looking at the scene)
        # Setup your specific camera view matrix here
        # This is the camera's field of view.
        pyramid2.draw()  # Or draw the scene from this camera's perspective

        glfw.swap_buffers(window_specific)

        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
