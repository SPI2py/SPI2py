import numpy as np
import sys
sys.path
sys.path.append('/Users/zgivans33/Documents/2021-22 Summer Research/SPI2GithubWork/SPI2Py/src/SPI2Py')
from utils.distance_calculations import min_points_linesegment_distance

# For all tests check gradient eval too..

def test_first():
    #test simple orthogonal endpoint case
    p = np.array([1., 0., 1.])
    a = np.array([0., 0., 0.])
    b = np.array([1., 0., 0.])

    min_dist = min_points_linesegment_distance(p, a, b)

    print("min_dist: ", min_dist)

    assert round(min_dist, 2) == 1




# Speed test saved...
# p = np.array([0., 1., 1.])
# a = np.array([0., 0., 0.])
# b = np.array([0., 0., 1.])
#
# aa = np.array([[0., 0., 0.]])
# ab = np.array([[0., 0., 0.],
#                [0., 0., 1.],
#                [0., 0., 1.],
#                [0., 0., 1.],
#                [0., 0., 1.]])
#
# start = perf_counter_ns()
# print(min_point_line_distance(p, a, b))
# stop = perf_counter_ns()
# print('Time', stop-start)
#
# start = perf_counter_ns()
# print(min_point_line_distance(p, a, b))
# stop = perf_counter_ns()
# print('Time', stop-start)
#
# start = perf_counter_ns()
# print(min_cdist(aa, ab))
# stop = perf_counter_ns()
# print('Time', stop-start)
#
# # print(min_cdist(p, ab))