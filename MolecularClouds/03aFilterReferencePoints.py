"""
This is the third stage of the BLOSMapping method where the reference points are determined.
In this file (03a), the potential reference points are found and sorted based on lowest extinction (or column density).
The anomalous points (that are too close to the cloud or with an odd RM value) are then excluded.
"""
import pandas as pd
import numpy as np
import math

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
extinctionCoordinateDataFile = config.ExtinctionCoordDataFile

AllPotRefPointsPath = config.AllPotRefPointFile

LogFile = config.Script03aFile

NearRejectedRefPointsFile = config.NearExtinctRefPointFile
FarRejectedRefPointsFile = config.FarExtinctRefPointFile
AnomRejRefPointFile = config.AnomRefPointFile
RejRefPointFile = config.RejRefPointFile

FilteredRefPointsPath = config.FilteredRefPointsFile
# ---- Output Files

# -------- DEFINE FILES AND PATHS. --------

# -------- CONFIGURE LOGGING --------
logging.basicConfig(filename=LogFile, filemode='w', format=config.logFormat, level=logging.INFO)
loggingDivider = config.logSectionDivider
# -------- CONFIGURE LOGGING --------

# ---- LOAD AND UNPACK MATCHED RM AND EXTINCTION DATA
MatchedRMExtinctionData = pd.read_csv(MatchedRMExtinctFile, sep=config.dataSeparator)
# ---- LOAD AND UNPACK MATCHED RM AND EXTINCTION DATA

# ---- TRACK INDEXES WHICH ARE ACCEPTED AS REFERENCE VALUES/REJECTED ----
PotRefPoints = []
RejectedReferencePoints = []
# ---- TRACK INDEXES WHICH ARE ACCEPTED AS REFERENCE VALUES/REJECTED ----

# ---- TRACK KEY DATAFRAMES ----
AllPotentialRefPoints = None
# ---- TRACK KEY DATAFRAMES ----

# -------- LOAD THE THRESHOLD EXTINCTION --------
# ---- Find the center of the cloud in equatorial coordinates
# Determining the center locations to properly identify Av threshold value
regionRaMin = cl.ra_hms2deg(regionOfInterest.raHoursMax, regionOfInterest.raMinsMax, regionOfInterest.raSecMax)
regionRaMax = cl.ra_hms2deg(regionOfInterest.raHoursMin, regionOfInterest.raMinsMin, regionOfInterest.raSecMin)
regionRaAvg = (regionRaMin + regionRaMax) / 2.0
regionDecMin = regionOfInterest.decDegMax
regionDecMax = regionOfInterest.decDegMin
regionDecAvg = (regionDecMin + regionDecMax) / 2.0
# ---- Find the center of the cloud in equatorial coordinates

# ---- Convert from equatorial to galactic coordinates
coord = SkyCoord(regionRaAvg, regionDecAvg, unit="deg", frame='icrs')
GalLongDeg = coord.galactic.l.degree
GalLatDeg = coord.galactic.b.degree
# ---- Convert from equatorial to galactic coordinates

# ---- Get the average extinction in the area of valid points.
xmin, xmax, ymin, ymax = regionOfInterest.xmin, regionOfInterest.xmax, regionOfInterest.ymin, regionOfInterest.ymax
regionData = regionOfInterest.hdu.data[ymin:ymax, xmin:xmax]
finiteVals = np.isfinite(regionData)
avgExt = np.average(regionData[finiteVals])
# ---- Get the average extinction in the area of valid points.

# ---- Load the threshold.
Av_threshold = None
if abs(GalLatDeg) < config.offDiskLatitude and (abs(GalLongDeg) < 90 or abs(GalLongDeg) > 270):
    Av_threshold = config.onDiskAvGalacticThresh
elif abs(GalLatDeg) < config.offDiskLatitude:
    Av_threshold = config.onDiskAvAntiGalacticThresh
else:
    Av_threshold = config.offDiskAvThresh

if config.avgExtMultiplier:
    Av_threshold = Av_threshold * avgExt #TODO: check if this is correct ??

highExtinctionThreshold = config.highExtinctionThreshMultiplier * Av_threshold
# ---- Load the threshold.

# ---- Save the info
columns = ['Extinction Threshold', 'Average Extinction',
           'High Extinction Threshold',
           'Region Right Ascension', 'Region Declination',
           'Region Galactic Longitude', 'Region Galactic Latitude']
extinctionCoordData = pd.DataFrame(columns=columns)
extinctionCoordData['Extinction Threshold'] = [Av_threshold]
extinctionCoordData['Average Extinction'] = [avgExt]
extinctionCoordData['High Extinction Threshold'] = [highExtinctionThreshold]
extinctionCoordData['Region Right Ascension'] = [regionRaAvg]
extinctionCoordData['Region Declination'] = [regionDecAvg]
extinctionCoordData['Region Galactic Longitude'] = [GalLongDeg]
extinctionCoordData['Region Galactic Latitude'] = [GalLatDeg]
extinctionCoordData.to_csv(extinctionCoordinateDataFile, sep=config.dataSeparator)
# ---- Save the info

# ---- Log info
messages = ['Potential reference points with a matched extinction value less than the extinction threshold set in the starting settings configuration are considered candidates.',
            '\t-For clouds that appear near the disk and towards the galactic center, an appropriate threshold value is {}.'.format(config.onDiskAvGalacticThresh),
            '\t-For clouds that appear near the disk and away from the galactic center, an appropriate threshold value is {}.'.format(config.onDiskAvAntiGalacticThresh),
            '\t-For clouds that appear off the disk, an appropriate threshold value is {}.'.format(config.offDiskAvThresh),
            "{}'s absolute calculated latitude is: {}".format(cloudName, abs(GalLatDeg)),
            "The selected threshold latitude (from the starting settings config) is: {}".format(config.offDiskLatitude),
            "Given this information, the threshold extinction has been set to the suggested {}".format(Av_threshold),
            "This info has been saved to: {}".format(extinctionCoordinateDataFile)]

logging.info(loggingDivider)
for message in messages:
    logging.info(message)
# ---- Log info
# -------- LOAD THE THRESHOLD EXTINCTION. --------

#======================================================================================================================

# -------- FIND ALL POTENTIAL REFERENCE POINTS --------
# -------- Criterion: Av < threshold
'''
We will only consider points with visual extinction less than the specified threshold value as potential 
reference points
- Here we extract these points and sort the resulting dataframe from smallest to greatest extinction 
'''
# All potential reference points are all reference points with extinction less than the threshold
dataframe = MatchedRMExtinctionData.copy()
columnName = 'Extinction_Value'
threshold = Av_threshold #TODO: Why multiplying the user defined A_v by the average Av of the region?
# Indices where the threshold is met in the given column
ind = np.where(dataframe[columnName] <= threshold)[0]
# All rows which exceed the threshold value in the given column
AllPotentialRefPoints = dataframe.loc[ind].sort_values(columnName, ignore_index=True)
numAllRefPoints = len(AllPotentialRefPoints)
listIndRefPoints = [i for i in range(numAllRefPoints)]
# -------- Criterion: Av < threshold.

# ---- SAVE REFERENCE POINT DATA AS A TABLE
if AllPotRefPointsPath is not None:
    AllPotentialRefPoints.to_csv(AllPotRefPointsPath, index=False, sep=config.dataSeparator)
# ---- SAVE REFERENCE POINT DATA AS A TABLE.
# -------- FIND ALL POTENTIAL REFERENCE POINTS. --------

# ---- Add those reference points to the data we're keeping track of
PotRefPoints += listIndRefPoints #Notes on +=: When both inputs are lists, the result is list concatenation. Ex. A = [1], B = [2, 3], then A += B = [1, 2, 3]. Here, both objects are lists.
RejectedReferencePoints += []
# ---- Add those reference points to the data we're keeping track of

# ---- Log info
messages = ['Based on the threshold extinction of {}, a total of {} potential reference points were found.'.format(Av_threshold, numAllRefPoints),
            "The IDs of the selected points are: {}".format([i+1 for i in PotRefPoints]),
            "The following are all the potential reference points: \n {}".format(AllPotentialRefPoints)]
logging.info(loggingDivider)
for message in messages:
    logging.info(message)
# ---- Log info
#======================================================================================================================

# -------- CHECK TO SEE IF ANY POTENTIAL POINTS ARE NEAR A REGION OF HIGH EXTINCTION --------
# -------- Define the range
# The distance the point can be from a region of high extinction and still be thought to sample the background
cloudDistance = regionOfInterest.distance  # [pc]
cloudJeansLength = regionOfInterest.jeanslength  # [pc] #Note: can skip these steps and just define NDeltNear and NDeltFar as a function of the extinction (hydrogen column density) fits file pixel size or telescope resolution.
minDiff = np.degrees(np.arctan(cloudJeansLength / cloudDistance))  # [deg]

degPerPix = abs(regionOfInterest.hdu.header['CDELT1'])
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
    if rjl.IsNearHighExt(px, py, regionOfInterest.hdu.data, NDeltNear, highExtinctionThreshold):
        nearHighExtinctionRegion.append(i)
    if not rjl.IsNearHighExt(px, py, regionOfInterest.hdu.data, NDeltFar, highExtinctionThreshold):
        farHighExtinctionRegion.append(i)
    # ---- Find the extinction range for the given point.
# -------- For each potential reference point.

# ---- Record the points rejected for what reason, and what points remain as potential reference points.
nearHighExtinctReject = [item for item in PotRefPoints if item in nearHighExtinctionRegion and config.useNearExtinctionRemove]
farHighExtinctReject = [item for item in PotRefPoints if item in farHighExtinctionRegion and config.useFarExtinctionRemove]

RejectedReferencePoints += nearHighExtinctReject #Notes on +=: When both inputs are lists, the result is list concatenation. Ex. A = [1], B = [2, 3], then A += B = [1, 2, 3]. Here, both objects are lists.
RejectedReferencePoints += farHighExtinctReject

PotRefPoints = [item for item in PotRefPoints if item not in nearHighExtinctReject]
PotRefPoints = [item for item in PotRefPoints if item not in farHighExtinctReject]

NearRejectedRefPoints = AllPotentialRefPoints.loc[nearHighExtinctReject].sort_values('Extinction_Value')
FarRejectedRefPoints = AllPotentialRefPoints.loc[farHighExtinctReject].sort_values('Extinction_Value')

NearRejectedRefPoints.to_csv(NearRejectedRefPointsFile, sep=config.dataSeparator)
FarRejectedRefPoints.to_csv(FarRejectedRefPointsFile, sep=config.dataSeparator)
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
for message in messages:
    logging.info(message)
# ---- Log info

# -------- CHECK TO SEE IF ANY POTENTIAL POINTS ARE NEAR A REGION OF HIGH EXTINCTION. --------
#======================================================================================================================
# -------- CHECK TO SEE IF ANY POTENTIAL POINTS HAVE ANOMALOUS RM VALUES --------
# -------- Define "anomalous"

# Choose a rotation measure corresponding to anomalous
rmAvg = np.mean(AllPotentialRefPoints['Rotation_Measure(rad/m2)'])
rmMedian = np.median(AllPotentialRefPoints['Rotation_Measure(rad/m2)'])
#print(rmMedian)

rmStd = np.std(AllPotentialRefPoints['Rotation_Measure(rad/m2)'])

rmQ1 = np.percentile(AllPotentialRefPoints['Rotation_Measure(rad/m2)'], 25)
rmQ3 = np.percentile(AllPotentialRefPoints['Rotation_Measure(rad/m2)'], 75)
rmIQR = rmQ3-rmQ1
#print(rmIQR)

coeffIQR = config.anomalousIQRNum
rmUpperLimit = rmMedian + coeffIQR * rmIQR
rmLowerLimit = rmMedian - coeffIQR * rmIQR
#print(rmUpperLimit)
#print(rmLowerLimit)

#print(rmStd, rmUpperLimit, rmLowerLimit)
# -------- Define "anomalous".

# -------- For each potential reference point
anomalousRMIndex = []
for i in list(AllPotentialRefPoints.index):
    idNum = AllPotentialRefPoints['ID#'][i]
    if AllPotentialRefPoints['Rotation_Measure(rad/m2)'][i] < rmLowerLimit or \
            AllPotentialRefPoints['Rotation_Measure(rad/m2)'][i] > rmUpperLimit:
        anomalousRMIndex.append(i)  # To identify points numbered in order of increasing extinction
# -------- For each potential reference point.

# ---- Record the points rejected for what reason, and what points remain as potential reference points.
anomalousReject = [item for item in PotRefPoints if item in anomalousRMIndex and config.useanomalousIQRNumRemove]

RejectedReferencePoints += anomalousReject #Notes on +=: When both inputs are lists, the result is list concatenation. Ex. A = [1], B = [2, 3], then A += B = [1, 2, 3]. Here, both objects are lists.
PotRefPoints = [item for item in PotRefPoints if item not in anomalousReject]

AnomalousRejectedRefPoints = AllPotentialRefPoints.loc[anomalousReject].sort_values('Extinction_Value')
AnomalousRejectedRefPoints.to_csv(AnomRejRefPointFile, sep=config.dataSeparator)
# ---- Record the points rejected for what reason, and what points remain as potential reference points.

# ---- Log info
messages = ['We will now check if any of the potential reference points have anomalous rotation measure values.',
            "\t-Anomalous rotation measure values have been defined in the starting configuration to be greater or less than {} standard deviations from the mean (rm < {:.2f}rad/m^2 or rm > {:.2f}rad/m^2)".format(coeffIQR, rmLowerLimit, rmUpperLimit),
            'As per configuration settings, anomalous points will be removed: {}'.format(config.useanomalousIQRNumRemove),
            'The potential reference point(s) {} have anomalous rotation measure values'.format(anomalousRMIndex),
            'As such, the remaining points by their IDs are: \n {}'.format(PotRefPoints),
            'Anomalous Rejected Points data was saved to {}'.format(AnomRejRefPointFile)]
logging.info(loggingDivider)
for message in messages:
    logging.info(message)
# ---- Log info
# -------- CHECK TO SEE IF ANY POTENTIAL POINTS HAVE ANOMALOUS RM VALUES. --------

#======================================================================================================================

# -------- SAVE REJECTED REFERENCE POINT INFO. --------
RejectedRefPoints = AllPotentialRefPoints.loc[RejectedReferencePoints].sort_values('Extinction_Value')
RejectedRefPoints.to_csv(RejRefPointFile, sep=config.dataSeparator)
messages = ['Rejected Reference Points data was saved to {}'.format(RejRefPointFile)]
for message in messages:
    logging.info(message)
# -------- SAVE REJECTED REFERENCE POINT INFO. --------

#======================================================================================================================

# -------- FINALIZE REMAINING POINTS AFTER WINNOWING FROM PRIOR STAGES --------
#Get the indexes of the remaining points.
RemainingPotRefPoints = [int(np.round(i)) for i in PotRefPoints]
#Make sure the number of points taken is no more than the accepted maximum number of points.
maxRefPoints = int(round(len(MatchedRMExtinctionData.index) * config.maxFracPointNum))
if len(RemainingPotRefPoints) > maxRefPoints: RemainingPotRefPoints = RemainingPotRefPoints[:maxRefPoints]

#Get the data of the points by selecting them from the data table, and save them.
FilteredRefPoints = AllPotentialRefPoints.loc[RemainingPotRefPoints].sort_values('Extinction_Value').reset_index()
'''
#Important comment: Originally points were identified by the 'Id#' column. 
However, they are not in order from lowest to highest extinction. 
We reset the index after sorting to get an index of the points from lowest to highest extinction. 
However, if you ever need to cross-reference with the points prior to this reset, 
you need to compare with the 'Id#' column, not the new index column!
'''
FilteredRefPoints.to_csv(FilteredRefPointsPath, sep=config.dataSeparator)

# ---- Check if the number of points left after filtering is good for further analysis.
if len(FilteredRefPoints.index) < 1:
    messages = ["Less than one potential reference points are left after filtering!",
                "No further analysis can be done, and all future scripts will error.",
                "Consider adjusting your judgement criteria in the config.",
                "Alternatively, consider getting more rotation measure data!"]
    logging.critical(loggingDivider)
    for message in messages:
        logging.critical(message)
        print(message)

elif len(FilteredRefPoints.index) == len(MatchedRMExtinctionData.index):
    messages = ["All matched RM-Extinction points remain after filtering!",
                "This will cause issues with stability trend analysis.",
                "Consider limiting how many points can be taken as off positions.",
                "This can be adjusted in the configs (Max Fraction Reference Points).",
                "Alternatively, consider getting more rotation measure data."]
    logging.critical(loggingDivider)
    for message in messages:
        logging.critical(message)
        print(message)
# ---- Check if the number of points left after filtering is good for further analysis.

# ---- Log info
messages = ["The Remaining Reference Points will be:",
            RemainingPotRefPoints,
            "The Remaining data is thus:",
            FilteredRefPoints,
            'Remaining data was saved to {}'.format(FilteredRefPointsPath)]
logging.info(loggingDivider)
for message in messages:
    logging.info(message)
 # ---- Log info
# -------- FINALIZE REMAINING POINTS AFTER WINNOWING FROM PRIOR STAGES --------