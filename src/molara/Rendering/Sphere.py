import numpy as np


class Sphere:
    """Creates a Sphere object, containing its vertices and indices.

    :param color: Color of the sphere.
    :type color: numpy.array of numpy.float32
    :param subdivisions: Number of subdivisions of the sphere.
    :type subdivisions: integer
    """

    def __init__(self, color, subdivisions):
        self.color = color
        self.subdivisions = subdivisions
        if color is not None and subdivisions is not None:
            vertices, indices = generate_sphere(self.color, self.subdivisions)
            self.vertices = vertices
            self.indices = indices
        else:
            self.vertices = None
            self.indices = None


class Spheres(Sphere):
    """Creates a Spheres object containing multiple spheres of the same color and the model matrices to draw multiple
    instances.

    :param color: Color of the sphere.
    :type color: numpy.array of numpy.float32
    :param subdivisions: Number of subdivisions of the sphere.
    :type subdivisions: integer
    """

    def __init__(self, color=None, subdivisions=None):
        super().__init__(color, subdivisions)
        self.model_matrices = None


def generate_sphere(color, subdivisions):
    """Calculates the vertices and indices of a sphere for a given color and number of subdivisions.

    :param color: Color of the sphere.
    :type color: numpy.array of numpy.float32
    :param subdivisions: Number of subdivisions of the sphere.
    :type subdivisions: integer
    :returns:
        - **vertices** (numpy.array of numpy.float32) - Vertices in the following order x,y,z,r,g,b,nx,ny,nz,..., where\
         xyz are the cartesian coordinates,rgb are the color values [0,1], and nxnynz are the components of the normal\
          vector.
        - **indices** (numpy.array of numpy.uint32) - Gives the connectivity of the vertices.
    """
    vertices = []
    indices = []
    normals = []

    for i in range(subdivisions + 1):
        phi = np.pi * (i / subdivisions - 0.5)
        y = np.sin(phi)

        for j in range(subdivisions * 2 + 1):
            theta = 2 * np.pi * j / (subdivisions * 2)
            x = np.cos(theta) * np.cos(phi)
            z = np.sin(theta) * np.cos(phi)

            normal = [x, y, z]
            normal /= np.linalg.norm(normal)
            normals.extend(normal)
            vertices.extend([x, y, z, color[0], color[1], color[2], normal[0], normal[1], normal[2]])
            if j < subdivisions * 2 and i < subdivisions:
                p1 = i * (subdivisions * 2 + 1) + j
                p2 = p1 + 1
                p3 = p1 + subdivisions * 2 + 1
                p4 = p3 + 1

                indices.extend([p1, p2, p3, p3, p2, p4])

    return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.uint32)
