import math
'''
Contains miscellaneous utility functions not yet sorted into other libraries.
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
