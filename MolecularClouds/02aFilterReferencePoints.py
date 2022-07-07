"""
This is the third stage of the BLOSMapping method where the reference points are determined
"""
import os

import pandas as pd
import numpy as np
import math

from astropy.wcs import WCS
from astropy.io import fits
from astropy.coordinates import SkyCoord

import LocalLibraries.ConversionLibrary as cl
from LocalLibraries.RegionOfInterest import Region

import LocalLibraries.config as config
import LocalLibraries.RefJudgeLib as rjl

import logging

# -------- LOAD THE REGION OF INTEREST --------
cloudName = config.cloud
regionOfInterest = Region(cloudName)
# -------- LOAD THE REGION OF INTEREST. --------

# -------- DEFINE FILES AND PATHS --------

# ---- Input Files
# Matched rm and extinction data
MatchedRMExtincPath = config.MatchedRMExtinctionFile
# ---- Input Files

# ---- Output Files
AllPotentialRefPointsPath = config.AllPotRefPointFile

saveScriptLogPath = config.Script02aFile

NearRejectedRefPointsPath = config.NearExtinctRefPointFile
FarRejectedRefPointsPath = config.FarExtinctRefPointFile
AnomalousRejectedRefPointsPath = config.AnomRefPointFile
RejectedRefPointsPath = config.RejRefPointFile
RemainingRefPointsPath = config.RemainingRefPointFile

FilteredRMExtincPath = config.FilteredRMExtinctionFile
# ---- Output Files

# -------- DEFINE FILES AND PATHS. --------

# -------- CONFIGURE LOGGING --------
logging.basicConfig(filename=saveScriptLogPath, filemode='w', format=config.logFormat, level=logging.INFO)
loggingDivider = "====================================================================================================="
# -------- CONFIGURE LOGGING --------

# -------- READ FITS FILE --------
hdulist = fits.open(regionOfInterest.fitsFilePath)
hdu = hdulist[0]
wcs = WCS(hdu.header)
# -------- READ FITS FILE. --------

# ---- LOAD AND UNPACK MATCHED RM AND EXTINCTION DATA
matchedRMExtinctionData = pd.read_csv(MatchedRMExtincPath)
# ---- LOAD AND UNPACK MATCHED RM AND EXTINCTION DATA

# -------- LOAD THE THRESHOLD EXTINCTION --------
# ---- Convert from equatorial to galactic coordinates (after finding the center)
regionRaMin = cl.ra_hms2deg(regionOfInterest.raHoursMax, regionOfInterest.raMinsMax, regionOfInterest.raSecMax)
regionRaMax = cl.ra_hms2deg(regionOfInterest.raHoursMin, regionOfInterest.raMinsMin, regionOfInterest.raSecMin)
regionRaAvg = (regionRaMin + regionRaMax) / 2.0
regionDecMin = regionOfInterest.decDegMax
regionDecMax = regionOfInterest.decDegMin
regionDecAvg = (regionDecMin + regionDecMax) / 2.0

coord = SkyCoord(regionRaAvg, regionDecAvg, unit="deg", frame='icrs')
GalLongDeg = coord.galactic.l.degree
GalLatDeg = coord.galactic.b.degree
# ---- Convert from equatorial to galactic coordinates
Av_threshold = None
if abs(GalLatDeg) < config.offDiskLatitude and (abs(GalLongDeg) < 90 or abs(GalLongDeg) > 270):
    Av_threshold = config.onDiskAvGalacticThresh
elif abs(GalLatDeg) < config.offDiskLatitude:
    Av_threshold = config.onDiskAvAntiGalacticThresh
else:
    Av_threshold = config.offDiskAvThresh
# ---- Log info
logging.info(loggingDivider)
logging.info('Potential reference points with a matched extinction value less than the extinction threshold set in the starting settings configuration are considered candidates.')
logging.info('\t-For clouds that appear near the disk and towards the galactic center, an appropriate threshold value is {}.'.format(config.onDiskAvGalacticThresh))
logging.info('\t-For clouds that appear near the disk and away from the galactic center, an appropriate threshold value is {}.'.format(config.onDiskAvAntiGalacticThresh))
logging.info('\t-For clouds that appear off the disk, an appropriate threshold value is {}.'.format(config.offDiskAvThresh))
logging.info("{}'s absolute calculated latitude is: {}".format(cloudName, abs(GalLatDeg)))
logging.info("The selected threshold latitude (from the starting settings config) is: {}".format(config.offDiskLatitude))
logging.info("Given this information, the threshold extinction has been set to the suggested {}".format(Av_threshold))
# ---- Log info
# -------- LOAD THE THRESHOLD EXTINCTION. --------

# ---- TRACK INDEXES WHICH ARE ACCEPTED AS REFERENCE VALUES/REJECTED ----
PotRefPoints = []
RejectedReferencePoints = []
# ---- TRACK INDEXES WHICH ARE ACCEPTED AS REFERENCE VALUES/REJECTED ----

# ---- TRACK KEY DATAFRAMES ----
AllPotentialRefPoints = None
# ---- TRACK KEY DATAFRAMES ----

#======================================================================================================================

# -------- FIND ALL POTENTIAL REFERENCE POINTS --------
# -------- Criterion: Av < threshold
'''
We will only consider points with visual extinction less than the specified threshold value as potential 
reference points
- Here we extract these points and sort the resulting dataframe from smallest to greatest extinction 
'''
# All potential reference points are all reference points with extinction less than the threshold:
dataframe = matchedRMExtinctionData.copy()
columnName = 'Extinction_Value'
threshold = Av_threshold
# Indices where the threshold is met in the given column
ind = np.where(dataframe[columnName] <= threshold)[0]
# All rows which exceed the threshold value in the given column
AllPotentialRefPoints = dataframe.loc[ind].sort_values(columnName, ignore_index=True)
numAllRefPoints = len(AllPotentialRefPoints)
listIndRefPoints = [i for i in range(numAllRefPoints)]
# -------- Criterion: Av < threshold.

# ---- SAVE REFERENCE POINT DATA AS A TABLE
if AllPotentialRefPointsPath is not None:
    AllPotentialRefPoints.to_csv(AllPotentialRefPointsPath, index=False)
# ---- SAVE REFERENCE POINT DATA AS A TABLE.
# -------- FIND ALL POTENTIAL REFERENCE POINTS. --------

PotRefPoints += listIndRefPoints
RejectedReferencePoints += []

# ---- Log info
logging.info(loggingDivider)
logging.info('Based on the threshold extinction of {}, a total of {} potential reference points were found.'.format(Av_threshold, numAllRefPoints))
logging.info("The IDs of the selected points are: {}".format([i+1 for i in PotRefPoints]))
logging.info("The following are all the potential reference points: \n {}".format(AllPotentialRefPoints))
# ---- Log info
#======================================================================================================================

# -------- CHECK TO SEE IF ANY POTENTIAL POINTS ARE NEAR A REGION OF HIGH EXTINCTION --------
# -------- Define the range
# The distance the point can be from a region of high extinction and still be thought to sample the background
cloudDistance = regionOfInterest.distance  # [pc]
cloudJeansLength = regionOfInterest.jeanslength  # [pc]
minDiff = np.degrees(np.arctan(cloudJeansLength / cloudDistance))  # [deg]

degPerPix = abs(hdu.header['CDELT1'])
minDiff_pix = minDiff / degPerPix
NDeltNear = config.nearExtinctionMultiplier * math.ceil(minDiff_pix)  # Round up
NDeltFar = config.farExtinctionMultiplier * math.ceil(minDiff_pix)  # Round up

# Choose the minimum extinction value which you want to correspond to an "on" position
highExtinctionThreshold = config.highExtinctionThreshMultiplier * Av_threshold
# -------- Define the range.

# -------- For each potential reference point
nearHighExtinctionRegion = []
farHighExtinctionRegion = []
for i in list(AllPotentialRefPoints.index):
    idNum = AllPotentialRefPoints['ID#'][i]
    px = AllPotentialRefPoints['Extinction_Index_x'][i]
    py = AllPotentialRefPoints['Extinction_Index_y'][i]

    # ---- Find the extinction range for the given point
    if rjl.nearHighExtinction(px, py, hdu.data, NDeltNear, highExtinctionThreshold):
        nearHighExtinctionRegion.append(i)
    if not rjl.nearHighExtinction(px, py, hdu.data, NDeltFar, highExtinctionThreshold):
        farHighExtinctionRegion.append(i)
    # ---- Find the extinction range for the given point.
# -------- For each potential reference point.

# ---- Record the points rejected for what reason, and what points remain as potential reference points.
nearHighExtinctReject = [item for item in PotRefPoints if item in nearHighExtinctionRegion and config.useNearExtinctionRemove]
farHighExtinctReject = [item for item in PotRefPoints if item in farHighExtinctionRegion and config.useFarExtinctionRemove]

RejectedReferencePoints += nearHighExtinctReject
RejectedReferencePoints += farHighExtinctReject

PotRefPoints = [item for item in PotRefPoints if item not in nearHighExtinctReject]
PotRefPoints = [item for item in PotRefPoints if item not in farHighExtinctReject]

NearRejectedRefPoints = AllPotentialRefPoints.loc[nearHighExtinctReject].sort_values('Extinction_Value')
FarRejectedRefPoints = AllPotentialRefPoints.loc[farHighExtinctReject].sort_values('Extinction_Value')

NearRejectedRefPoints.to_csv(NearRejectedRefPointsPath)
FarRejectedRefPoints.to_csv(FarRejectedRefPointsPath)
# ---- Record the points rejected for what reason, and what points remain as potential reference points.

# ---- Log info
logging.info(loggingDivider)
logging.info('We will now check if any of the potential reference points are near a region of high extinction.')
logging.info("\t-A close region around the point has been defined to the configuration-selected {} pixels".format(NDeltNear))
logging.info("\t-A far region around the point has been defined to the configuration-selected {} pixels".format(NDeltFar))
logging.info("\t-A region of high extinction has been defined to the configuration-selected Av={}".format(highExtinctionThreshold))
logging.info('The potential reference point(s) {} are near a region of high extinction'.format([i+1 for i in nearHighExtinctionRegion]))
logging.info('The potential reference point(s) {} are far from a region of high extinction'.format([i+1 for i in farHighExtinctionRegion]))
logging.info('As per configuration settings, near points will be removed: {}'.format(config.useNearExtinctionRemove))
logging.info('As per configuration settings, far points will be removed: {}'.format(config.useFarExtinctionRemove))
logging.info('As such, the remaining points by their IDs are: \n {}'.format(PotRefPoints))
logging.info('Near High Extinction Rejected Points data was saved to {}'.format(NearRejectedRefPointsPath))
logging.info('Far from High Extinction Rejected Points data was saved to {}'.format(FarRejectedRefPointsPath))
# ---- Log info

# -------- CHECK TO SEE IF ANY POTENTIAL POINTS ARE NEAR A REGION OF HIGH EXTINCTION. --------
#======================================================================================================================
# -------- CHECK TO SEE IF ANY POTENTIAL POINTS HAVE ANOMALOUS RM VALUES --------
# -------- Define "anomalous"

# Choose a rotation measure corresponding to anomalous
rm_avg = np.mean(matchedRMExtinctionData['Rotation_Measure(rad/m2)'])
rm_std = np.std(matchedRMExtinctionData['Rotation_Measure(rad/m2)'])

coeffSTD = config.anomalousSTDNum
rm_upperLimit = rm_avg + coeffSTD * rm_std
rm_lowerLimit = rm_avg - coeffSTD * rm_std
# -------- Define "anomalous".

# -------- For each potential reference point
anomalousRMIndex = []
for i in list(AllPotentialRefPoints.index):
    idNum = AllPotentialRefPoints['ID#'][i]
    if AllPotentialRefPoints['Rotation_Measure(rad/m2)'][i] < rm_lowerLimit or \
            AllPotentialRefPoints['Rotation_Measure(rad/m2)'][i] > rm_upperLimit:
        anomalousRMIndex.append(i)  # To identify points numbered in order of increasing extinction
# -------- For each potential reference point.
anomalousReject = [item for item in PotRefPoints if item in anomalousRMIndex and config.useAnomalousSTDNumRemove]

RejectedReferencePoints += anomalousReject
PotRefPoints = [item for item in PotRefPoints if item not in anomalousReject]

AnomalousRejectedRefPoints = AllPotentialRefPoints.loc[anomalousReject].sort_values('Extinction_Value')
AnomalousRejectedRefPoints.to_csv(AnomalousRejectedRefPointsPath)
# ---- Log info
logging.info(loggingDivider)
logging.info('We will now check if any of the potential reference points have anomalous rotation measure values.')
logging.info("\t-Anomalous rotation measure values have been defined in the starting configuration to be greater or less than {} standard deviations from the mean (rm < {:.2f}rad/m^2 or"
                                   " rm > {:.2f}rad/m^2)".format(coeffSTD, rm_lowerLimit, rm_upperLimit))
logging.info('As per configuration settings, anomalous points will be removed: {}'.format(config.useAnomalousSTDNumRemove))
logging.info('The potential reference point(s) {} have anomalous rotation measure values'.format(anomalousRMIndex))
logging.info('As such, the remaining points by their IDs are: \n {}'.format(PotRefPoints))
logging.info('Anomalous Rejected Points data was saved to {}'.format(AnomalousRejectedRefPointsPath))
# ---- Log info
# -------- CHECK TO SEE IF ANY POTENTIAL POINTS HAVE ANOMALOUS RM VALUES. --------

#======================================================================================================================

# -------- SAVE REJECTED AND REMAINING REFERENCE POINT INFO. --------
RejectedRefPoints = AllPotentialRefPoints.loc[RejectedReferencePoints].sort_values('Extinction_Value')
RemainingRefPoints = AllPotentialRefPoints.loc[PotRefPoints].sort_values('Extinction_Value')
RejectedRefPoints.to_csv(RejectedRefPointsPath)
RemainingRefPoints.to_csv(RemainingRefPointsPath)
logging.info('Rejected Reference Points data was saved to {}'.format(RejectedRefPointsPath))
logging.info('Remaining Reference Points data was saved to {}'.format(RemainingRefPointsPath))
# -------- SAVE REJECTED AND REMAINING REFERENCE POINT INFO. --------

#======================================================================================================================

# -------- FINALIZE REMAINING POINTS AFTER WINNOWING FROM PRIOR STAGES --------
chosenRefPoints_Num = [int(np.round(i)) for i in PotRefPoints]

FilteredRMExtincPoints = AllPotentialRefPoints.loc[chosenRefPoints_Num].sort_values('Extinction_Value').reset_index()
FilteredRMExtincPoints.to_csv(FilteredRMExtincPath)

logging.info(loggingDivider)
logging.info("The Remaining Reference Points will be:")
logging.info(PotRefPoints)
logging.info("The Remaining data is thus:")
logging.info(FilteredRMExtincPoints)
logging.info('Remaining data was saved to {}'.format(FilteredRMExtincPath))
# -------- FINALIZE REMAINING POINTS AFTER WINNOWING FROM PRIOR STAGES --------