from cgi import test
import math
import numpy as np
import sys
sys.path
sys.path.append('/Users/zgivans33/Documents/2021-22 Summer Research/SPI2GithubWork/SPI2Py/src/SPI2Py')
from utils.distance_calculations import min_linesegment_linesegment_distance

# Add test to this and other dist for list vs np array


def test_parallel():

    #test single dimension
    a0 = np.array([0., 0., 0.])
    a1 = np.array([1., 0., 0.])
    b0 = np.array([0., 0., 1.])
    b1 = np.array([1., 0., 1.])

    dist = min_linesegment_linesegment_distance(a0, a1, b0, b1)

    print('dist', dist)

    assert round(dist,2) == 1

    #Zane to do: add more tests
    #https://www.cliffsnotes.com/study-guides/geometry/parallel-lines/testing-for-parallel-lines

    #test 3 dimensions
    a0 = np.array([2., 2., 2.])
    a1 = np.array([8., 6., 4.])
    b0 = np.array([1., 1., 1.])
    b1 = np.array([7., 5., 3.])

    dist = min_linesegment_linesegment_distance(a0, a1, b0, b1)

    print('dist', dist)

    assert round(dist,2) == round(math.sqrt(3), 2)

    #test parallel line segments overlapping
    a0 = np.array([0., 0., 0.])
    a1 = np.array([0., 0., 4.])
    b0 = np.array([0., 0., 2.])
    b1 = np.array([0., 0., 5.])

    dist = min_linesegment_linesegment_distance(a0, a1, b0, b1)

    print('dist', dist)

    assert round(dist,2) == 0

    #test line segments on same line but not overlapping
    a0 = np.array([0., 0., 0.])
    a1 = np.array([0., 1., 0.])
    b0 = np.array([0., 2., 0.])
    b1 = np.array([0., 4., 0.])

    dist = min_linesegment_linesegment_distance(a0, a1, b0, b1)

    print('dist', dist)

    assert round(dist,2) == 1

def test_skew():

    #test two endpoints closest point two dimensions
    a0 = np.array([0., 0., 0.])
    a1 = np.array([1., 0., 0.])
    b0 = np.array([0., 0., 2.])
    b1 = np.array([1., 0., 1.])

    dist = min_linesegment_linesegment_distance(a0, a1, b0, b1)

    print('dist', dist)

    assert round(dist,2) == 1

    #test two midsections closest point two dimensions
    a0 = np.array([0., 0., 0.])
    a1 = np.array([3., 3., 0.])
    b0 = np.array([0., 3., 1.])
    b1 = np.array([3., 0., 1.])

    dist = min_linesegment_linesegment_distance(a0, a1, b0, b1)

    print('dist', dist)

    assert round(dist,2) == 1

    #test midsection closest to endpoint
    a0 = np.array([0., 0., 0.])
    a1 = np.array([2., 2., 2.])
    b0 = np.array([2., 0., 3.])
    b1 = np.array([2., 4., 3.])

    dist = min_linesegment_linesegment_distance(a0, a1, b0, b1)

    print('dist', dist)

    assert round(dist,2) == 1

    #test negative points
    a0 = np.array([-1., -2., 0.])
    a1 = np.array([-1., -2., -3.])
    b0 = np.array([-3., -2., 0.])
    b1 = np.array([-5., -8., -3.])

    dist = min_linesegment_linesegment_distance(a0, a1, b0, b1)

    print('dist', dist)

    assert round(dist,2) == 2



test_parallel()
test_skew()