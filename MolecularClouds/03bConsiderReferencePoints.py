"""
This is the third stage of the BLOSMapping method where the reference points are determined
"""
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt

from LocalLibraries.RegionOfInterest import Region
import LocalLibraries.config as config

import LocalLibraries.OptimalRefPoints as orp
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
# Filtered rm and extinction data
FilteredRMExtinctFile = config.FilteredRMExtinctionFile
# ---- Input Files

# ---- Output Files
QuadDivDataFile = config.QuadDivDataFile

ChosenRefPointFile = config.ChosenRefPointFile
ChosenRefDataFile = config.ChosenRefDataFile

BLOSvsNRef_AllPotRefPointsPlot = config.BLOSvsNRef_AllPlotFile
BLOSvsNRef_ChosenPlotFile = config.BLOSvsNRef_ChosenPlotFile

StabilityTrendDataTablePath = config.StabilityTrendDataTablePath
LogFile = config.Script03bFile
# ---- Output Files

# -------- DEFINE FILES AND PATHS. --------

# -------- CONFIGURE LOGGING --------
logging.basicConfig(filename=LogFile, filemode='w', format=config.logFormat, level=logging.INFO)
loggingDivider = config.logSectionDivider
# -------- CONFIGURE LOGGING --------

# ---- LOAD AND UNPACK MATCHED RM AND EXTINCTION DATA
MatchedRMExtinctionData = pd.read_csv(MatchedRMExtinctFile, sep=config.dataSeparator)
# ---- LOAD AND UNPACK MATCHED RM AND EXTINCTION DATA

# ---- LOAD AND UNPACK FILTERED RM AND EXTINCTION DATA
FilteredRefPoints = pd.read_csv(FilteredRMExtinctFile, sep=config.dataSeparator)
# ---- LOAD AND UNPACK FILTERED RM AND EXTINCTION DATA

#============================================================================================================
# -------- SORT THE AVAILABLE POINTS INTO QUADRANTS RELATIVE TO THE CLOUD, TO ENSURE EVEN SAMPLING --------
# ---- Find the lines which divide the cloud into quadrants.
cloudCenterX, cloudCenterY = rjl.findWeightedCenter(regionOfInterest.hdu.data, regionOfInterest.xmin, regionOfInterest.xmax, regionOfInterest.ymin, regionOfInterest.ymax)
m, b = rjl.getDividingLine(regionOfInterest.hdu.data, regionOfInterest.xmin, regionOfInterest.xmax, regionOfInterest.ymin, regionOfInterest.ymax)
mPerp, bPerp = rjl.getPerpendicularLine(cloudCenterX, cloudCenterY, m)
# ---- Find the lines which divide the cloud into quadrants.

# ---- Sort the points into those quadrants.
Q1, Q2, Q3, Q4 = rjl.sortQuadrants(list(FilteredRefPoints.index), FilteredRefPoints['Extinction_Index_x'], FilteredRefPoints['Extinction_Index_y'], m, b, mPerp, bPerp)
# ---- Sort the points into those quadrants.

# ---- Calculate Results. (They will be used in a later stage)
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
# ---- Calculate Results.

# ---- Save Data
QuadDivCols = ['Cloud Center X', 'Cloud Center Y',
               'Slope of Line Through Cloud', 'Vertical Offset of Line Through Cloud',
               'Slope of Perpendicular Line', 'Vertical Offset of Perpendicular Line']
QuadDivData = pd.DataFrame(columns = QuadDivCols)
QuadDivData['Cloud Center X'] = [cloudCenterX]
QuadDivData['Cloud Center Y'] = [cloudCenterY]
QuadDivData['Slope of Line Through Cloud'] = m
QuadDivData['Vertical Offset of Line Through Cloud'] = b
QuadDivData['Slope of Perpendicular Line'] = mPerp
QuadDivData['Vertical Offset of Perpendicular Line'] = bPerp
QuadDivData.to_csv(QuadDivDataFile, index=False, sep=config.dataSeparator)
# ---- Save Data

# ---- Log results
messages = ["The filtered reference points, sorted by quadrant, are:",
            "Q1: {}".format(Q1),
            "Q2: {}".format(Q2),
            "Q3: {}".format(Q3),
            "Q4: {}".format(Q4),
            "As defined in the starting configuration, a quadrant does not have enough points sampled if there are less than {} points in the quadrant chosen.".format(minSamples),
            "{} quadrants have less than {} points sampled!".format(quadrantsUndersampled, minSamples),
            "If 1 or more quadrants have insufficient points sampled at this stage,",
            "consider raising your extinction threshold in your start settings configuration and trying again!",
            "The lines which divide the cloud into quadrants have been saved to {}.".format(QuadDivDataFile)]
logging.info(loggingDivider)
for message in messages:
    logging.info(message)
# ---- Log results
# -------- SORT THE AVAILABLE POINTS INTO QUADRANTS RELATIVE TO THE CLOUD, TO ENSURE EVEN SAMPLING --------
#============================================================================================================
# -------- FIND OPTIMAL NUMBER OF REFERENCE POINTS --------
# ---- Find the trend data
TrendDataTable = orp.findTrendData(FilteredRefPoints, MatchedRMExtinctionData, regionOfInterest)
TrendDataTable.to_csv(StabilityTrendDataTablePath, sep=config.dataSeparator)
# ---- Find the trend data

# ---- Plot the trend data
fig = orp.plotStabilityTrend(TrendDataTable)
plt.savefig(BLOSvsNRef_AllPotRefPointsPlot)
# ---- Plot the trend data

# ---- Total number of points
TotalNumPoints = len(MatchedRMExtinctionData)
# ---- Total number of points

'''
We can now determine the optimal number of reference points using the calculated BLOS values as a function of 
number of candidate reference points.
 '''
Optimal_NumRefPoints = orp.stabilityCheckAlg(TrendDataTable) #[orp.minRefRMOn(MatchedRMExtinctionData, FilteredRefPoints, 1.5)] #orp.stabilityCheckAlg(TrendDataTable) #[orp.minRefRMOff(FilteredRefPoints, 1)]
# -------- Find the optimal number of reference points using the trend data
# The number of reference points should be greater than 3 and less than half the total number of points
minStablePoints = config.minRefPoints
maxFracPoints = config.maxFracPointNum
Optimal_NumRefPoints_Selection = [value for value in Optimal_NumRefPoints if minStablePoints <= value <= maxFracPoints * TotalNumPoints]
if len(Optimal_NumRefPoints_Selection) < 1:
    messages = ["There is no optimal reference point information with the given parameters!"
                "In the config, the minimum number of points selected by the stability trend algorithm is: {}".format(config.minRefPoints),
                "In the config, the maxinum fraction of points selected by the stability trend algorithm is: {}.".format(config.maxFracPointNum),
                "This corresponds to a maximum number of points: {}".format(maxFracPoints * TotalNumPoints),
                "Please select a larger region, obtain a denser RM Catalogue, or adjust your stability trend requirements.",
                "This analysis will fail."]
    logging.critical(loggingDivider)
    for message in messages:
        logging.critical(message)
        print(message)
OptimalNumRefPoints_from_AllPotentialRefPoints = orp.mode(Optimal_NumRefPoints_Selection)
# -------- Find the optimal number of reference points using the trend data

# -------- Solidify reference points.
chosenRefPoints_Num = [i for i in range(OptimalNumRefPoints_from_AllPotentialRefPoints)] if config.UseOptRefPoints else [i for i in range(len(FilteredRefPoints.index))]
chosenRefPoints = FilteredRefPoints.loc[chosenRefPoints_Num].sort_values('Extinction_Value')
# -------- Solidify reference points.

# -------- FIND OPTIMAL NUMBER OF REFERENCE POINTS --------
#======================================================================================================================
# -------- ENSURE CHOSEN OPTIMAL NUMBER OF POINTS SAMPLES THE QUADRANTS FAIRLY --------
# ---- Sort chosen ref points into quadrants
Q1c, Q2c, Q3c, Q4c = rjl.sortQuadrants(list(chosenRefPoints.index), chosenRefPoints['Extinction_Index_x'], chosenRefPoints['Extinction_Index_y'], m, b, mPerp, bPerp)
# ---- Sort chosen ref points into quadrants

# ---- Check to see which quadrants are undersampled as a result of the optimal selection of points
# A region is undersampled if it no longer makes the minimum samples criteria but previously could.
Q1Undersampled = len(Q1c) < minSamples and not Q1Less
Q2Undersampled = len(Q2c) < minSamples and not Q2Less
Q3Undersampled = len(Q3c) < minSamples and not Q3Less
Q4Undersampled = len(Q4c) < minSamples and not Q4Less
# ---- Check to see which quadrants are undersampled as a result of the optimal selection of points

# ---- Fix the undersampled quadrants by sampling more points until the quadrant has enough points
minSamplesList = []
if Q1Undersampled:
    for i in range(min(len(Q1)-len(Q1c), config.minPointsPerQuadrant-len(Q1c))):
        minSamplesList.append(Q1[i])
if Q2Undersampled:
    for i in range(min(len(Q2) - len(Q2c), config.minPointsPerQuadrant - len(Q2c))):
        minSamplesList.append(Q2[i])
if Q3Undersampled:
    for i in range(min(len(Q3) - len(Q2c), config.minPointsPerQuadrant - len(Q3c))):
        minSamplesList.append(Q3[i])
if Q4Undersampled:
    for i in range(min(len(Q4) - len(Q4c), config.minPointsPerQuadrant - len(Q4c))):
        minSamplesList.append(Q4[i])
minSamples = max(minSamplesList) if len(minSamplesList) > 0 else max(chosenRefPoints_Num)
minSamples = minSamples+1 #Account for the index shift.
# ---- Fix the undersampled quadrants by sampling more points until the quadrant has enough points

# ---- Solidify ref points
chosenRefPoints_After_Quadrants_Num = [i for i in range(minSamples)] if config.useQuadrantEnforce else chosenRefPoints_Num
chosenRefPoints = FilteredRefPoints.loc[chosenRefPoints_After_Quadrants_Num].sort_values('Extinction_Value')
# ---- Solidify ref points

# ---- Log info
messages = ['By analyzing the stability of calculated BLOS values as a function of number of reference points from 1 to the '
      'total number of reference points ({}):'.format(len(FilteredRefPoints)),
            "Given this information, the recommended reference points are {}.".format([i + 1 for i in chosenRefPoints_Num]),
            "Next, minimum quadrant sampling is accounted for.",
            "The chosen reference points, sorted by quadrant, are:",
            "Q1: {}".format(Q1c),
            "Q2: {}".format(Q2c),
            "Q3: {}".format(Q3c),
            "Q4: {}".format(Q4c),
            "Additional points are taken until quadrants which could meet the minimum sampling criteria set in the configuration start settings,",
            "but do not from the stability-recommended points, meet the minimum sampling criteria.",
            "Given this information, the recommended reference points are {}.".format([i + 1 for i in chosenRefPoints_After_Quadrants_Num]),
            "Given this information, the remaining table is \n {}.".format(chosenRefPoints),
            'Please review the BLOS trend stability plot at {}.'.format(BLOSvsNRef_AllPotRefPointsPlot)]
logging.info(loggingDivider)
for message in messages:
    logging.info(message)
# ---- Log info
# -------- ENSURE CHOSEN OPTIMAL NUMBER OF POINTS SAMPLES THE QUADRANTS FAIRLY --------
#======================================================================================================================

# -------- REASSESS STABILITY --------
'''
We are going to start the plot off with all of the chosen reference points
 - which are in order of increasing extinction.  They may have jumps but this is okay
However, we also want to include points which come after the chosen reference points
The following selects all of the chosen reference points and then adds any of the potential reference points with
extinction greater than the extinction of the last chosen reference point/
'''
# ---- Check the trend data of the chosen reference points
#We ignore the last element ([:-1]) because the append adds it back in.
RefPoints = chosenRefPoints[:-1].append(FilteredRefPoints.set_index('ID#').
                                        loc[list(chosenRefPoints['ID#'])[-1]:].reset_index())\
    .reset_index(drop=True)
TrendDataTable = orp.findTrendData(RefPoints, MatchedRMExtinctionData, regionOfInterest)
# ---- Check the trend data of the chosen reference points

# ---- Create a figure
fig = orp.plotStabilityTrend(TrendDataTable)
yLower, yUpper = plt.ylim()
plt.vlines(OptimalNumRefPoints_from_AllPotentialRefPoints, yLower, yUpper, color='black', label='Suggested optimal '
                                                                                                'number of reference '
                                                                                                'points')
#plt.legend(loc='center right', bbox_to_anchor=(1.1, 0.5), ncol=2, framealpha=1)

plt.savefig(BLOSvsNRef_ChosenPlotFile)
#plt.show()
#plt.close()
# ---- Create a figure

# ---- Log info
logging.info(loggingDivider)
logging.info('Saving the BLOS stability reassessment figure to ' + BLOSvsNRef_ChosenPlotFile)
# ---- Log info

# -------- REASSESS STABILITY. --------

#======================================================================================================================
# -------- DETERMINE WEIGHTING SCHEME --------
refRM = 0.0
refAvgErr = 0.0
refRMStd = 0.0
refExtinc = 0.0

if config.weightingScheme == "Quadrant":
    # -------- Sort ref points into quadrants
    Q1c, Q2c, Q3c, Q4c = rjl.sortQuadrants(list(chosenRefPoints.index), chosenRefPoints['Extinction_Index_x'],
                                           chosenRefPoints['Extinction_Index_y'], m, b, mPerp, bPerp)
    # -------- Sort ref points into quadrants
    perQuadrantWeight = 100000000 #Arbitrarily large number for weighting.
    chosenPoints = []
    weightPoints = []
    for quadrant in [Q1c, Q2c, Q3c, Q4c]:
        chosenPoints += quadrant
        weightPoints += [perQuadrantWeight/len(quadrant) for _ in range(len(quadrant))]
    refRM += np.average(chosenRefPoints.loc[chosenPoints]['Rotation_Measure(rad/m2)'], weights = weightPoints)
    refExtinc += np.average(chosenRefPoints.loc[chosenPoints]['Extinction_Value'], weights = weightPoints)
    refAvgErr += np.average(chosenRefPoints.loc[chosenPoints]['RM_Err(rad/m2)'], weights = weightPoints)
    refRMStd += (np.sqrt(np.cov(chosenRefPoints.loc[chosenPoints]['Rotation_Measure(rad/m2)'], aweights=weightPoints)) / np.sqrt(len(chosenRefPoints.loc[chosenPoints]['Rotation_Measure(rad/m2)'])))

else:
    refRM = np.mean(chosenRefPoints['Rotation_Measure(rad/m2)'])
    refAvgErr = np.mean(chosenRefPoints['RM_Err(rad/m2)'])
    refRMStd = np.std(chosenRefPoints['Rotation_Measure(rad/m2)'], ddof=1) / np.sqrt(
        len(chosenRefPoints['Rotation_Measure(rad/m2)']))
    refExtinc = np.mean(chosenRefPoints['Extinction_Value'])
# -------- DETERMINE WEIGHTING SCHEME --------

# -------- CALCULATE AND SAVE REFERENCE VALUES --------
logging.info(loggingDivider)
logging.info("The chosen point weighting scheme is: {}".format(config.weightingScheme))

cols = ['Number of Reference Points', 'Reference Extinction', 'Reference RM', 'Reference RM AvgErr',
        'Reference RM Std']
referenceData = pd.DataFrame(columns=cols)

referenceData['Number of Reference Points'] = [len(chosenRefPoints)]
referenceData['Reference RM'] = [refRM]
referenceData['Reference RM AvgErr'] = [refAvgErr]

# Standard error of the sampled mean:
referenceData['Reference RM Std'] = [refRMStd]
referenceData['Reference Extinction'] = [refExtinc]
referenceData.to_csv(ChosenRefDataFile, index=False, sep=config.dataSeparator)

message = 'Reference values were saved to {}'.format(ChosenRefDataFile)
logging.info(loggingDivider)
logging.info(message)
print(message)
# -------- CALCULATE AND SAVE REFERENCE VALUES. --------

# -------- SAVE REFERENCE POINTS  --------
chosenRefPoints.to_csv(ChosenRefPointFile, index=False, sep=config.dataSeparator)

message = 'Chosen reference points were saved to {}'.format(ChosenRefPointFile)
logging.info(loggingDivider)
logging.info(message)
print(message)
# -------- SAVE REFERENCE POINTS. --------