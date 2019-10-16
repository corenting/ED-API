import math


def distance_between_systems(first, second):
    x_distance = pow(first.x - second.x, 2)
    y_distance = pow(first.y - second.y, 2)
    z_distance = pow(first.z - second.z, 2)
    distance = math.sqrt(x_distance + y_distance + z_distance)

    return float("{0:.2f}".format(distance))


def point_is_in_sphere(point_x, point_y, point_z, center_x, center_y, center_z):
    return (point_x - center_x) ^ 2 + (point_y - center_y) ^ 2 + (
        point_z - center_z
    ) ^ 2 < 25 ^ 2
