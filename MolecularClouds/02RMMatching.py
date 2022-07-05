"""
This is the second stage of the BLOSMapping method where rotation measure points from the catalogue are matched to
an extinction value from the fits file. Matching is based on physical proximity.

The matched rotation measure data and extinction information are saved in a file.
"""
from itertools import zip_longest

import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.wcs import WCS

import numpy as np
import pandas as pd
import math

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
RMCatalogPath = os.path.join(config.dir_root, config.dir_data, config.file_RMCatalogue)
saveFilePath = os.path.join(config.dir_root, config.dir_fileOutput, config.cloud, config.prefix_RMExtinctionMatch + config.cloud + '.txt')

saveScriptLogPath = os.path.join(config.dir_root, config.dir_fileOutput, cloudName, config.dir_logs, "Script2Log.txt")
# -------- DEFINE FILES AND PATHS. --------

# -------- CONFIGURE LOGGING --------
logging.basicConfig(filename=saveScriptLogPath, filemode='w', format=config.logFormat, level=logging.INFO)
# -------- CONFIGURE LOGGING --------

# -------- READ FITS FILE --------
hdulist = fits.open(regionOfInterest.fitsFilePath)
hdu = hdulist[0]
wcs = WCS(hdu.header)
# -------- READ FITS FILE. --------

# -------- PREPROCESS FITS DATA TYPE. --------
data = rjl.deepCopy(hdu.data)
nodata = np.isnan(data)

# If fitsDataType is column density, then convert to visual extinction
if regionOfInterest.fitsDataType == 'HydrogenColumnDensity':
    data = data / config.VExtinct_2_Hcol

#Handle bad data (negative/no values) by interpolation.
boxXMin = regionOfInterest.xmin
boxXMax = regionOfInterest.xmax
boxYMin = regionOfInterest.ymin
boxYMax = regionOfInterest.ymax

xmin, xmax, ymin, ymax = getBoxBounds(data, boxXMin, boxXMax, boxYMin, boxYMax)

if config.fillMissing == 'Zero':
    data[nodata] = 0
elif config.fillMissing == 'Average':
    data[nodata] = np.average(data[np.isfinite(data)])
else:
    data[nodata] = math.nan

baddata = data[ymin:ymax, xmin:xmax] < 0
data[ymin:ymax, xmin:xmax][baddata] = np.nan

if config.doInterpExtinct and config.interpAll:
    data[ymin:ymax, xmin:xmax] = rjl.interpMask(data[ymin:ymax, xmin:xmax], baddata[ymin:ymax, xmin:xmax], config.interpMethod) #This step is computationally costly. It may be omitted if it is taking too long.

# -------- PREPROCESS FITS DATA TYPE. --------

# -------- READ ROTATION MEASURE FILE --------
# Get all the rm points within the region of interest
rmData = RMCatalog(RMCatalogPath, regionOfInterest.raHoursMax, regionOfInterest.raMinsMax, regionOfInterest.raSecMax,
                   regionOfInterest.raHoursMin, regionOfInterest.raMinsMin, regionOfInterest.raSecMin,
                   regionOfInterest.decDegMax, regionOfInterest.decDegMin)
# -------- READ ROTATION MEASURE FILE. --------

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
# -------- It is 1 pixel at most if the extinction map has a lower resolution than the RM map. The maximum number of pixels which fit within the RM's resolution otherwise.
if (ExtinctionResolutionDegs > RMResolutionDegs):
    NDelt = 1
else:
    NDelt = np.ceil(RMResolutionDegs/ExtinctionResolutionDegs)
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
    hasData = inFitsFile and data[py, px] != -1 and math.isfinite(data[py, px])
    validPoint = inFitsFile and hasData

    # ---- Interpolate Missing Data
    if inFitsFile and math.isnan(data[py, px]) and config.doInterpExtinct and not config.interpAll:
        ind_xmin, ind_xmax, ind_ymin, ind_ymax = rjl.getNullBox(px, py, data)
        data[ind_ymin:ind_ymax, ind_xmin:ind_xmax] = rjl.interpMask(data[ind_ymin:ind_ymax, ind_xmin:ind_xmax],
                                                                    baddata[ind_ymin:ind_ymax, ind_xmin:ind_xmax],
                                                                    config.interpMethod)
    # ---- Interpolate Missing Data

    #if not validPoint:
    if not inFitsFile:
        print("Continuing.")
        continue
    # ---- Skip the point if it violates a condition.

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
            if math.isnan(data[pyy, pxx]) and not config.interpAll:
                ind_xmin, ind_xmax, ind_ymin, ind_ymax = rjl.getNullBox(pxx, pyy, data)
                data[ind_ymin:ind_ymax, ind_xmin:ind_xmax] = rjl.interpMask(data[ind_ymin:ind_ymax, ind_xmin:ind_xmax],
                                                                            baddata[ind_ymin:ind_ymax,
                                                                            ind_xmin:ind_xmax],
                                                                            config.interpMethod)
            extinction = data[pyy, pxx]
            extinction_temp.append(extinction)
            xx, yy = wcs.wcs_pix2world(pxx, pyy, 0)
            ra_temp.append(xx)
            dec_temp.append(yy)
    # ---- Cycle through extinction values within the error range.

    # Find minimum extinction value
    #print("Min Temp:", min(extinction_temp))
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
matchedRMExtinct.to_csv(saveFilePath)
# -------- WRITE TO A FILE. --------

logging.info('\nWithin the specified region of interest, a total of {} rotation measure points were matched '
      'to visual extinction values.\n'.format(len(Identifier)))
logging.info('Matched visual extinction and rotation measure data were saved to {}'.format(saveFilePath))

print('\nWithin the specified region of interest, a total of {} rotation measure points were matched '
      'to visual extinction values.\n'.format(len(Identifier)))
print('Matched visual extinction and rotation measure data were saved to {}'.format(saveFilePath))
