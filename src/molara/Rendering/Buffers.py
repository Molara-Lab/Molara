import ctypes

from OpenGL.GL import (
    GL_ARRAY_BUFFER,
    GL_DYNAMIC_DRAW,
    GL_ELEMENT_ARRAY_BUFFER,
    GL_FALSE,
    GL_FLOAT,
    GL_STATIC_DRAW,
    glBindBuffer,
    glBindVertexArray,
    glBufferData,
    glDeleteVertexArrays,
    glEnableVertexAttribArray,
    glGenBuffers,
    glGenVertexArrays,
    glVertexAttribDivisor,
    glVertexAttribPointer,
)


def setup_vao(vertices, indices, model_matrices):
    """Sets up a vertex attribute object and binds it to the GPU.

    :param vertices: Vertices in the following order x,y,z,r,g,b,nx,ny,nz,..., where xyz are the cartesian coordinates,
        rgb are the color values [0,1], and nxnynz are the components of the normal vector.
    :type vertices: numpy.array of numpy.float32
    :param indices: Gives the connectivity of the vertices.
    :type indices: numpy.array of numpy.uint32
    :param model_matrices: Each matrix gives the transformation from object space to world.
    :type model_matrices: numpy.array of numpy.float32
    :return: Returns a bound vertex attribute object
    """
    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)

    glBindVertexArray(vao)

    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    # Vertex positions
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, vertices.itemsize * 9, ctypes.c_void_p(0))

    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, vertices.itemsize * 9, ctypes.c_void_p(12))

    glEnableVertexAttribArray(2)
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, vertices.itemsize * 9, ctypes.c_void_p(24))

    if indices is not None:
        ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    if model_matrices is not None:
        # Instance matrices
        instance_vbo = glGenBuffers(1)
        num_instances = len(model_matrices)
        glBindBuffer(GL_ARRAY_BUFFER, instance_vbo)
        glBufferData(GL_ARRAY_BUFFER, num_instances * 16 * model_matrices.itemsize, model_matrices, GL_DYNAMIC_DRAW)

        for i in range(4):
            glEnableVertexAttribArray(3 + i)
            glVertexAttribPointer(3 + i, 4, GL_FLOAT, GL_FALSE, 16 * 4, ctypes.c_void_p(i * 16))
            glVertexAttribDivisor(3 + i, 1)

    glBindVertexArray(0)

    return vao


class Vao:
    """Creates a vertex attribute object.

    :param opengl_widget: QOpenGLWidget object in order to set the opengl context to the one used in the
        QT openGL widget.
    :type opengl_widget: QOpenGLWidget
    :param vertices: Vertices in the following order x,y,z,r,g,b,nx,ny,nz,..., where xyz are the cartesian coordinates,
        rgb are the color values [0,1], and nxnynz are the components of the normal vector.
    :type vertices: numpy.array of numpy.float32
    :param indices: gives the connectivity of the vertices.
    :type indices: numpy.array of numpy.uint32, optional
    :param model_matrices: Each matrix gives the transformation from object space to world.
    :type model_matrices: numpy.array of numpy.float32, optional
    """

    def __init__(self, opengl_widget, vertices, indices=None, model_matrices=None):
        opengl_widget.makeCurrent()

        self.vertices = vertices
        self.indices = indices
        self.model_matrices = model_matrices
        self.vao = setup_vao(self.vertices, self.indices, self.model_matrices)

    def destroy(self):
        """Destroys the vertex attribute object."""
        glDeleteVertexArrays(1, self.vao)