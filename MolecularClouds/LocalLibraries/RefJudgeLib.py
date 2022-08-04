'''
Contains functions involved with providing information to make decisions on which points to include or exclude.
'''
import math
import scipy.interpolate as interpolate
import numpy as np
from sklearn.linear_model import Ridge

import copy

# -------- FUNCTION DEFINITION --------
def findWeightedCenter(data, xmin = np.nan, xmax = np.nan, ymin = np.nan, ymax = np.nan, maskWeight = 4):
    """
    Given a 2d numpy array and some bounds, finds the weighted center of the bounded region.
    :param data: 2d numpy array, such as a greyscale image file (Numerical array)
    :param xmin: Left x-axis bound (int)
    :param xmax: Right x-axis bound (int)
    :param ymin: Bottom y-axis bound (int)
    :param ymax: Top y-axis bound (int)
    :param maskWeight: Points less than maskWeight * average data value will not be considered. Set to 0 to weight everything (Float)
    :return:
        xCoord: The x-coordinate of the weighted center of the bound region (Float)
        yCoord: The y-coordinate of the weighted center of the bound region (Float)
    """
    #Guard against modifying input data
    locData = copy.deepcopy(data)

    #Clean input data
    locData[np.isnan(locData)] = 0
    locData[np.isinf(locData)] = 0

    #Find offsets in case we only care about a smaller region
    xOffset = 0
    yOffset = 0
    if not math.isnan(xmax) and not math.isnan(xmin):
        locData = locData[:, int(xmin):int(xmax)]
        xOffset = xmin
    if not math.isnan(ymax) and not math.isnan(ymin):
        locData = locData[int(ymin):int(ymax), :]
        yOffset = ymin

    #Weight the multipliers by position
    x = range(0, locData.shape[1])
    y = range(0, locData.shape[0])
    X, Y = np.meshgrid(x, y)

    #Mask out all values not part of the cloud we care about
    lowExtinctMask = locData < 1.0 * maskWeight * np.sum(locData) / (locData.shape[0] * locData.shape[1])
    locData[lowExtinctMask] = 0

    xCoord = ((X * locData).sum() / locData.sum().astype(float)) + xOffset
    yCoord = ((Y * locData).sum() / locData.sum().astype(float)) + yOffset

    return xCoord, yCoord
# -------- FUNCTION DEFINITION --------

# -------- FUNCTION DEFINITION --------
def getDividingLine(data, xmin = np.nan, xmax = np.nan, ymin = np.nan, ymax = np.nan, maskWeight = 4):
    """
    Given a bound region with data, finds a line which divides it into two equally-weighted regions.
    :param data: 2d numpy array, such as a greyscale image file (Numerical array)
    :param xmin: Left x-axis bound (int)
    :param xmax: Right x-axis bound (int)
    :param ymin: Bottom y-axis bound (int)
    :param ymax: Top y-axis bound (int)
    :param maskWeight: Points less than maskWeight * average data value will not be considered. Set to 0 to weight everything (Float)
    :return:
        m: The multiplier, in mx+b (float)
        b: The offset, in mx+b (float)
    """
    # Guard against modifying input data
    locData = copy.deepcopy(data)

    # Clean input data
    locData[np.isnan(locData)] = 0
    locData[np.isinf(locData)] = 0

    # Find offsets in case we only care about a smaller region
    xOffset = 0
    yOffset = 0
    if not math.isnan(xmax) and not math.isnan(xmin):
        locData = locData[:, int(xmin):int(xmax)]
        xOffset = xmin
    if not math.isnan(ymax) and not math.isnan(ymin):
        locData = locData[int(ymin):int(ymax), :]
        yOffset = ymin

    #Define masks and weights
    highExtinctMask = locData > maskWeight * np.sum(locData)/(locData.shape[0]*locData.shape[1])
    weights = locData[highExtinctMask]
    coordsHighExtinct = np.argwhere(highExtinctMask)

    #x indexes
    xInput = coordsHighExtinct[:, 1].reshape(-1, 1)

    #y indexes to predict
    y = coordsHighExtinct[:, 0]

    # Linear Predictor
    predictor = Ridge(alpha=0.1)
    predictor.fit(xInput, y, weights)

    # Generate predictions
    xOutput = np.array([xInput.min(), xInput.max()]).reshape(-1, 1).astype(float)
    yOutput = predictor.predict(xOutput).astype(float)

    #Adjust for offsets
    xOutput += xOffset
    yOutput += yOffset

    m = (yOutput[1]-yOutput[0])/(xOutput[1]-xOutput[0])
    b = (xOutput[0]*yOutput[1] - xOutput[1]*yOutput[0])/(xOutput[0]-xOutput[1])

    return m, b
# -------- FUNCTION DEFINITION --------

# -------- FUNCTION DEFINITION --------
def isPointAboveLine(x, y, m, b):
    """
    Checks to see if a point is above or below a line
    :param x: x-value of the point
    :param y: y-value of the point
    :param m: The slope of the line, from mx+b
    :param b: The line offset, from mx+b
    :return: True or False, depending on if the point is above or below the line
    """
    linePoint = m * x + b
    return y > linePoint
# -------- FUNCTION DEFINITION --------

# -------- FUNCTION DEFINITION --------
def getPerpendicularLine(x, y, m):
    """
    Given a point and a slope, gives the parameters of the perpendicular line which passes through the point
    :param x: x-value of the point
    :param y: y-value of the point
    :param m: The slope of the input line, from mx+b
    :return:
        mPerp: The slope of the perpendicular line, from mx+b
        bPerp: The offset of the perpendicular line, from mx+b
    """
    mPerp = -1/m
    bPerp = y - mPerp * x
    return mPerp, bPerp
# -------- FUNCTION DEFINITION --------

# -------- FUNCTION DEFINITION --------
def getBoxRange(px, py, data, NDelt):
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
# -------- FUNCTION DEFINITION --------

# -------- FUNCTION DEFINITION --------
def getNullBox(px, py, data):
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
# -------- FUNCTION DEFINITION --------

# -------- FUNCTION DEFINITION --------
def getNullBox(px, py, data):
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
# -------- FUNCTION DEFINITION --------

# -------- FUNCTION DEFINITION --------
def nearHighExtinction(px, py, data, NDelt, highExtinctionThreshold):
    """
    Checks to see if a point is near a point of high extinction.
    :param px: x location of the point
    :param py: y location of the point
    :param hdu: The extinction dataset in question
    :param NDelt: Number of pixels above, below, left and right of the point to check, in a square box.
    :param highExtinctionThreshold: The threshold beyond which a point is considered to be high extinction.
    :return: True or False, depending on if the point is near a point of high extinction or not.
    """
    # ---- Find the extinction range for the given point
    ind_xmin, ind_xmax, ind_ymin, ind_ymax = getBoxRange(px, py, data, NDelt)
    # ---- Find the extinction range for the given point.

    # ---- Select the relevant data range and check if any point is greater than the threshold.
    locData = copy.deepcopy(data[ind_ymin:ind_ymax, ind_xmin:ind_xmax])
    mask = locData > highExtinctionThreshold
    if np.sum(mask) > 0:
        return True
    return False
# -------- FUNCTION DEFINITION --------

# -------- FUNCTION DEFINITION --------
def sortQuadrants(ind, X, Y, m, b, m2, b2):
    '''
    Given a set of points, sorts them into quadrants as divided by two lines.
    :param ind: The indexes of the points.
    :param X: The x coordinate of the points.
    :param Y: The y coordinate of the points.
    :param m: The slope of the first line
    :param b: The y offset of the first line.
    :param m2: The slope of the second line.
    :param b2: The y offset of the second line.
    :return: Q1, Q2, Q3, Q4 - Four lists which contain the indexes sorted into the four quadrants.
    '''
    Q1 = []
    Q2 = []
    Q3 = []
    Q4 = []
    for i in ind:
        px = X[i]
        py = Y[i]
        # ---- Sort into quadrant
        aboveLine1 = isPointAboveLine(px, py, m, b)
        aboveLine2 = isPointAboveLine(px, py, m2, b2)

        if aboveLine1 and aboveLine2:
            Q1.append(i)
        elif aboveLine1 and not aboveLine2:
            Q2.append(i)
        elif not aboveLine1 and aboveLine2:
            Q3.append(i)
        elif not aboveLine1 and not aboveLine2:
            Q4.append(i)
    return Q1, Q2, Q3, Q4
# -------- FUNCTION DEFINITION --------

# -------- FUNCTION DEFINITION --------
def averageBox(px, py, data, NDelt):
    """
    Returns the average of a box around the specified point/
    :param px: x location of the point
    :param py: y location of the point
    :param hdu: The extinction dataset in question
    :param NDelt: Number of pixels above, below, left and right of the point to check, in a square box.
    :return: The average around that point, as defined by a box around it.
    """
    # ---- Find the box range for the given point
    ind_xmin, ind_xmax, ind_ymin, ind_ymax = getBoxRange(px, py, data, NDelt)
    # ---- Find the box range for the given point.

    # ---- Select the relevant data range and check if any point is greater than the threshold.
    locData = copy.deepcopy(data[ind_ymin:ind_ymax, ind_xmin:ind_xmax])
    return np.average(locData)
# -------- FUNCTION DEFINITION --------

# -------- FUNCTION DEFINITION --------
def deepCopy(data):
    '''
    Alias for copy.deepcopy, so that a given file which has imported this module doesn't need to import that too.
    :param data: The data to be deep-copied
    :return: A deep copy of the data.
    '''
    return copy.deepcopy(data)
# -------- FUNCTION DEFINITION --------

# -------- FUNCTION DEFINITION --------
def interpMask(data, mask, method='cubic', fill_value=0):
    '''
    Given some data and a mask on that data, performs interpolation on the points in the data specified by the mask.
    :param data: The data to interpolate on. Numpy array.
    :param mask: A boolean mask on that data that indicates where to interpolate on. Boolean numpy array.
    :param method: The interpolation method. Strong. Ex. 'linear', 'nearest', 'cubic'.
    :param fill_value: Default value to fill values outside the convex hull of the input data.
    :return: returnData: The data with the interpolated data.
    '''
    width = data.shape[1]
    height = data.shape[0]
    x, y = np.meshgrid(np.arange(width), np.arange(height))

    goodX = x[~mask]
    goodY = y[~mask]

    knownData = data[~mask]

    missingX = x[mask]
    missingY = y[mask]

    interpMissingVals = interpolate.griddata((goodX, goodY), knownData, (missingX, missingY), method = method, fill_value = fill_value)

    returnData = copy.deepcopy(data)
    returnData[missingY, missingX] = interpMissingVals

    return returnData
# -------- FUNCTION DEFINITION --------

# -------- FUNCTION DEFINITION --------
def fillMissing(data, fillMode, interpMethod = 'linear'):
    '''
    Fill missing data within the provided data array.
    :param data: The 2d numpy data array with missing data values.
    :param fillMode: What the missing data should be filled with. String.
    :param interpMethod: Interpolation method, if interpolation is to be used. Default is linear. String.
    :return: data - with the fillings.
    '''
    nodata = np.isnan(data)

    if fillMode == 'Zero':
        data[nodata] = 0
    elif fillMode == 'Average':
        data[nodata] = np.average(data[np.isfinite(data)])
    elif fillMode == 'Inf':
        data[nodata] = math.inf
    elif fillMode == 'Interpolate':
        data = interpMask(data, nodata, interpMethod)
    else:
        data[nodata] = math.nan

    return data
# -------- FUNCTION DEFINITION --------
