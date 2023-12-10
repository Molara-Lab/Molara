cpdef bint check_sphere_intersect(float[:] sphere_origin, float radius, float[:] ray_origin, float[:], ray_direction):
    """Check if a given ray with a specified origin and direction intersects a sphere.
    
    :param sphere_origin: Origin of sphere
    :param radius: Radius of sphere
    :param ray_origin: Origin of ray
    :param ray_direction: Direction the ray points in. Need to be normalized!
    :return:
    """

