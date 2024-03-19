import numpy as np
import pyrr


cpdef int select_sphere(float[:] screen_coordinates, float[:] camera_position,
                        float[:,:] view_matrix_inv, float[:,:] projection_matrix_inv, float fov, float aspect_ratio,
                        float[:,:] sphere_origins, float[:] radii):
    """Select the sphere that is closest to the screen coordinates.

    :param screen_coordinates: Screen coordinates of mouse click
    :param camera_position: Position of camera
    :param view_matrix_inv: Inverted view matrix of camera
    :param projection_matrix_inv: Inverted projection matrix of camera
    :param fov: Field of view of camera
    :param aspect_ratio: Aspect ratio of camera
    :param sphere_origins: Origins of spheres
    :param radii: Radii of spheres
    :return: Index of selected sphere or -1 if no sphere was selected
    """

    cdef int i, selected_sphere_index
    cdef float min_distance, distance, ray[3]

    min_distance = -1.0
    selected_sphere_index = -1

    # Calculate ray origin and direction
    ray[0] = screen_coordinates[0] * projection_matrix_inv[1,1] / aspect_ratio
    ray[1] = -screen_coordinates[1] * projection_matrix_inv[1,1]
    ray[2] = -1.0

    # This should not work... But it does, I do not know why :)

    ray = pyrr.matrix44.inverse(view_matrix_inv).dot(np.append(ray, 0.0))[:3]
    ray = ray / np.linalg.norm(ray)

    for i in range(sphere_origins.shape[0]):
        distance = check_sphere_intersect(sphere_origins[i,:], radii[i], camera_position, ray)
        if distance > 0:
            if min_distance < 0 or distance < min_distance:
                min_distance = distance
                selected_sphere_index = i

    return selected_sphere_index



cpdef float check_sphere_intersect(float[:] sphere_origin, float radius,
                                   float[:] ray_origin, float[:] ray_direction):
    """Check if a given ray with a specified origin and direction intersects a sphere.

    :param sphere_origin: Origin of sphere
    :param radius: Radius of sphere
    :param ray_origin: Origin of ray
    :param ray_direction: Direction the ray points in. Need to be normalized!
    :return: Distance to intersection point or -1.0 if no intersection
    """

    cdef float discriminant, dx, dy, dz, a, b, c, q, t1, t2, discriminant_sqrt

    dx = ray_origin[0] - sphere_origin[0]
    dy = ray_origin[1] - sphere_origin[1]
    dz = ray_origin[2] - sphere_origin[2]

    a = 1
    b = 2 * (ray_direction[0]*dx + ray_direction[1]*dy + ray_direction[2]*dz)
    c = dx**2 + dy**2 + dz**2 - radius**2
    discriminant = b**2 - 4 * a * c
    if discriminant < 0:
        return -1.0
    elif discriminant > 0:
        discriminant_sqrt = discriminant**0.5
        q = 1 / (2 * a)
        t1 = (-b + discriminant_sqrt) * q
        t2 = (-b - discriminant_sqrt) * q
        if t1 > t2:
            return t2
        else:
            return t1
    else:
        return -b / (2 * a)
