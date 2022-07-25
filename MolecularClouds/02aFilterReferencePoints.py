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
MatchedRMExtinctFile = config.MatchedRMExtinctionFile
# ---- Input Files

# ---- Output Files
AllPotRefPointsPath = config.AllPotRefPointFile

LogFile = config.Script02aFile

NearRejectedRefPointsFile = config.NearExtinctRefPointFile
FarRejectedRefPointsFile = config.FarExtinctRefPointFile
AnomRejRefPointFile = config.AnomRefPointFile
RejRefPointFile = config.RejRefPointFile
RemainingRefPointsFile = config.RemainingRefPointFile

FilteredRMExtincPath = config.FilteredRMExtinctionFile
# ---- Output Files

# -------- DEFINE FILES AND PATHS. --------

# -------- CONFIGURE LOGGING --------
logging.basicConfig(filename=LogFile, filemode='w', format=config.logFormat, level=logging.INFO)
loggingDivider = config.logSectionDivider
# -------- CONFIGURE LOGGING --------

# -------- READ FITS FILE --------
hdulist = fits.open(regionOfInterest.fitsFilePath)
hdu = hdulist[0]
wcs = WCS(hdu.header)
# -------- READ FITS FILE. --------

# -------- PREPROCESS FITS DATA TYPE. --------
# If fitsDataType is column density, then convert to visual extinction
if regionOfInterest.fitsDataType == 'HydrogenColumnDensity':
    hdu.data = hdu.data / config.VExtinct_2_Hcol
# -------- PREPROCESS FITS DATA TYPE. --------

# ---- LOAD AND UNPACK MATCHED RM AND EXTINCTION DATA
MatchedRMExtinctionData = pd.read_csv(MatchedRMExtinctFile)
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
messages = ['Potential reference points with a matched extinction value less than the extinction threshold set in the starting settings configuration are considered candidates.',
            '\t-For clouds that appear near the disk and towards the galactic center, an appropriate threshold value is {}.'.format(config.onDiskAvGalacticThresh),
            '\t-For clouds that appear near the disk and away from the galactic center, an appropriate threshold value is {}.'.format(config.onDiskAvAntiGalacticThresh),
            '\t-For clouds that appear off the disk, an appropriate threshold value is {}.'.format(config.offDiskAvThresh),
            "{}'s absolute calculated latitude is: {}".format(cloudName, abs(GalLatDeg)),
            "The selected threshold latitude (from the starting settings config) is: {}".format(config.offDiskLatitude),
            "Given this information, the threshold extinction has been set to the suggested {}".format(Av_threshold)]

logging.info(loggingDivider)
map(logging.info, messages)
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
dataframe = MatchedRMExtinctionData.copy()
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
if AllPotRefPointsPath is not None:
    AllPotentialRefPoints.to_csv(AllPotRefPointsPath, index=False)
# ---- SAVE REFERENCE POINT DATA AS A TABLE.
# -------- FIND ALL POTENTIAL REFERENCE POINTS. --------

PotRefPoints += listIndRefPoints
RejectedReferencePoints += []

# ---- Log info
messages = ['Based on the threshold extinction of {}, a total of {} potential reference points were found.'.format(Av_threshold, numAllRefPoints),
            "The IDs of the selected points are: {}".format([i+1 for i in PotRefPoints]),
            "The following are all the potential reference points: \n {}".format(AllPotentialRefPoints)]
logging.info(loggingDivider)
map(logging.info, messages)
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

NearRejectedRefPoints.to_csv(NearRejectedRefPointsFile)
FarRejectedRefPoints.to_csv(FarRejectedRefPointsFile)
# ---- Record the points rejected for what reason, and what points remain as potential reference points.

# ---- Log info
messages = ['We will now check if any of the potential reference points are near a region of high extinction.',
            "\t-A close region around the point has been defined to the configuration-selected {} pixels".format(NDeltNear),
            "\t-A far region around the point has been defined to the configuration-selected {} pixels".format(NDeltFar),
            "\t-A region of high extinction has been defined to the configuration-selected Av={}".format(highExtinctionThreshold),
            'The potential reference point(s) {} are near a region of high extinction'.format([i+1 for i in nearHighExtinctionRegion]),
            'The potential reference point(s) {} are far from a region of high extinction'.format([i+1 for i in farHighExtinctionRegion]),
            'As per configuration settings, near points will be removed: {}'.format(config.useNearExtinctionRemove),
            'As per configuration settings, far points will be removed: {}'.format(config.useFarExtinctionRemove),
            'As such, the remaining points by their IDs are: \n {}'.format(PotRefPoints),
            'Near High Extinction Rejected Points data was saved to {}'.format(NearRejectedRefPointsFile),
            'Far from High Extinction Rejected Points data was saved to {}'.format(FarRejectedRefPointsFile)]
logging.info(loggingDivider)
map(logging.info, messages)
# ---- Log info

# -------- CHECK TO SEE IF ANY POTENTIAL POINTS ARE NEAR A REGION OF HIGH EXTINCTION. --------
#======================================================================================================================
# -------- CHECK TO SEE IF ANY POTENTIAL POINTS HAVE ANOMALOUS RM VALUES --------
# -------- Define "anomalous"

# Choose a rotation measure corresponding to anomalous
rm_avg = np.mean(MatchedRMExtinctionData['Rotation_Measure(rad/m2)'])
rm_std = np.std(MatchedRMExtinctionData['Rotation_Measure(rad/m2)'])

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
AnomalousRejectedRefPoints.to_csv(AnomRejRefPointFile)
# ---- Log info
messages = ['We will now check if any of the potential reference points have anomalous rotation measure values.',
            "\t-Anomalous rotation measure values have been defined in the starting configuration to be greater or less than {} standard deviations from the mean (rm < {:.2f}rad/m^2 or rm > {:.2f}rad/m^2)".format(coeffSTD, rm_lowerLimit, rm_upperLimit),
            'As per configuration settings, anomalous points will be removed: {}'.format(config.useAnomalousSTDNumRemove),
            'The potential reference point(s) {} have anomalous rotation measure values'.format(anomalousRMIndex),
            'As such, the remaining points by their IDs are: \n {}'.format(PotRefPoints),
            'Anomalous Rejected Points data was saved to {}'.format(AnomRejRefPointFile)]
logging.info(loggingDivider)
map(logging.info, messages)
# ---- Log info
# -------- CHECK TO SEE IF ANY POTENTIAL POINTS HAVE ANOMALOUS RM VALUES. --------

#======================================================================================================================

# -------- SAVE REJECTED AND REMAINING REFERENCE POINT INFO. --------
RejectedRefPoints = AllPotentialRefPoints.loc[RejectedReferencePoints].sort_values('Extinction_Value')
RemainingRefPoints = AllPotentialRefPoints.loc[PotRefPoints].sort_values('Extinction_Value')
RejectedRefPoints.to_csv(RejRefPointFile)
RemainingRefPoints.to_csv(RemainingRefPointsFile)
messages = ['Rejected Reference Points data was saved to {}'.format(RejRefPointFile),
            'Remaining Reference Points data was saved to {}'.format(RemainingRefPointsFile)]
map(logging.info, messages)
# -------- SAVE REJECTED AND REMAINING REFERENCE POINT INFO. --------

#======================================================================================================================

# -------- FINALIZE REMAINING POINTS AFTER WINNOWING FROM PRIOR STAGES --------
chosenRefPoints_Num = [int(np.round(i)) for i in PotRefPoints]

maxRefPoints = int(round(len(MatchedRMExtinctionData.index) * config.maxFracPointNum))
if len(chosenRefPoints_Num) > maxRefPoints: chosenRefPoints_Num = chosenRefPoints_Num[:maxRefPoints]

FilteredRMExtincPoints = AllPotentialRefPoints.loc[chosenRefPoints_Num].sort_values('Extinction_Value').reset_index()
FilteredRMExtincPoints.to_csv(FilteredRMExtincPath)

# ---- Check if the number of points left after filtering is good for further analysis.
if len(FilteredRMExtincPoints.index) < 1:
    messages = ["Less than one potential reference points are left after filtering!",
                "No further analysis can be done, and all future scriPoints will error.",
                "Consider adjusting your judgement criteria in the config.",
                "Alternatively, consider getting more rotation measure data!"]
    logging.critical(loggingDivider)
    map(logging.critical, messages)

elif len(FilteredRMExtincPoints.index) == len(MatchedRMExtinctionData.index):
    messages = ["All matched RM-Extinction points remain after filtering!",
                "This will cause issues with stability trend analysis.",
                "Consider limiting how many points can be taken as off positions.",
                "This can be adjusted in the configs (Max Fraction Reference Points).",
                "Alternatively, consider getting more rotation measure data."]
    logging.critical(loggingDivider)
    map(logging.critical, messages)

# ---- Check if the number of points left after filtering is good for further analysis.
messages = ["The Remaining Reference Points will be:",
            PotRefPoints,
            "The Remaining data is thus:",
            FilteredRMExtincPoints,
            'Remaining data was saved to {}'.format(FilteredRMExtincPath)]
logging.info(loggingDivider)
map(logging.info, messages)
# -------- FINALIZE REMAINING POINTS AFTER WINNOWING FROM PRIOR STAGES --------