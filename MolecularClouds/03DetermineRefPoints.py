"""
This is the third stage of the BLOSMapping method where the reference points are determined
"""
import os

import pandas as pd
import numpy as np
import math

from astropy.wcs import WCS
from astropy.io import fits

import matplotlib.pyplot as plt


import LocalLibraries.ConversionLibrary as cl
from LocalLibraries.RegionOfInterest import Region
from LocalLibraries.FindOptimalRefPoints import findTrendData
from LocalLibraries.FindOptimalRefPoints import FindOptimalRefPoints

import LocalLibraries.config as config
import LocalLibraries.RefJudgeLib as rjl
import LocalLibraries.PlotTemplates as pt
import LocalLibraries.RMPlotLibrary as rmpl

import logging

def plotRefPoints(refPoints, hdu, regionOfInterest, title):
    # -------- PREPARE TO PLOT REFERENCE POINTS --------
    labels = list(refPoints['ID#'])
    Ra = list(refPoints['Ra(deg)'])
    Dec = list(refPoints['Dec(deg)'])
    # ---- Convert Ra and Dec of reference points into pixel values of the fits file
    x, y = cl.RADec2xy(Ra, Dec, wcs)
    # ---- Convert Ra and Dec of reference points into pixel values of the fits file.
    # -------- PREPARE TO PLOT REFERENCE POINTS. --------

    # -------- CREATE A FIGURE - ALL REF POINTS MAP --------
    fig, ax = pt.extinctionPlot(hdu, regionOfInterest)

    plt.title(title, fontsize=12, y=1.08)
    plt.scatter(x, y, marker='o', facecolor='green', linewidth=.5, edgecolors='black', s=50)

    # ---- Annotate the chosen reference points
    pt.labelPoints(ax, labels, x, y)
    # ---- Annotate the chosen reference points
    # -------- CREATE A FIGURE - ALL REF POINTS MAP. --------
    return fig, ax

# -------- LOAD THE REGION OF INTEREST --------
cloudName = config.cloud
regionOfInterest = Region(cloudName)
# -------- LOAD THE REGION OF INTEREST. --------

# -------- DEFINE FILES AND PATHS --------
saveFilePath_ALlPotentialRefPoints = os.path.join(config.dir_root, config.dir_fileOutput, cloudName, config.prefix_allPotRefPoints + cloudName + '.txt')
saveFilePath_ReferencePoints = os.path.join(config.dir_root, config.dir_fileOutput, cloudName, config.prefix_selRefPoints + cloudName + '.txt')
saveFilePath_ReferenceData = os.path.join(config.dir_root, config.dir_fileOutput, cloudName, config.prefix_refData + cloudName + '.txt')

saveFigurePath_BLOSvsNRef_AllPotentialRefPoints = os.path.join(config.dir_root, config.dir_fileOutput, cloudName, config.dir_plots, 'BLOS_vs_NRef_AllPotentialRefPoints.png')
saveFigurePath_BLOSvsNRef_ChosenPotentialRefPoints = os.path.join(config.dir_root, config.dir_fileOutput, cloudName, config.dir_plots, 'BLOS_vs_NRef_ChosenRefPoints.png')
saveFigureDir_RefPointMap = os.path.join(config.dir_root, config.dir_fileOutput, cloudName, config.dir_plots)

saveQuadrantFigurePath = os.path.join(config.dir_root, config.dir_fileOutput, cloudName, config.dir_plots, cloudName + "QuadrantDivision.png")

saveScriptLogPath = os.path.join(config.dir_root, config.dir_fileOutput, cloudName, config.dir_logs, "Script3Log.txt")

# -------- Matched rm and extinction data
MatchedRMExtincPath = os.path.join(config.dir_root, config.dir_fileOutput, cloudName, config.prefix_RMExtinctionMatch + cloudName + '.txt')
# -------- Matched rm and extinction data.

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
Av_threshold = None
if abs(regionOfInterest.cloudLatitude) < config.offDiskLatitude:
    Av_threshold = config.onDiskAvThresh
else:
    Av_threshold = config.offDiskAvThresh
# ---- Log info
logging.info(loggingDivider)
logging.info('Potential reference points with a matched extinction value less than the extinction threshold set in the starting settings configuration are considered candidates.')
logging.info('\t-For clouds that appear near the disk, an appropriate threshold value is {}.'.format(config.onDiskAvThresh))
logging.info('\t-For clouds that appear off the disk, an appropriate threshold value is {}.'.format(config.offDiskAvThresh))
logging.info("{}'s absolute latitude is: {}".format(cloudName, abs(regionOfInterest.cloudLatitude)))
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

#============================================================================================================

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
if saveFilePath_ALlPotentialRefPoints is not None:
    AllPotentialRefPoints.to_csv(saveFilePath_ALlPotentialRefPoints, index=False)
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
#============================================================================================================
# -------- PREPARE TO PLOT ALL POTENTIAL REFERENCE POINTS --------
title = 'All Potential Reference Points' + ' in the ' + cloudName + ' region\n'
plotRefPoints(AllPotentialRefPoints, hdu, regionOfInterest, title)
# ---- Display or save the figure
saveFigurePath_RefPointMap = saveFigureDir_RefPointMap + os.sep + 'RefPointMap_AllPotentialRefPoints.png'
plt.savefig(saveFigurePath_RefPointMap)
plt.close()
# ---- Display or save the figure.
# ---- Log info
logging.info(loggingDivider)
logging.info('Saving the map: ' + title + ' to '+saveFigurePath_RefPointMap)
# ---- Log info
# -------- CREATE A FIGURE - ALL POTENTIAL REF POINTS MAP. --------

#============================================================================================================

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
nearHighExtinctReject = [item for item in PotRefPoints if item in nearHighExtinctionRegion and config.useNearExtinctionRemove]
farHighExtinctReject = [item for item in PotRefPoints if item in farHighExtinctionRegion and config.useFarExtinctionRemove]

RejectedReferencePoints += nearHighExtinctReject
RejectedReferencePoints += farHighExtinctReject

PotRefPoints = [item for item in PotRefPoints if item not in nearHighExtinctReject]
PotRefPoints = [item for item in PotRefPoints if item not in farHighExtinctReject]
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
# ---- Log info
# -------- CHECK TO SEE IF ANY POTENTIAL POINTS ARE NEAR A REGION OF HIGH EXTINCTION. --------

#============================================================================================================
# -------- PREPARE TO PLOT NEAR HIGH EXTINCTION REJECTED REFERENCE POINTS --------
RejectedRefPoints = AllPotentialRefPoints.loc[nearHighExtinctReject].sort_values('Extinction_Value')
title = 'All Near-High Extinction Rejected Reference Points' + ' in the ' + cloudName + ' region\n'
plotRefPoints(RejectedRefPoints, hdu, regionOfInterest, title)
# ---- Display or save the figure
saveFigurePath_RefPointMap = saveFigureDir_RefPointMap + os.sep + 'RefPointMap_NearExtinctRejectedRefPoints.png'
plt.savefig(saveFigurePath_RefPointMap)
plt.close()
# ---- Display or save the figure.
# ---- Log info
logging.info(loggingDivider)
logging.info('Saving the map: ' + title + ' to '+saveFigurePath_RefPointMap)
# ---- Log info

#============================================================================================================
# -------- PREPARE TO PLOT FAR FROM HIGH EXTINCTION REFERENCE POINTS --------
RejectedRefPoints = AllPotentialRefPoints.loc[farHighExtinctReject].sort_values('Extinction_Value')
title = 'All Too Far from High Extinction Rejected Reference Points' + ' in the ' + cloudName + ' region\n'
plotRefPoints(RejectedRefPoints, hdu, regionOfInterest, title)
# ---- Display or save the figure
saveFigurePath_RefPointMap = saveFigureDir_RefPointMap + os.sep + 'RefPointMap_FarExtinctRejectedRefPoints.png'
plt.savefig(saveFigurePath_RefPointMap)
plt.close()
# ---- Display or save the figure.
# ---- Log info
logging.info(loggingDivider)
logging.info('Saving the map: ' + title + ' to '+saveFigurePath_RefPointMap)
# ---- Log info

#============================================================================================================
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
# ---- Log info
logging.info(loggingDivider)
logging.info('We will now check if any of the potential reference points have anomalous rotation measure values.')
logging.info("\t-Anomalous rotation measure values have been defined in the starting configuration to be greater or less than {} standard deviations from the mean (rm < {:.2f}rad/m^2 or"
                                   " rm > {:.2f}rad/m^2)".format(coeffSTD, rm_lowerLimit, rm_upperLimit))
logging.info('As per configuration settings, anomalous points will be removed: {}'.format(config.useAnomalousSTDNumRemove))
logging.info('The potential reference point(s) {} have anomalous rotation measure values'.format(anomalousRMIndex))
logging.info('As such, the remaining points by their IDs are: \n {}'.format(PotRefPoints))
# ---- Log info
# -------- CHECK TO SEE IF ANY POTENTIAL POINTS HAVE ANOMALOUS RM VALUES. --------

#============================================================================================================
# -------- PREPARE TO PLOT ANOMALOUS REJECTED REFERENCE POINTS --------
RejectedRefPoints = AllPotentialRefPoints.loc[anomalousReject].sort_values('Extinction_Value')
title = 'All Anomalous RM Rejected Reference Points' + ' in the ' + cloudName + ' region\n'
plotRefPoints(RejectedRefPoints, hdu, regionOfInterest, title)
# ---- Display or save the figure
saveFigurePath_RefPointMap = saveFigureDir_RefPointMap + os.sep + 'RefPointMap_AnomalousRMRejectedRefPoints.png'
plt.savefig(saveFigurePath_RefPointMap)
plt.close()
# ---- Display or save the figure.
# ---- Log info
logging.info(loggingDivider)
logging.info('Saving the map: ' + title + ' to '+saveFigurePath_RefPointMap)
# ---- Log info

#============================================================================================================
# -------- PREPARE TO PLOT ALL REJECTED REFERENCE POINTS --------
RejectedRefPoints = AllPotentialRefPoints.loc[RejectedReferencePoints].sort_values('Extinction_Value')
title = 'All Rejected Reference Points' + ' in the ' + cloudName + ' region\n'
plotRefPoints(RejectedRefPoints, hdu, regionOfInterest, title)

# ---- Display or save the figure
saveFigurePath_RefPointMap = saveFigureDir_RefPointMap + os.sep + 'RefPointMap_AllRejectedRefPoints.png'
plt.savefig(saveFigurePath_RefPointMap)
plt.close()
# ---- Display or save the figure.
# ---- Log info
logging.info(loggingDivider)
logging.info('Saving the map: ' + title + ' to '+saveFigurePath_RefPointMap)
# ---- Log info
# -------- CREATE A FIGURE - ALL REJECTED REF POINTS MAP. --------

#============================================================================================================
# -------- PREPARE TO PLOT REMAINING REFERENCE POINTS --------
RemainingRefPoints = AllPotentialRefPoints.loc[PotRefPoints].sort_values('Extinction_Value')
title = 'All Remaining Reference Points' + ' in the ' + cloudName + ' region\n'
plotRefPoints(RemainingRefPoints, hdu, regionOfInterest, title)
# ---- Display or save the figure
saveFigurePath_RefPointMap = saveFigureDir_RefPointMap + os.sep + 'RefPointMap_RemainingRefPoints.png'
plt.savefig(saveFigurePath_RefPointMap)
plt.close()
# ---- Display or save the figure.
# ---- Log info
logging.info(loggingDivider)
logging.info('Saving the map: ' + title + ' to '+saveFigurePath_RefPointMap)
# ---- Log info
# -------- CREATE A FIGURE - REMAINING REF POINTS MAP. --------
#============================================================================================================
# -------- PREPARE TO PLOT REMAINING AND REJECTED REFERENCE POINTS --------
refPoints = AllPotentialRefPoints.loc[PotRefPoints].sort_values('Extinction_Value')
nearExtRefPoints = AllPotentialRefPoints.loc[nearHighExtinctReject].sort_values('Extinction_Value')
farExtRefPoints = AllPotentialRefPoints.loc[farHighExtinctReject].sort_values('Extinction_Value')
anomRefPoints = AllPotentialRefPoints.loc[anomalousReject].sort_values('Extinction_Value')
RejectedRefPoints = AllPotentialRefPoints.loc[RejectedReferencePoints].sort_values('Extinction_Value')

fig, ax = pt.extinctionPlot(hdu, regionOfInterest)
title = 'All Potential Reference Points Sorted in the ' + cloudName + ' region\n'
plt.title(title, fontsize=12, y=1.08)

# -------- PREPARE TO PLOT REFERENCE POINTS --------
labels = list(refPoints['ID#'])
Ra = list(refPoints['Ra(deg)'])
Dec = list(refPoints['Dec(deg)'])
RM = list(refPoints['Rotation_Measure(rad/m2)'])
# ---- Convert Ra and Dec of reference points into pixel values of the fits file
x, y = cl.RADec2xy(Ra, Dec, wcs)
# ---- Convert Ra and Dec of reference points into pixel values of the fits file.
c, s = rmpl.rm2RGB(RM)
ax.scatter(x, y, marker='o', facecolor=c, s=s, edgecolors='black')
# -------- PREPARE TO PLOT REFERENCE POINTS. --------

# ---- Annotate the chosen reference points
pt.labelPoints(ax, labels, x, y)
# ---- Annotate the chosen reference points

# -------- PREPARE TO PLOT REFERENCE POINTS --------
idsNear = [str(i) for i in list(nearExtRefPoints['ID#'])]
idsFar = [str(i) for i in list(farExtRefPoints['ID#'])]
idsAnom = [str(i) for i in list(anomRefPoints['ID#'])]

#Todo: If the thing is rejected for multiple reasons, this is not tracked!
labelsRej = [str(i) for i in list(RejectedRefPoints['ID#'])]
labelsRej = [i + ',n' if i in idsNear else i for i in labelsRej]
labelsRej = [i + ',f' if i in idsFar else i for i in labelsRej]
labelsRej = [i + ',a' if i in idsAnom else i for i in labelsRej]

RaRej = list(RejectedRefPoints['Ra(deg)'])
DecRej = list(RejectedRefPoints['Dec(deg)'])
RMRej = list(RejectedRefPoints['Rotation_Measure(rad/m2)'])
# ---- Convert Ra and Dec of reference points into pixel values of the fits file
xRej, yRej = cl.RADec2xy(RaRej, DecRej, wcs)
# ---- Convert Ra and Dec of reference points into pixel values of the fits file.
c, s = rmpl.rm2G(RMRej)
ax.scatter(xRej, yRej, marker='o', facecolor=c, s=s, edgecolors='black')
# -------- PREPARE TO PLOT REFERENCE POINTS. --------

# ---- Annotate the chosen reference points
pt.labelPoints(ax, labelsRej, xRej, yRej)
# ---- Annotate the chosen reference points
# -------- CREATE A FIGURE - ALL REF POINTS MAP. --------

# ---- Style the legend
marker1 = plt.scatter([], [], s=10, facecolor=(1, 1, 1, 0.7), edgecolor='black')
marker2 = plt.scatter([], [], s=50, facecolor=(1, 1, 1, 0.7), edgecolor='black')
marker3 = plt.scatter([], [], s=100, facecolor=(1, 1, 1, 0.7), edgecolor='black')
marker4 = plt.scatter([], [], s=200, facecolor=(1, 1, 1, 0.7), edgecolor='black')
marker5 = plt.scatter([], [], s=100, facecolor=(1, 0, 0, 0.7), edgecolor='black')
marker6 = plt.scatter([], [], s=100, facecolor=(0, 0, 1, 0.7), edgecolor='black')
marker7 = plt.scatter([], [], s=100, facecolor=(0, 1, 0, 0.7), edgecolor='black')
legend_markers = [marker1, marker2, marker3, marker4, marker5, marker6, marker7]

labels = [
    str(10) + ' rad m' + r'$^{-2}$',
    str(50) + ' rad m' + r'$^{-2}$',
    str(100) + ' rad m' + r'$^{-2}$',
    str(200) + ' rad m' + r'$^{-2}$',
    'Negative RM',
    'Positive RM',
    'Rejected Point']

legend = plt.legend(handles=legend_markers, labels=labels, scatterpoints=1)

frame = legend.get_frame()
frame.set_facecolor('1')
frame.set_alpha(0.4)
# ---- Style the legend.

# ---- Display or save the figure
saveFigurePath_RefPointMap = saveFigureDir_RefPointMap + os.sep + 'RefPointMap_RemainingAndRejectedRefPoints.png'
plt.savefig(saveFigurePath_RefPointMap)
plt.close()
# ---- Display or save the figure.
# ---- Log info
logging.info(loggingDivider)
logging.info('Saving the map: ' + title + ' to '+saveFigurePath_RefPointMap)
# ---- Log info
# -------- CREATE A FIGURE - REMAINING AND REJECTED REF POINTS MAP. --------
#============================================================================================================

# -------- FINALIZE REMAINING POINTS AFTER WINNOWING FROM PRIOR STAGES --------
chosenRefPoints_Num = [int(np.round(i)) for i in PotRefPoints]
AllPotentialRefPoints = AllPotentialRefPoints.loc[chosenRefPoints_Num].sort_values('Extinction_Value').reset_index()

logging.info(loggingDivider)
logging.info("The Remaining Reference Points will be:")
logging.info(PotRefPoints)
logging.info("The Chosen data is thus:")
logging.info(AllPotentialRefPoints)
# -------- FINALIZE REMAINING POINTS AFTER WINNOWING FROM PRIOR STAGES --------

#============================================================================================================
# -------- FIND REGIONS TO SPLIT THE CLOUD INTO. --------
cloudCenterX, cloudCenterY = rjl.findWeightedCenter(hdu.data, regionOfInterest.xmin, regionOfInterest.xmax, regionOfInterest.ymin, regionOfInterest.ymax)
m, b = rjl.getDividingLine(hdu.data, regionOfInterest.xmin, regionOfInterest.xmax, regionOfInterest.ymin, regionOfInterest.ymax)
mPerp, bPerp = rjl.getPerpendicularLine(cloudCenterX, cloudCenterY, m)
# -------- FIND REGIONS TO SPLIT THE CLOUD INTO. --------

# -------- SORT REF POINTS INTO THESE REGIONS. --------
Q1, Q2, Q3, Q4 = rjl.sortQuadrants(list(AllPotentialRefPoints.index), AllPotentialRefPoints['Extinction_Index_x'], AllPotentialRefPoints['Extinction_Index_y'], m, b, mPerp, bPerp)
# ---- Sort into quadrant
# -------- SORT REF POINTS INTO THESE REGIONS. --------

# -------- Calculate Results. --------
minSamples = config.minPointsPerQuadrant
Q1Less = len(Q1) < minSamples
Q2Less = len(Q2) < minSamples
Q3Less = len(Q3) < minSamples
Q4Less = len(Q4) < minSamples

quadrantsUndersampled = 0
quadrantsUndersampled = quadrantsUndersampled + 1 if Q1Less else quadrantsUndersampled
quadrantsUndersampled = quadrantsUndersampled + 1 if Q2Less else quadrantsUndersampled
quadrantsUndersampled = quadrantsUndersampled + 1 if Q3Less else quadrantsUndersampled
quadrantsUndersampled = quadrantsUndersampled + 1 if Q4Less else quadrantsUndersampled

# -------- Calculate Results. --------

# -------- OUTPUT RESULTS. --------
logging.info(loggingDivider)
logging.info("The chosen reference points, sorted by quadrant, are:")
logging.info("Q1: {}".format(Q1))
logging.info("Q2: {}".format(Q2))
logging.info("Q3: {}".format(Q3))
logging.info("Q4: {}".format(Q4))
logging.info("As defined in the starting configuration, a quadrant does not have enough points sampled if there are less than {} points in the quadrant chosen.".format(minSamples))
logging.info("Warning: {} quadrants have less than {} points sampled!".format(quadrantsUndersampled, minSamples))
logging.info("If 1 or more quadrants have insufficient points sampled at this stage,")
logging.info("consider raising your extinction threshold in your start settings configuration and trying again!")
# -------- OUTPUT RESULTS. --------

#============================================================================================================

# -------- FIND OPTIMAL NUMBER OF REFERENCE POINTS USING "ALL POTENTIAL REFERENCE POINTS" --------
OptimalNumRefPoints_from_AllPotentialRefPoints = FindOptimalRefPoints(regionOfInterest, AllPotentialRefPoints, saveFigurePath_BLOSvsNRef_AllPotentialRefPoints)
# -------- Solidify reference points. --------
chosenRefPoints_Num = [i for i in range(OptimalNumRefPoints_from_AllPotentialRefPoints)] if config.useStableMinimum else [i for i in range(len(AllPotentialRefPoints.index))]
#chosenRefPoints = AllPotentialRefPoints #If we ignore the algorithm.
chosenRefPoints = AllPotentialRefPoints.loc[chosenRefPoints_Num].sort_values('Extinction_Value')

# -------- SORT REF POINTS INTO THESE REGIONS. --------
Q1c, Q2c, Q3c, Q4c = rjl.sortQuadrants(list(chosenRefPoints.index), chosenRefPoints['Extinction_Index_x'], chosenRefPoints['Extinction_Index_y'], m, b, mPerp, bPerp)
# -------- SORT REF POINTS INTO THESE REGIONS. --------

Q1Undersampled = len(Q1c) < minSamples and not Q1Less
Q2Undersampled = len(Q2c) < minSamples and not Q2Less
Q3Undersampled = len(Q3c) < minSamples and not Q3Less
Q4Undersampled = len(Q4c) < minSamples and not Q4Less

minSamples = []
if Q1Undersampled:
    for i in range(min(len(Q1)-len(Q1c), config.minPointsPerQuadrant-len(Q1c))):
        minSamples.append(Q1[i])
if Q2Undersampled:
    for i in range(min(len(Q2) - len(Q2c), config.minPointsPerQuadrant - len(Q2c))):
        minSamples.append(Q2[i])
if Q3Undersampled:
    for i in range(min(len(Q3) - len(Q2c), config.minPointsPerQuadrant - len(Q3c))):
        minSamples.append(Q3[i])
if Q4Undersampled:
    for i in range(min(len(Q4) - len(Q4c), config.minPointsPerQuadrant - len(Q4c))):
        minSamples.append(Q4[i])
minSamples = max(minSamples) if len(minSamples) > 0 else max(chosenRefPoints_Num)
minSamples = minSamples+1 #Account for the index shift.

chosenRefPoints_After_Quadrants_Num = [i for i in range(minSamples)] if config.useQuadrantEnforce else chosenRefPoints_Num
#chosenRefPoints = AllPotentialRefPoints #If we ignore the algorithm.
chosenRefPoints = AllPotentialRefPoints.loc[chosenRefPoints_After_Quadrants_Num].sort_values('Extinction_Value')

# ---- Log info
logging.info(loggingDivider)
logging.info('By analyzing the stability of calculated BLOS values as a function of number of reference points from 1 to the '
      'total number of reference points ({}):'.format(len(AllPotentialRefPoints)))
logging.info("Given this information, the recommended reference points are {}.".format([i + 1 for i in chosenRefPoints_Num]))
logging.info("Next, minimum quadrant sampling is accounted for.")
logging.info("The chosen reference points, sorted by quadrant, are:")
logging.info("Q1: {}".format(Q1c))
logging.info("Q2: {}".format(Q2c))
logging.info("Q3: {}".format(Q3c))
logging.info("Q4: {}".format(Q4c))
logging.info("Additional points are taken until quadrants which could meet the minimum sampling criteria set in the configuration start settings,")
logging.info("but do not from the stability-recommended points, meet the minimum sampling criteria.")
logging.info("Given this information, the recommended reference points are {}.".format([i + 1 for i in chosenRefPoints_After_Quadrants_Num]))
logging.info("Given this information, the remaining table is \n {}.".format(chosenRefPoints))
logging.info('Please review the BLOS trend stability plot at {}.'.format(saveFigurePath_BLOSvsNRef_AllPotentialRefPoints))
# ---- Log info

# -------- Solidify reference points. --------

#======================================================================================================================
# -------- PREPARE TO PLOT CHOSEN REFERENCE POINTS --------
title = 'All Chosen Reference Points' + ' in the ' + cloudName + ' region\n'
plotRefPoints(chosenRefPoints, hdu, regionOfInterest, title)

# ---- Display or save the figure
saveFigurePath_RefPointMap = saveFigureDir_RefPointMap + os.sep + 'RefPointMap_ChosenRefPoints.png'
plt.savefig(saveFigurePath_RefPointMap)
plt.close()
# ---- Display or save the figure.
# ---- Log info
logging.info(loggingDivider)
logging.info('Saving the map: ' + title + ' to '+saveFigurePath_RefPointMap)
# ---- Log info
# -------- CREATE A FIGURE - ALL REJECTED REF POINTS MAP. --------

#======================================================================================================================

# -------- REASSESS STABILITY --------
'''
We are going to start the plot off with all of the chosen reference points
 - which are in order of increasing extinction.  They may have jumps but this is okay
However, we also want to include points which come after the chosen reference points
The following selects all of the chosen reference points and then adds any of the potential reference points with
extinction greater than the extinction of the last chosen reference point/
'''
RefPoints = chosenRefPoints[:-1].append(AllPotentialRefPoints.set_index('ID#').
                                        loc[list(chosenRefPoints['ID#'])[-1]:].reset_index())\
    .reset_index(drop=True)

DataNoRef = findTrendData(RefPoints, matchedRMExtinctionData, regionOfInterest)

# -------- CREATE A FIGURE --------
plt.figure(figsize=(6, 4), dpi=120, facecolor='w', edgecolor='k')

plt.title('Calculated BLOS value as a function of the number of reference points \n ' + cloudName, fontsize=12,
          y=1.08)
plt.xlabel('Number of reference points')
plt.ylabel('Calculated BLOS value ' + r'($\mu G$)')

x = [int(col) for col in DataNoRef.columns]
plt.xticks(x, list(DataNoRef.columns))

cmap = plt.get_cmap('terrain')
colors = [cmap(i) for i in np.linspace(0, 1, len(DataNoRef.index))]

# For each BLOS Point
for i, number in enumerate(DataNoRef.index):
    plt.plot(x, list(DataNoRef.loc[number]), '-o', color=colors[i], markersize=3)

yLower, yUpper = plt.ylim()
plt.vlines(OptimalNumRefPoints_from_AllPotentialRefPoints, yLower, yUpper, color='black', label='Suggested optimal '
                                                                                                'number of reference '
                                                                                                'points')
plt.legend(loc='center right', bbox_to_anchor=(1.1, 0.5), ncol=2, framealpha=1)

plt.savefig(saveFigurePath_BLOSvsNRef_ChosenPotentialRefPoints)
#plt.show()
plt.close()

logging.info(loggingDivider)
logging.info('Saving the BLOS stability reassessment figure to '+saveFigurePath_BLOSvsNRef_ChosenPotentialRefPoints)

# -------- CREATE A FIGURE. --------
# -------- REASSESS STABILITY. --------

#======================================================================================================================
# -------- CALCULATE AND SAVE REFERENCE VALUES --------
#Even quadrant weighting.

# -------- SORT REF POINTS INTO THESE REGIONS. --------
Q1c, Q2c, Q3c, Q4c = rjl.sortQuadrants(list(chosenRefPoints.index), chosenRefPoints['Extinction_Index_x'], chosenRefPoints['Extinction_Index_y'], m, b, mPerp, bPerp)
# -------- SORT REF POINTS INTO THESE REGIONS. --------
'''
refRM = 0.0
refAvgErr = 0.0
refRMStd = 0.0
refExtinc = 0.0
totalQuadrants = 0
for quadrant in [Q1c, Q2c, Q3c, Q4c]:
    refRM += np.mean(chosenRefPoints.loc[quadrant]['Rotation_Measure(rad/m2)']) if len(quadrant) > 0 else 0.0
    refAvgErr += np.mean(chosenRefPoints.loc[quadrant]['RM_Err(rad/m2)']) if len(quadrant) > 0 else 0.0
    refRMStd += (np.std(chosenRefPoints.loc[quadrant]['Rotation_Measure(rad/m2)'], ddof=1) / np.sqrt(len(chosenRefPoints.loc[quadrant]['Rotation_Measure(rad/m2)']))) if len(quadrant) > 0 else 0.0
    refExtinc += np.mean(chosenRefPoints.loc[quadrant]['Extinction_Value']) if len(quadrant) > 0 else 0.0
    totalQuadrants += 1.0 if len(quadrant) > 0 else 0.0

refRM = refRM/totalQuadrants if totalQuadrants > 0 else refRM
refAvgErr = refAvgErr/totalQuadrants if totalQuadrants > 0 else refAvgErr
refRMStd = refRMStd/totalQuadrants if totalQuadrants > 0 else refRMStd
refExtinc = refExtinc/totalQuadrants if totalQuadrants > 0 else refExtinc
'''
#No weighting
refRM = np.mean(chosenRefPoints['Rotation_Measure(rad/m2)'])
refAvgErr = np.mean(chosenRefPoints['RM_Err(rad/m2)'])
refRMStd = np.std(chosenRefPoints['Rotation_Measure(rad/m2)'], ddof=1) / np.sqrt(len(chosenRefPoints['Rotation_Measure(rad/m2)']))
refExtinc = np.mean(chosenRefPoints['Extinction_Value'])

cols = ['Number of Reference Points', 'Reference Extinction', 'Reference RM', 'Reference RM AvgErr',
        'Reference RM Std']
referenceData = pd.DataFrame(columns=cols)

referenceData['Number of Reference Points'] = [len(chosenRefPoints)]
referenceData['Reference RM'] = [refRM]
referenceData['Reference RM AvgErr'] = [refAvgErr]

# Standard error of the sampled mean:
referenceData['Reference RM Std'] = [refRMStd]
referenceData['Reference Extinction'] = [refExtinc]
referenceData.to_csv(saveFilePath_ReferenceData, index=False)

logging.info(loggingDivider)
logging.info('Reference values were saved to {}'.format(saveFilePath_ReferenceData))
print('Reference values were saved to {}'.format(saveFilePath_ReferenceData))
# -------- CALCULATE AND SAVE REFERENCE VALUES. --------

# -------- SAVE REFERENCE POINTS  --------
chosenRefPoints.to_csv(saveFilePath_ReferencePoints, index=False)

logging.info(loggingDivider)
logging.info('Chosen reference points were saved to {}'.format(saveFilePath_ReferencePoints))
print('Chosen reference points were saved to {}'.format(saveFilePath_ReferencePoints))
# -------- SAVE REFERENCE POINTS. --------

#============================================================================================================