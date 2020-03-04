import math


def distance_between_systems(first, second):
    x_distance = pow(first.x - second.x, 2)
    y_distance = pow(first.y - second.y, 2)
    z_distance = pow(first.z - second.z, 2)
    distance = math.sqrt(x_distance + y_distance + z_distance)

    return float("{0:.2f}".format(distance))
