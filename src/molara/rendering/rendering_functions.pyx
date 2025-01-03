"""This contains the functions used in rendering written in cython for speedup."""
from molara.rendering.opengl_cython cimport *
from molara.rendering.object3d import Object3D

cpdef void _render_object(object_: Object3D):
    """Draw a 3D object.

    :param object_: Object3D object to be drawn.
    """
    if object_.wire_frame:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glBindVertexArray(object_.vao)
    if object_.buffers.ebo != -1:
        glDrawElementsInstanced(
            GL_TRIANGLES,
            object_.number_of_vertices,
            GL_UNSIGNED_INT,
            NULL,
            object_.number_of_instances,
        )
    else:
        glDrawArraysInstanced(GL_TRIANGLES, 0, object_.number_of_vertices, object_.number_of_instances)
    # if object_.wire_frame:
    #     glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    glBindVertexArray(0)