'''
This module contains functions related to filling in missing information.
'''
import copy
import math

import numpy as np
from scipy import interpolate as interpolate


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


def deepCopy(data):
    '''
    Alias for copy.deepcopy, so that a given file which has imported this module doesn't need to import that too.
    :param data: The data to be deep-copied
    :return: A deep copy of the data.
    '''
    return copy.deepcopy(data)
