"""
This is the first stage of the BLOSMapping method where rotation measure points from the catalogue are matched to
an extinction value from the fits file. Matching is based on physical proximity.

The matched rotation measure data and extinction information are saved in a file.
"""
from itertools import zip_longest

from astropy.io import fits
from astropy.wcs import WCS

import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt

from LocalLibraries.RMCatalog import RMCatalog
from LocalLibraries.RegionOfInterest import Region
import LocalLibraries.config as config

from LocalLibraries.util import getBoxBounds
import LocalLibraries.ConversionLibrary as cl
import LocalLibraries.RefJudgeLib as rjl

import os
import logging

# -------- CHOOSE THE REGION OF INTEREST --------
cloudName = config.cloud
regionOfInterest = Region(cloudName)
# -------- CHOOSE THE REGION OF INTEREST. --------

# -------- DEFINE FILES AND PATHS --------
RMCatalogPath = config.DataRMCatalogFile

MatchedRMExtinctFile = config.MatchedRMExtinctionFile
LogFile = config.Script01aFile
# -------- DEFINE FILES AND PATHS. --------

# -------- CONFIGURE LOGGING --------
loggingDivider = config.logSectionDivider
logging.basicConfig(filename=LogFile, filemode='w', format=config.logFormat, level=logging.INFO)
# -------- CONFIGURE LOGGING --------

# -------- READ FITS FILE --------
hdulist = fits.open(regionOfInterest.fitsFilePath)
hdu = hdulist[0]
wcs = WCS(hdu.header)
# -------- READ FITS FILE. --------

# -------- PREPROCESS FITS DATA TYPE. --------
data = rjl.deepCopy(hdu.data)

# Identify where there is no data
nodata = np.isnan(data)

# If fitsDataType is column density, then convert to visual extinction
if regionOfInterest.fitsDataType == 'HydrogenColumnDensity':
    data = data / config.VExtinct_2_Hcol

# Obtain data bounds
boxXMin = regionOfInterest.xmin
boxXMax = regionOfInterest.xmax
boxYMin = regionOfInterest.ymin
boxYMax = regionOfInterest.ymax
xmin, xmax, ymin, ymax = getBoxBounds(data, boxXMin, boxXMax, boxYMin, boxYMax)

# Set default data values for missing data.
if config.fillMissingExtinct == 'Zero':
    data[nodata] = 0
elif config.fillMissingExtinct == 'Average':
    data[nodata] = np.average(data[np.isfinite(data)])
elif config.fillMissingExtinct == 'Inf':
    data[nodata] = math.inf
elif config.fillMissingExtinct == 'Interpolate':
    data[ymin:ymax, xmin:xmax] = rjl.interpMask(data[ymin:ymax, xmin:xmax], nodata[ymin:ymax, xmin:xmax], config.interpMethod)
else:
    data[nodata] = math.nan

#Refresh the nodata situation depending on config decision.
if config.useFillExtinct:
    nodata = np.isnan(data)

# Identify and remove bad data, defined as non-physical negative extinction values.
baddata = data < 0
data[ymin:ymax, xmin:xmax][baddata[ymin:ymax, xmin:xmax]] = math.nan

# Handle bad data (negative/no values) by full fits-file interpolation, if turned on.
if config.doInterpExtinct and config.interpRegion == 'All':
    data[ymin:ymax, xmin:xmax] = rjl.interpMask(data[ymin:ymax, xmin:xmax], baddata[ymin:ymax, xmin:xmax], config.interpMethod) #This step is computationally costly. It may be omitted if it is taking too long.
    baddata[ymin:ymax, xmin:xmax] = False

logging.info(loggingDivider)
logging.info("The Region Fits File Data Type is: {}".format(regionOfInterest.fitsDataType))
logging.info("The bounds of the region of interest in the fits file are:")
logging.info("xmin: {}".format(xmin))
logging.info("xmax: {}".format(xmax))
logging.info("ymin: {}".format(ymin))
logging.info("ymax: {}".format(ymax))
logging.info("Missing (Nan) data is set to (according to the config): {}".format(config.fillMissingExtinct))
logging.info("Missing (Nan) data is used for matching RM Extinctions (according to the config): {}".format(config.useFillExtinct))
logging.info("Non-Physical (Negative) data is to be interpolated (according to the config): {}".format(config.doInterpExtinct))
logging.info("Non-Physical (Negative) data is to be interpolated (according to the config): {}".format(config.interpMethod))
# -------- PREPROCESS FITS DATA TYPE. --------

# -------- READ ROTATION MEASURE FILE --------
# Get all the rm points within the region of interest
rmData = RMCatalog(RMCatalogPath, regionOfInterest.raHoursMax, regionOfInterest.raMinsMax, regionOfInterest.raSecMax,
                   regionOfInterest.raHoursMin, regionOfInterest.raMinsMin, regionOfInterest.raSecMin,
                   regionOfInterest.decDegMax, regionOfInterest.decDegMin)
# -------- READ ROTATION MEASURE FILE. --------

# -------- CHECK THAT THERE'S ENOUGH POINTS IN THE FILE. --------
if len(rmData.targetRotationMeasures) < 2:
    logging.critical(loggingDivider)
    logging.critical("Less than 2 Rotation Measures have been LOADED for the given region.")
    logging.critical("This technique requires at least one on-position, and at least one off-position.")
    logging.critical("As such, there is insufficient data to perform this analysis.")
    logging.critical("Please select a larger region or obtain a denser RM Catalogue.")
    logging.critical("This script will abort.")

    print("Less than 2 Rotation Measures have been LOADED for the given region.")
    print("This technique requires at least one on-position, and at least one off-position.")
    print("As such, there is insufficient data to perform this analysis.")
    print("Please select a larger region or obtain a denser RM Catalogue.")
    print("This script will abort.")
    exit()
# -------- CHECK THAT THERE'S ENOUGH POINTS IN THE FILE. --------

# -------- DEFINE THE ERROR RANGE --------
# The physical limit on how far an extinction value can be from the rm and still be considered valid/applicable

# Uncertainty based.
raErrsSec = np.array(rmData.targetRAErrSecs)
decErrs = np.array(rmData.targetDecErrArcSecs)

raErrSec = max(abs(raErrsSec)) #s
raErr = cl.ra_hms2deg(0, 0, raErrSec) #deg

decErrSec = max(abs(decErrs)) #s
decErr = cl.dec_dms2deg(0, 0, decErrSec) #deg

RMResolutionDegs = max(raErr, decErr)

''' Configuration based
RMResolutionDegs = config.resolution_RMCatalogue
'''
ExtinctionResolutionDegs = min(abs(hdu.header['CDELT1']), abs(hdu.header['CDELT2'])) #deg
# It is 1 pixel at most if the extinction map has a lower resolution than the RM map.
# #The maximum number of pixels which fit within the RM's resolution otherwise.
if (ExtinctionResolutionDegs > RMResolutionDegs):
    NDelt = 1
else:
    NDelt = np.ceil(RMResolutionDegs/ExtinctionResolutionDegs)

logging.info(loggingDivider)
logging.info("The uncertainty/resolution of the RM Catalogue for the given region (in degrees) is: {}".format(RMResolutionDegs))
logging.info("The uncertainty/resolution of the Extinction map for the given region (in degrees) is: {}".format(ExtinctionResolutionDegs))
logging.info("Given this, the number of extinction map pixels needed to cover the uncertainty in rotation measures is: {}".format(NDelt))
logging.info("This will be used to find the uncertainties later on.")
# -------- DEFINE THE ERROR RANGE. --------

# -------- DEFINE PARAMETERS --------
ExtinctionIndex_x = []
ExtinctionIndex_y = []
ExtinctionRa = []
ExtinctionDec = []
ExtinctionValue = []

Identifier = []
RMRa = []
RMDec = []
RMValue = []
RMErr = []

ErrRangePix = []

Extinction_MinInRangeRa = []
Extinction_MinInRangeDec = []
Extinction_MinInRange = []

Extinction_MaxInRangeRa = []
Extinction_MaxInRangeDec = []
Extinction_MaxInRange = []

IsExtinctionObserved = []
# -------- DEFINE PARAMETERS. --------

# -------- MATCH ROTATION MEASURES AND EXTINCTION VALUES --------
cntr = 0  # To keep track of how many matches have been made - numbering starts at 0
# Go through all of the rotation measure values and match them to an extinction value
for index in range(len(rmData.targetRotationMeasures)):
    # ---- Location of the rotation measure
    rmRA = rmData.targetRaHourMinSecToDeg[index]
    rmDec = rmData.targetDecDegArcMinSecs[index]
    py, px = wcs.world_to_array_index_values(rmRA, rmDec)  # Array indices of the rotation measure
    # ---- Location of the rotation measure.

    # ---- Skip the point if it violates a condition.
    inFitsFile = 0 <= px < data.shape[1] and 0 <= py < data.shape[0]

    hasData = inFitsFile and not nodata[py, px]
    physicalData = inFitsFile and not baddata[py, px]
    interpByPoint = config.doInterpExtinct and config.interpRegion == 'Local'

    validPoint = inFitsFile and hasData and (physicalData or interpByPoint)

    #if not validPoint:
    if not validPoint:
        continue
    # ---- Skip the point if it violates a condition.

    # ---- Interpolate Missing Data
    if not physicalData and interpByPoint:
        ind_xmin, ind_xmax, ind_ymin, ind_ymax = rjl.getNullBox(px, py, data)
        data[ind_ymin:ind_ymax, ind_xmin:ind_xmax] = rjl.interpMask(data[ind_ymin:ind_ymax, ind_xmin:ind_xmax],
                                                                    baddata[ind_ymin:ind_ymax, ind_xmin:ind_xmax],
                                                                    config.interpMethod)
        baddata[ind_ymin:ind_ymax, ind_xmin:ind_xmax] = False
    # ---- Interpolate Missing Data

    extinction = data[py, px]

    Identifier.append(cntr)
    RMRa.append(rmRA)
    RMDec.append(rmDec)
    RMValue.append(rmData.targetRotationMeasures[index])
    RMErr.append(rmData.targetRMErrs[index])

    # ---- Match rotation measure to an extinction value
    ExtinctionIndex_x.append(int(px))
    ExtinctionIndex_y.append(int(py))
    ExtinctionRa.append(wcs.wcs_pix2world(px, py, 0)[0])
    ExtinctionDec.append(wcs.wcs_pix2world(px, py, 0)[1])
    ExtinctionValue.append(extinction)
    # ---- Match rotation measure to an extinction value.

    # ---- Find the extinction error range for the given rm
    ErrRangePix.append(NDelt)
    ind_xmin, ind_xmax, ind_ymin, ind_ymax = rjl.getBoxRange(px, py, data, NDelt)
    # ---- Find the extinction error range for the given rm.

    # ---- Cycle through extinction values within the error range
    extinction_temp = []
    ra_temp = []
    dec_temp = []

    for pxx in range(ind_xmin, ind_xmax):
        for pyy in range(ind_ymin, ind_ymax):
            # ---- Skip Missing Data
            if nodata[pyy, pxx] and math.isnan(data[pyy, pxx]):
                continue
            # ---- Skip Missing Data
            # ---- Interpolate Bad Data
            if baddata[pyy, pxx] and config.interpRegion == 'Local':
                #Problem is probably interpolation over areas declared to be baddata...
                xmin, xmax, ymin, ymax = rjl.getNullBox(pxx, pyy, data)
                data[ymin:ymax, xmin:xmax] = rjl.interpMask(data[ymin:ymax, xmin:xmax],
                                                                            baddata[ymin:ymax,
                                                                            xmin:xmax],
                                                                            config.interpMethod)
                baddata[ymin:ymax, xmin:xmax] = False
            # ---- Interpolate Missing Data
            extinction = data[pyy, pxx]
            extinction_temp.append(extinction)
            xx, yy = wcs.wcs_pix2world(pxx, pyy, 0)
            ra_temp.append(xx)
            dec_temp.append(yy)
    # ---- Cycle through extinction values within the error range.

    # Find minimum extinction value
    ind_min = np.where(extinction_temp == min(extinction_temp))[0][0]
    Extinction_MinInRangeRa.append(ra_temp[ind_min])
    Extinction_MinInRangeDec.append(dec_temp[ind_min])
    Extinction_MinInRange.append(extinction_temp[ind_min])

    # Find maximum extinction value
    ind_max = np.where(extinction_temp == max(extinction_temp))[0][0]
    Extinction_MaxInRangeRa.append(ra_temp[ind_max])
    Extinction_MaxInRangeDec.append(dec_temp[ind_max])
    Extinction_MaxInRange.append(extinction_temp[ind_max])

    # ---- Negative extinction (the rm value landed on a negative pixel)
    # Negative extinction is not physical; in prior step it was interpolated away. Mark these points.
    if baddata[py, px]:
        IsExtinctionObserved.append(False)
    else:
        IsExtinctionObserved.append(True)
    # ---- Negative extinction.

    cntr += 1

# -------- MATCH ROTATION MEASURES AND EXTINCTION VALUES. --------

# -------- CHECK THAT THERE'S ENOUGH POINTS MATCHED. --------
if len(RMValue) < 2:
    logging.critical(loggingDivider)
    logging.critical("Less than 2 Rotation Measures have been MATCHED for the given region.")
    logging.critical("This technique requires at least one on-position, and at least one off-position.")
    logging.critical("As such, there is insufficient data to perform this analysis.")
    logging.critical("Please select a larger region or obtain a denser RM Catalogue.")

    print("Less than 2 Rotation Measures have been MATCHED for the given region.")
    print("This technique requires at least one on-position, and at least one off-position.")
    print("As such, there is insufficient data to perform this analysis.")
    print("Please select a larger region or obtain a denser RM Catalogue.")

elif len(RMValue) < config.minStablePointNum:
    logging.critical(loggingDivider)
    logging.critical("Less than {} Rotation Measures have been MATCHED for the given region.".format(len(RMValue)))
    logging.critical("In the config, the minimum number of points selected by the stability trend algorithm is: {}".format(config.minStablePointNum))
    logging.critical("As such, there is insufficient data to perform this analysis.")
    logging.critical("Please select a larger region, obtain a denser RM Catalogue, or adjust your stability trend requirements.")

    print("Less than {} Rotation Measures have been MATCHED for the given region.".format(len(RMValue)))
    print("In the config, the minimum number of points selected by the stability trend algorithm is: {}".format(config.minStablePointNum))
    print("As such, there is insufficient data to perform this analysis.")
    print("Please select a larger region, obtain a denser RM Catalogue, or adjust your stability trend requirements.")

elif len(RMValue) < 2*config.minStablePointNum:
    logging.critical(loggingDivider)
    logging.critical("Less than {} Rotation Measures have been MATCHED for the given region.".format(len(RMValue)))
    logging.critical("In the config, the minimum number of points selected by the stability trend algorithm is: {}".format(config.minStablePointNum))
    logging.critical("Since some points will be excluded, there may be insufficient data to perform this analysis.")
    logging.critical("Please select a larger region, obtain a denser RM Catalogue, or adjust your stability trend requirements.")

    print("Less than {} Rotation Measures have been MATCHED for the given region.".format(len(RMValue)))
    print("In the config, the minimum number of points selected by the stability trend algorithm is: {}".format(config.minStablePointNum))
    print("Since some points will be excluded, there may be insufficient data to perform this analysis.")
    print("Please select a larger region, obtain a denser RM Catalogue, or adjust your stability trend requirements.")

# -------- CHECK THAT THERE'S ENOUGH POINTS MATCHED. --------

# -------- WRITE TO A FILE --------
columns = ['Extinction_Index_x','Extinction_Index_y','Ra(deg)','Dec(deg)','Rotation_Measure(rad/m2)',
           'RM_Err(rad/m2)','RA_inExtincFile(degree)','Dec_inExtincFile(degree)','Extinction_Value','Error_Range(pix)','Min_Extinction_Value',
           'Min_Extinction_Ra','Min_Extinction_Dec','Max_Extinction_Value','Max_Extinction_RA','Max_Extinction_dec','Extinction_Observed']
data = list(zip_longest(ExtinctionIndex_x, ExtinctionIndex_y, RMRa, RMDec, RMValue, RMErr,
                        ExtinctionRa, ExtinctionDec, ExtinctionValue, ErrRangePix,
                        Extinction_MinInRange, Extinction_MinInRangeRa, Extinction_MinInRangeDec,
                        Extinction_MaxInRange, Extinction_MaxInRangeRa, Extinction_MaxInRangeDec,
                        IsExtinctionObserved,
                        fillvalue=''))
matchedRMExtinct = pd.DataFrame(data, columns=columns)
matchedRMExtinct.index.name = 'ID#'
matchedRMExtinct.to_csv(MatchedRMExtinctFile)
# -------- WRITE TO A FILE. --------
logging.info(loggingDivider)
logging.info('Within the specified region of interest, a total of {} rotation measure points were matched '
      'to visual extinction values.'.format(len(Identifier)))
logging.info('Matched visual extinction and rotation measure data were saved to {}'.format(MatchedRMExtinctFile))

print()
print('Within the specified region of interest, a total of {} rotation measure points were matched '
      'to visual extinction values.'.format(len(Identifier)))
print('Matched visual extinction and rotation measure data were saved to {}'.format(MatchedRMExtinctFile))
