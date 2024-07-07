import math

import numpy as np

'''
Contains functions related to finding a valid box bound around a region.
'''
def getBoxBounds(data, boxXMin, boxXMax, boxYMin, boxYMax):
    '''
    Given a data canvas and a set of desired bounds, returns valid bounds
    :param data: The data canvas. Needed for its shape.
    :param boxXMin: Desired xmin bound.
    :param boxXMax: Desired xmax bound.
    :param boxYMin: Desired ymin bound.
    :param boxYMax: Desired ymax bound.
    :return: xmin, xmax, ymin, ymax - a set of valid bounds for the canvas.
    '''
    xmin = 0
    xmax = data.shape[1]
    ymin = 0
    ymax = data.shape[0]
    if not math.isnan(boxXMin) and boxXMin > xmin:
        xmin = int(boxXMin)
    if not math.isnan(boxXMax) and boxXMin < xmax:
        xmax = int(boxXMax)
    if not math.isnan(boxYMin) and boxYMin > ymin:
        ymin = int(boxYMin)
    if not math.isnan(boxYMax) and boxYMax < ymax:
        ymax = int(boxYMax)
    return xmin, xmax, ymin, ymax

def getNullBoxBound(px, py, data):
    '''
    Given a point on a data canvas, gets the box that bounds all the nan values inside.

    :param px: The x coordinate of the center of the box
    :param py: The y coordinate of the center of the box
    :param data: A data canvas, to make sure the box is within the bounds of the canvas and expand the box as needed to cover the nans.
    :return: ind_xmin, ind_xmax, ind_ymin, ind_ymax - The x and y bounds of that box.
    '''
    ind_xmax = px + 1 + 1  # add 1 to be inclusive of the upper bound
    ind_ymax = py + 1 + 1  # add 1 to be inclusive of the upper bound
    ind_xmin = px - 1
    ind_ymin = py - 1

    boundaries = True
    while boundaries:
        right_boundary = ind_xmax < data.shape[1] and math.isnan(np.sum(data[ind_ymin:ind_ymax, ind_xmax-1]))
        left_boundary = ind_xmin > 0 and math.isnan(np.sum(data[ind_ymin:ind_ymax, ind_xmin]))
        top_boundary = ind_ymax < data.shape[0] and math.isnan(np.sum(data[ind_ymax-1, ind_xmin:ind_xmax]))
        bottom_boundary = ind_ymin > 0 and math.isnan(np.sum(data[ind_ymin, ind_xmin:ind_xmax]))

        if right_boundary:
            ind_xmax += 1
        if left_boundary:
            ind_xmin -= 1
        if top_boundary:
            ind_ymax += 1
        if bottom_boundary:
            ind_ymin -= 1

        boundaries = right_boundary or left_boundary or top_boundary or bottom_boundary

    ind_xmin = int(max(ind_xmin, 0))
    ind_xmax = int(min(ind_xmax, data.shape[1]))
    ind_ymin = int(max(ind_ymin, 0))
    ind_ymax = int(min(ind_ymax, data.shape[0]))

    return ind_xmin, ind_xmax, ind_ymin, ind_ymax


def getBoxBound(px, py, data, NDelt):
    '''
    Returns valid bounds of a box around a coordinate.
    :param px: The x coordinate of the center of the box
    :param py: The y coordinate of the center of the box
    :param data: A data canvas, to make sure the box is within the bounds of the canvas.
    :param NDelt: Number of pixels horizontally and vertically from the center to extend out the box.
    :return: ind_xmin, ind_xmax, ind_ymin, ind_ymax - The x and y bounds of that box.
    '''
    ind_xmax = px + NDelt + 1  # add 1 to be inclusive of the upper bound
    ind_ymax = py + NDelt + 1  # add 1 to be inclusive of the upper bound
    ind_xmin = px - NDelt
    ind_ymin = py - NDelt

    ind_xmin = int(max(ind_xmin, 0))
    ind_xmax = int(min(ind_xmax, data.shape[1]))
    ind_ymin = int(max(ind_ymin, 0))
    ind_ymax = int(min(ind_ymax, data.shape[0]))

    return ind_xmin, ind_xmax, ind_ymin, ind_ymax
