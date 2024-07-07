import numpy as np
from astropy.coordinates import SkyCoord

'''
Contains common unit conversion utilities.
'''
def ra_hms2deg(ra_h, ra_m, ra_s):
    """
     This function converts a right ascension in hour:min:sec to degrees
    :param ra_h: hour component of right ascension
    :param ra_m: minute component of right ascension
    :param ra_s: second component of right ascension
    :return: Right ascension in degrees
    """
    h2deg = np.array(ra_h) * 15
    m2deg = np.array(ra_m)/4
    s2deg = np.array(ra_s)/240
    return h2deg + m2deg + s2deg

def dec_dms2deg(dec_d, dec_m, dec_s):
    """
     This function converts a declination in degree:arcmin:arcsec to degrees
    :param dec_d: degree component of declination
    :param dec_m: arcminute component of declination
    :param dec_s: arcsecond component of declination
    :return: Declination in degrees
    """
    deg2deg = np.array(abs(dec_d))
    min2deg = np.array(abs(dec_m))/60
    sec2deg = np.array(abs(dec_s))/3600
    sign = np.sign(dec_d)
    result = (deg2deg + min2deg + sec2deg) * sign
    return result

def ra_deg2hms(ra_deg):
    """
     This function converts a right ascension in degrees to hour:min:sec
    :param: ra_deg: Right ascension in degrees
    :return ra_h: hour component of right ascension
    :return ra_m: minute component of right ascension
    :return ra_s: second component of right ascension
    """
    ra_h = ra_deg // 15
    remaining_deg = ra_deg % 15
    ra_m = remaining_deg // (1/4)
    remaining_deg = remaining_deg % (1/4)
    ra_s = remaining_deg // (1/240)

    return ra_h, ra_m, ra_s

def dec_deg2dms(dec_deg):
    """
     This function converts a declination in degree:arcmin:arcsec to degrees
    :param: dec_deg: Declination in degrees
    :return dec_d: degree component of declination
    :return dec_m: arcminute component of declination
    :return dec_s: arcsecond component of declination
    """
    dec_d = dec_deg // 1
    remaining_deg = dec_deg % 1
    dec_m = remaining_deg // (1/60)
    remaining_deg = remaining_deg % (1/60)
    dec_s = remaining_deg // (1/3600)

    return dec_d, dec_m, dec_s

def RADec2xy(RA, Dec, wcs):
    '''
     Converts two lists of Right Ascensions and Declinations associated with a set of points via a World Coordinate System (wcs) into pixel points.
    :param RA: List of Right Ascensions associated with a set of points
    :param Dec: List of Declinations associated with a set of points
    :param wcs: A World Coordinate System associated with the grid we want to convert the RA and Dec to.
    :return: xCoords, yCoords: Two lists which contain the x and y coordinates of the points, respectively.
    '''
    xCoords = []
    yCoords = []
    for i in range(len(RA)):
        pixelRow, pixelColumn = wcs.wcs_world2pix(RA[i], Dec[i], 0)
        xCoords.append(pixelRow)
        yCoords.append(pixelColumn)
    return xCoords, yCoords

def getRaDecMinSec(xmin, xmax, ymin, ymax, wcs):
    '''
     Given an x-y coordinate box bound, converts it to a maximal Ra-Dec box bound using the World Coordinate System (wcs)
    :param xmin: Minimum x value of the box bound.
    :param xmax: Maximum x value of the box bound.
    :param ymin: Minimum y value of the box bound.
    :param ymax: Maximum y value of the box bound.
    :param wcs: World coordinate system to convert the x-y to Right Ascensions and Declinations.
    :return: coordRaMin, coordRaMax, coordDecMin, coordDecMax - the box bound in Right Ascension (hms) and Declination (degrees)
    '''
    bottomLeft = SkyCoord.from_pixel(xmin, ymin, wcs)
    bottomRight = SkyCoord.from_pixel(xmax, ymin, wcs)
    topLeft = SkyCoord.from_pixel(xmin, ymax, wcs)
    topRight = SkyCoord.from_pixel(xmax, ymax, wcs)
    coords = [bottomLeft, bottomRight, topLeft, topRight]
    coordsRa = [coord.icrs.ra.hms for coord in coords]

    coordRaMin = min(coordsRa)
    coordRaMax = max(coordsRa)

    coordsDec = [coord.icrs.dec.degree for coord in coords]
    coordDecMin = min(coordsDec)
    coordDecMax = max(coordsDec)

    return coordRaMin, coordRaMax, coordDecMin, coordDecMax
