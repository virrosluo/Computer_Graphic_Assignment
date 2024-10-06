from triangle.triangle import Triangle
from rectangle.rectangle import Rectangle
from point_3d.point_3d import Point3D
from vector_3d.vector_3d import Vector3D
from line_segment.line_segment import LineSegments
from tetrahedron.tetrahedron import Tetrahedron
from cube.cube import Cube
from sphere.sphere import Sphere
from cylinder.cylinder import Cylinder
from mesh_3d.mesh_3d import Mesh3D
from model.model import ObjModel
from model.model1 import ObjModel1
from viewer import Viewer

import math
import glfw

if __name__ == "__main__":

    if not glfw.init():
        raise Exception("Failed to initialize GLFW")

    view = Viewer()

    # model = Triangle(
    #     vert_shader="triangle/triangle.vert",
    #     frag_shader="triangle/triangle.frag"
    # )

    # model = Rectangle(
    #     vert_shader="rectangle/rectangle.vert",
    #     frag_shader="rectangle/rectangle.frag"
    # )

    # model = Point3D(
    #     vert_shader="point_3d/point.vert",
    #     frag_shader="point_3d/point.frag"
    # )

    # model = Vector3D(
    #     vert_shader="vector_3d/vector.vert",
    #     frag_shader="vector_3d/vector.frag"
    # )

    # model = LineSegments(
    #     vert_shader="line_segment/line_segment.vert",
    #     frag_shader="line_segment/line_segment.frag"
    # )

    # model = Tetrahedron(
    #     vert_shader="tetrahedron/tetrahedron.vert",
    #     frag_shader="tetrahedron/tetrahedron.frag"
    # )

    # model = Cube(
    #     vert_shader="cube/cube.vert",
    #     frag_shader="cube/cube.frag"
    # )

    # model = Sphere(
    #     vert_shader="sphere/sphere.vert",
    #     frag_shader="sphere/sphere.frag",
    #     N=100,
    #     r=0.5
    # )

    # model = Cylinder(
    #     vert_shader="cylinder/cylinder.vert",
    #     frag_shader="cylinder/cylinder.frag",
    #     N=100,
    #     R=1,
    #     height=2
    # )

    # model = Mesh3D(
    #     vert_shader="mesh_3d/mesh.vert",
    #     frag_shader="mesh_3d/mesh.frag",
    #     func=lambda x, y: x**2 + y**2,
    #     # func=lambda x, y: math.cos(x**2 + y) + math.sin(y**2 + x),
    #     x_range=(-1.0, 1.0),
    #     y_range=(-1.0, 1.0),
    #     resolution=50
    # )

    # model = ObjModel(
    #     model_path='model/cottage_obj.obj', 
    #     vert_shader='model/model.vert',
    #     frag_shader='model/model.frag'
    # )

    model = ObjModel1(
        model_path='model/cottage_obj.obj', 
        vert_shader='model/model1.vert',
        frag_shader='model/model1.frag',
        texture_path='model/Liberty-Pavimentazione-1.bmp'
    )
    model.setup()

    view.add(model)
    view.run()

    glfw.terminate()