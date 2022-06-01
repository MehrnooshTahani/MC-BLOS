"""
This is the second stage of the BLOSMapping method where rotation measure points from the catalogue are matched to
an extinction value from the fits file. Matching is based on physical proximity.

The matched rotation measure data and extinction information are saved in a file.
"""
import csv
from itertools import zip_longest
from LocalLibraries.DataFile import DataFile
import os
from astropy.io import fits
from astropy.wcs import WCS
import numpy as np
import math
from LocalLibraries.RegionOfInterest import Region
import LocalLibraries.config as config
import LocalLibraries.RefJudgeLib as rjl

# -------- CHOOSE THE REGION OF INTEREST --------
cloudName = config.cloud
regionOfInterest = Region(cloudName)
# -------- CHOOSE THE REGION OF INTEREST. --------

# -------- DEFINE FILES AND PATHS --------
RMCatalogPath = os.path.join(config.dir_root, config.dir_data, config.file_RMCatalogue)
saveFilePath = os.path.join(config.dir_root, config.dir_fileOutput, config.cloud, config.prefix_RMExtinctionMatch + config.cloud + '.txt')
# -------- DEFINE FILES AND PATHS. --------

# -------- READ FITS FILE --------
hdulist = fits.open(regionOfInterest.fitsFilePath)
hdu = hdulist[0]
wcs = WCS(hdu.header)
# -------- READ FITS FILE. --------

# -------- PREPROCESS FITS DATA TYPE. --------
data = rjl.deepCopy(hdu.data)

# If fitsDataType is column density, then convert to visual extinction
if regionOfInterest.fitsDataType == 'HydrogenColumnDensity':
    data = data / config.VExtinct_2_Hcol

#Handle bad data by interpolation.
'''
data[data < 0] = np.nan
baddata = np.isnan(data)
data = rjl.interpMask(data, baddata, 'linear') #Todo: This is an extremely costly step...
'''
# -------- PREPROCESS FITS DATA TYPE. --------

# -------- READ ROTATION MEASURE FILE --------
# Get all the rm points within the region of interest
rmData = DataFile(RMCatalogPath, regionOfInterest.raHoursMax, regionOfInterest.raMinsMax, regionOfInterest.raSecMax,
                  regionOfInterest.raHoursMin, regionOfInterest.raMinsMin, regionOfInterest.raSecMin,
                  regionOfInterest.decDegMax, regionOfInterest.decDegMin)
# -------- READ ROTATION MEASURE FILE. --------

# -------- DEFINE THE ERROR RANGE --------
# The physical limit on how far an extinction value can be from the rm and still be considered valid/applicable
# Todo: We want to redo this with pixel resolution instead. NOT DONE
'''
cloudDistance = regionOfInterest.distance  # [pc]
cloudJeansLength = regionOfInterest.jeanslength  # [pc]
minDiff = np.degrees(np.arctan(cloudJeansLength / cloudDistance))  # [deg]

minDiff_pix = minDiff / abs(hdu.header['CDELT1'])
NDelt = math.ceil(minDiff_pix)  # Round up
'''
RMResolution = 10
ExtinctionResolution = 100
if (ExtinctionResolution > RMResolution):
    NDelt = 1
else:
    NDelt = np.ceil(RMResolution/ExtinctionResolution)
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

    # If the rm lies within the given fits file:
    if 0 <= px < data.shape[1] and 0 <= py < data.shape[0]:

        # If the rm lies on a point with data:
        if data[py, px] != -1 and math.isnan(data[py, px]) is False:
            extinction = data[py, px]
            # ---- Negative extinction (the rm value landed on a negative pixel)
            # Negative extinction is not physical; take the extinction value to be an average of surrounding pixels
            # Todo: What if the negative pixel is surrounded by other negative pixels?
            # Todo: It does matter; issue warning and either exclude the point or ask the user to use a new file. Don't average from an even larger region.
            if extinction < 0:
                extinction = rjl.averageBox(px, py, data, 1)
            # ---- Negative extinction.

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

            #Todo: This can be made more efficient with numpy vectorized operations.
            # ---- Cycle through extinction values within the error range
            extinction_temp = []
            ra_temp = []
            dec_temp = []

            # Todo: The below doesn't account for negative extinction range values which nonetheless have been selected and averaged above.
            #  Should it? (Via the average) (or do we just ignore it)
            #  Work with a copy of the data and fill in data with interpolation, also give a warning that the value in question is interpolated.* Perhaps masking.
            for pxx in range(ind_xmin, ind_xmax):
                for pyy in range(ind_ymin, ind_ymax):
                    extinction = data[pyy, pxx]
                    if extinction >= 0:  # Negative extinction is not physical
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
            cntr += 1
# -------- MATCH ROTATION MEASURES AND EXTINCTION VALUES. --------

# -------- WRITE TO A FILE --------
with open(saveFilePath, 'w') as f:
    f.write('ID#' + '\t' + 'Extinction_Index_x' + '\t' + 'Extinction_Index_y' + '\t' + 'Ra(deg)' + '\t' +
            'Dec(deg)' + '\t' + 'Rotation_Measure(rad/m2)' + '\t' + 'RM_Err(rad/m2)' + '\t' +
            'RA_inExtincFile(degree)' + '\t' +
            'Dec_inExtincFile(degree)' + '\t' + 'Extinction_Value' + '\t' + 'Error_Range(pix)' + '\t' +
            'Min_Extinction_Value' + '\t' + 'Min_Extinction_Ra' + '\t' + 'Min_Extinction_Dec' + '\t' +
            'Max_Extinction_Value' + '\t' + 'Max_Extinction_RA' + '\t' + 'Max_Extinction_dec' + '\n')
    writer = csv.writer(f, delimiter='\t')
    writer.writerows(zip_longest(Identifier, ExtinctionIndex_x, ExtinctionIndex_y, RMRa, RMDec, RMValue, RMErr,
                                 ExtinctionRa, ExtinctionDec, ExtinctionValue, ErrRangePix,
                                 Extinction_MinInRange, Extinction_MinInRangeRa, Extinction_MinInRangeDec,
                                 Extinction_MaxInRange, Extinction_MaxInRangeRa, Extinction_MaxInRangeDec,
                                 fillvalue=''))
# -------- WRITE TO A FILE. --------

print('\nWithin the specified region of interest, a total of {} rotation measure points were matched '
      'to visual extinction values.\n'.format(len(Identifier)))
print('Matched visual extinction and rotation measure data were saved to {}'.format(saveFilePath))
