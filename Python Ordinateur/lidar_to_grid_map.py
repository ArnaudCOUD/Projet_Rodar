"""
LIDAR to 2D grid map example

author: Erno Horvath, Csaba Hajdu based on Atsushi Sakai's scripts
"""

import math
from collections import deque

import matplotlib.pyplot as plt
import numpy as np

EXTEND_AREA = 1.0


def donnee_read(donnee):    
    """
    Reading LIDAR laser beams (angles and corresponding distance data)
    """
    angles = []
    distances = []
    for key, value in donnee.items():
        angles.append(math.radians(key))
        distances.append(value / 3000)
    angles = np.array(angles)
    distances = np.array(distances)
    return angles, distances


def bresenham(start, end):
    """
    Implementation of Bresenham's line drawing algorithm
    See en.wikipedia.org/wiki/Bresenham's_line_algorithm
    Bresenham's Line Algorithm
    Produces a np.array from start and end (original from roguebasin.com)
    >>> points1 = bresenham((4, 4), (6, 10))
    >>> print(points1)
    np.array([[4,4], [4,5], [5,6], [5,7], [5,8], [6,9], [6,10]])
    """
    # setup initial conditions
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1
    is_steep = abs(dy) > abs(dx)  # determine how steep the line is
    if is_steep:  # rotate line
        x1, y1 = y1, x1
        x2, y2 = y2, x2
    # swap start and end points if necessary and store swap state
    swapped = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        swapped = True
    dx = x2 - x1  # recalculate differentials
    dy = y2 - y1  # recalculate differentials
    error = int(dx / 2.0)  # calculate error
    y_step = 1 if y1 < y2 else -1
    # iterate over bounding box generating points between start and end
    y = y1
    points = []
    for x in range(x1, x2 + 1):
        coord = [y, x] if is_steep else (x, y)
        points.append(coord)
        error -= abs(dy)
        if error < 0:
            y += y_step
            error += dx
    if swapped:  # reverse the list if the coordinates were swapped
        points.reverse()
    points = np.array(points)
    return points


def calc_grid_map_config(ox, oy, xy_resolution):
    """
    Calculates the size, and the maximum distances according to the the
    measurement center
    """
    min_x = round(min(ox) - EXTEND_AREA / 2.0)
    min_y = round(min(oy) - EXTEND_AREA / 2.0)
    max_x = round(max(ox) + EXTEND_AREA / 2.0)
    max_y = round(max(oy) + EXTEND_AREA / 2.0)
    xw = int(round((max_x - min_x) / xy_resolution))
    yw = int(round((max_y - min_y) / xy_resolution))
    print("The grid map is ", xw, "x", yw, ".")
    return min_x, min_y, max_x, max_y, xw, yw


def atan_zero_to_twopi(y, x):
    angle = math.atan2(y, x)
    if angle < 0.0:
        angle += math.pi * 2.0
    return angle


def init_flood_fill(center_point, obstacle_points, xy_points, min_coord,
                    xy_resolution):
    """
    center_point: center point
    obstacle_points: detected obstacles points (x,y)
    xy_points: (x,y) point pairs
    """
    center_x, center_y = center_point
    prev_ix, prev_iy = center_x - 1, center_y
    ox, oy = obstacle_points
    xw, yw = xy_points
    min_x, min_y = min_coord
    occupancy_map = (np.ones((xw, yw))) * 0.5
    for (x, y) in zip(ox, oy):
        # x coordinate of the the occupied area
        ix = int(round((x - min_x) / xy_resolution))
        # y coordinate of the the occupied area
        iy = int(round((y - min_y) / xy_resolution))
        free_area = bresenham((prev_ix, prev_iy), (ix, iy))
        for fa in free_area:
            occupancy_map[fa[0]][fa[1]] = 0  # free area 0.0
        prev_ix = ix
        prev_iy = iy
    return occupancy_map


def flood_fill(center_point, occupancy_map):
    """
    center_point: starting point (x,y) of fill
    occupancy_map: occupancy map generated from Bresenham ray-tracing
    """
    # Fill empty areas with queue method
    sx, sy = occupancy_map.shape
    fringe = deque()
    fringe.appendleft(center_point)
    while fringe:
        n = fringe.pop()
        nx, ny = n
        # West
        if nx > 0:
            if occupancy_map[nx - 1, ny] == 0.5:
                occupancy_map[nx - 1, ny] = 0.0
                fringe.appendleft((nx - 1, ny))
        # East
        if nx < sx - 1:
            if occupancy_map[nx + 1, ny] == 0.5:
                occupancy_map[nx + 1, ny] = 0.0
                fringe.appendleft((nx + 1, ny))
        # North
        if ny > 0:
            if occupancy_map[nx, ny - 1] == 0.5:
                occupancy_map[nx, ny - 1] = 0.0
                fringe.appendleft((nx, ny - 1))
        # South
        if ny < sy - 1:
            if occupancy_map[nx, ny + 1] == 0.5:
                occupancy_map[nx, ny + 1] = 0.0
                fringe.appendleft((nx, ny + 1))


def generate_ray_casting_grid_map(ox, oy, xy_resolution, breshen=True):
    """
    The breshen boolean tells if it's computed with bresenham ray casting
    (True) or with flood fill (False)
    """
    min_x, min_y, max_x, max_y, x_w, y_w = calc_grid_map_config(
        ox, oy, xy_resolution)
    # default 0.5 -- [[0.5 for i in range(y_w)] for i in range(x_w)]
    occupancy_map = np.ones((x_w, y_w)) / 2
    center_x = int(
        round(-min_x / xy_resolution))  # center x coordinate of the grid map
    center_y = int(
        round(-min_y / xy_resolution))  # center y coordinate of the grid map
    # occupancy grid computed with bresenham ray casting
    if breshen:
        for (x, y) in zip(ox, oy):
            # x coordinate of the the occupied area
            ix = int(round((x - min_x) / xy_resolution))
            # y coordinate of the the occupied area
            iy = int(round((y - min_y) / xy_resolution))
            laser_beams = bresenham((center_x, center_y), (
                ix, iy))  # line form the lidar to the occupied point
            for laser_beam in laser_beams:
                occupancy_map[laser_beam[0]][
                    laser_beam[1]] = 0.0  # free area 0.0
            occupancy_map[ix][iy] = 1.0  # occupied area 1.0
            occupancy_map[ix + 1][iy] = 1.0  # extend the occupied area
            occupancy_map[ix][iy + 1] = 1.0  # extend the occupied area
            occupancy_map[ix + 1][iy + 1] = 1.0  # extend the occupied area
    # occupancy grid computed with with flood fill
    else:
        occupancy_map = init_flood_fill((center_x, center_y), (ox, oy),
                                        (x_w, y_w),
                                        (min_x, min_y), xy_resolution)
        flood_fill((center_x, center_y), occupancy_map)
        occupancy_map = np.array(occupancy_map, dtype=float)
        for (x, y) in zip(ox, oy):
            ix = int(round((x - min_x) / xy_resolution))
            iy = int(round((y - min_y) / xy_resolution))
            occupancy_map[ix][iy] = 1.0  # occupied area 1.0
            occupancy_map[ix + 1][iy] = 1.0  # extend the occupied area
            occupancy_map[ix][iy + 1] = 1.0  # extend the occupied area
            occupancy_map[ix + 1][iy + 1] = 1.0  # extend the occupied area
    return occupancy_map, min_x, max_x, min_y, max_y, xy_resolution


def main(donnee):
    """
    Example usage
    """
    xy_resolution = 0.02  # x-y grid resolution
    ang, dist = donnee_read(donnee)
    ox = np.sin(ang) * dist
    oy = np.cos(ang) * dist
    occupancy_map, min_x, max_x, min_y, max_y, xy_resolution = \
        generate_ray_casting_grid_map(ox, oy, xy_resolution, True)
    xy_res = np.array(occupancy_map).shape
    plt.figure(1, figsize=(10, 4))
    plt.subplot(122)
    plt.imshow(occupancy_map, cmap="PiYG_r", vmin=0, vmax=1)
    # Adjust the color limits to make the heatmap more pronounced
    plt.clim(0, 1)
    plt.gca().set_xticks(np.arange(-.5, xy_res[1], 1), minor=True)
    plt.gca().set_yticks(np.arange(-.5, xy_res[0], 1), minor=True)
    plt.grid(True, which="minor", color="w", linewidth=0.6, alpha=0.5)
    plt.colorbar()
    plt.subplot(121)
    plt.plot([oy, np.zeros(np.size(oy))], [ox, np.zeros(np.size(oy))], "ro-")
    plt.axis("equal")
    plt.plot(0.0, 0.0, "ob")
    plt.gca().set_aspect("equal", "box")
    bottom, top = plt.ylim()  # return the current y-lim
    plt.ylim((top, bottom))  # rescale y axis, to match the grid orientation
    plt.grid(True)
    plt.show()


if __name__ == '__main__':
    main({6.0: 5327.567, 7.0: 5328.617, 8.0: 5305.06, 10.0: 3596.095, 11.0: 3568.465, 12.0: 3549.695, 13.0: 3509.149, 14.0: 3511.29, 15.0: 3628.545, 17.0: 3319.771, 18.0: 3315.485, 19.0: 3309.777, 30.0: 1594.499, 32.0: 1495.235, 33.0: 1457.311, 34.0: 1435.898, 35.0: 1396.511, 36.0: 1361.505, 37.0: 1338.774, 38.0: 1315.505, 39.0: 1302.782, 40.0: 1311.762, 41.0: 1327.935, 42.0: 1348.004, 43.0: 1372.437, 44.0: 1401.011, 47.0: 963.374, 48.0: 963.443, 67.0: 954.848, 72.0: 4378.993, 73.0: 4370.386, 88.0: 966.167, 89.0: 951.307, 90.0: 938.164, 91.0: 940.577, 92.0: 952.649, 93.0: 971.152, 94.0: 969.431, 95.0: 955.028, 96.0: 949.482, 97.0: 945.925, 98.0: 959.417, 101.0: 1210.812, 102.0: 1211.913, 103.0: 1216.56, 104.0: 1228.459, 106.0: 1655.882, 107.0: 1667.675, 108.0: 1672.612, 109.0: 1689.752, 111.0: 1657.07, 112.0: 1652.295, 113.0: 1605.916, 114.0: 1584.442, 115.0: 1580.367, 116.0: 1569.324, 118.0: 2299.163, 119.0: 2270.052, 120.0: 2272.216, 123.0: 1135.346, 124.0: 1132.74, 125.0: 1130.181, 126.0: 1129.96, 127.0: 866.228, 128.0: 867.259, 142.0: 981.498, 143.0: 968.91, 144.0: 950.487, 145.0: 949.722, 146.0: 935.8, 147.0: 939.683, 152.0: 2235.234, 153.0: 2219.402, 154.0: 2195.209, 165.0: 1779.202, 166.0: 1787.706, 167.0: 1750.566, 168.0: 1742.958, 169.0: 1734.648, 170.0: 1727.051, 171.0: 1718.669, 172.0: 1713.889, 173.0: 1707.708, 174.0: 1717.989, 175.0: 1733.953, 177.0: 1967.837, 178.0: 1966.91, 179.0: 1971.849, 180.0: 1975.967, 181.0: 1979.168, 182.0: 1983.476, 183.0: 1988.101, 184.0: 1992.211, 185.0: 1998.597, 186.0: 2006.114, 187.0: 2007.906, 211.0: 2017.733, 212.0: 2020.332, 214.0: 1529.885, 215.0: 1522.809, 216.0: 1518.114, 217.0: 1513.542, 219.0: 1205.472, 225.0: 1424.506, 226.0: 1419.977, 227.0: 1409.206, 231.0: 1290.523, 232.0: 1295.997, 233.0: 1287.717, 234.0: 1274.506, 235.0: 1271.392, 236.0: 1273.934, 237.0: 1272.831, 238.0: 1262.125, 239.0: 1251.773, 240.0: 1244.208, 241.0: 1232.011, 242.0: 1219.58, 243.0: 1209.595, 244.0: 1201.772, 245.0: 1192.486, 246.0: 1182.585, 247.0: 1174.711, 248.0: 1167.754, 249.0: 1161.938, 250.0: 1155.172, 251.0: 1148.555, 252.0: 1143.047, 253.0: 1139.775, 254.0: 1134.74, 255.0: 1143.422, 256.0: 1186.379, 257.0: 1183.839, 258.0: 1167.007, 259.0: 1163.922, 260.0: 1181.399, 261.0: 1192.647, 262.0: 1188.277, 263.0: 1170.455, 264.0: 1162.151, 265.0: 1174.821, 266.0: 1187.747, 269.0: 2328.42, 270.0: 2334.887, 271.0: 2307.163, 272.0: 2267.548, 273.0: 2224.792, 274.0: 2206.734, 275.0: 2219.681, 276.0: 2468.25, 277.0: 2502.35, 280.0: 1117.033, 281.0: 1118.3, 282.0: 1125.48, 283.0: 1133.04, 284.0: 1142.789, 285.0: 1153.223, 286.0: 1157.707, 287.0: 1170.527, 288.0: 1183.193, 289.0: 1197.534, 290.0: 1205.221, 291.0: 1210.6, 292.0: 1219.901, 293.0: 1202.961, 299.0: 1230.608, 300.0: 1234.575, 301.0: 1240.282, 302.0: 1242.943, 303.0: 1245.6, 304.0: 1248.275, 305.0: 1251.731, 306.0: 1253.152, 307.0: 1254.095, 308.0: 1265.574, 310.0: 1380.446, 311.0: 1381.718, 312.0: 1393.257, 313.0: 1422.733, 314.0: 1447.385, 315.0: 1475.411, 316.0: 1506.804, 317.0: 1557.419, 318.0: 1589.323, 319.0: 1614.229, 323.0: 2052.872, 324.0: 2101.606, 325.0: 2176.909, 326.0: 2218.698, 327.0: 2313.481, 331.0: 3876.692, 332.0: 3770.112, 333.0: 3815.81, 334.0: 3816.134, 335.0: 3788.578, 336.0: 3763.183, 337.0: 3739.594, 338.0: 3615.987, 339.0: 3615.976, 340.0: 3637.838, 341.0: 3652.754, 342.0: 3649.121, 343.0: 3689.395, 346.0: 5238.914, 347.0: 5794.698, 348.0: 6699.727, 349.0: 6762.606, 350.0: 6791.579, 351.0: 6840.147})
    
    
    """ Code de main test
    
    from communication import communication_robot
    #import ast #text to dico bibliothèque
    import  lidar_to_grid_map
    try:
        cr = communication_robot()
        cr.connection(1)
        cr.envoie_lidar('start_lidar')
        dico=ast.literal_eval(cr.reception_lidar())
        #print(type(dico))
        lidar_to_grid_map.main(dico)
        #for key,value in dico.items():
         #   print(f'{key} {type(key)}')
    finally:
        cr.shutdown()
        
    """
