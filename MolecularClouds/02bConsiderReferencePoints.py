"""
This is the third stage of the BLOSMapping method where the reference points are determined
"""
import os

import pandas as pd
import numpy as np

from astropy.wcs import WCS
from astropy.io import fits

import matplotlib.pyplot as plt

from LocalLibraries.RegionOfInterest import Region

from LocalLibraries.FindOptimalRefPoints import stabilityTrendGraph
from LocalLibraries.FindOptimalRefPoints import findTrendData
from LocalLibraries.FindOptimalRefPoints import FindOptimalRefPoints

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
MatchedRMExtincPath = os.path.join(config.dir_root, config.dir_fileOutput, cloudName, config.prefix_RMExtinctionMatch + cloudName + '.txt')
# Filtered rm and extinction data
FilteredRMExtincPath = os.path.join(config.dir_root, config.dir_fileOutput, cloudName, config.prefix_RMExtinctionFiltered + cloudName + '.txt')
# ---- Input Files

# ---- Output Files
saveFilePath_ReferencePoints = os.path.join(config.dir_root, config.dir_fileOutput, cloudName, config.prefix_selRefPoints + cloudName + '.txt')
saveFilePath_ReferenceData = os.path.join(config.dir_root, config.dir_fileOutput, cloudName, config.prefix_refData + cloudName + '.txt')

saveFigurePath_BLOSvsNRef_AllPotentialRefPoints = os.path.join(config.dir_root, config.dir_fileOutput, cloudName, config.dir_plots, 'BLOS_vs_NRef_AllPotentialRefPoints.png')
saveFigurePath_BLOSvsNRef_ChosenPotentialRefPoints = os.path.join(config.dir_root, config.dir_fileOutput, cloudName, config.dir_plots, 'BLOS_vs_NRef_ChosenRefPoints.png')

saveScriptLogPath = os.path.join(config.dir_root, config.dir_fileOutput, cloudName, config.dir_logs, "Script2bLog.txt")
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

# ---- LOAD AND UNPACK FILTERED RM AND EXTINCTION DATA
FilteredRefPoints = pd.read_csv(FilteredRMExtincPath)
# ---- LOAD AND UNPACK FILTERED RM AND EXTINCTION DATA

#============================================================================================================
# -------- FIND REGIONS TO SPLIT THE CLOUD INTO. --------
cloudCenterX, cloudCenterY = rjl.findWeightedCenter(hdu.data, regionOfInterest.xmin, regionOfInterest.xmax, regionOfInterest.ymin, regionOfInterest.ymax)
m, b = rjl.getDividingLine(hdu.data, regionOfInterest.xmin, regionOfInterest.xmax, regionOfInterest.ymin, regionOfInterest.ymax)
mPerp, bPerp = rjl.getPerpendicularLine(cloudCenterX, cloudCenterY, m)
# -------- FIND REGIONS TO SPLIT THE CLOUD INTO. --------

# -------- SORT REF POINTS INTO THESE REGIONS. --------
Q1, Q2, Q3, Q4 = rjl.sortQuadrants(list(FilteredRefPoints.index), FilteredRefPoints['Extinction_Index_x'], FilteredRefPoints['Extinction_Index_y'], m, b, mPerp, bPerp)
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
logging.info("The filtered reference points, sorted by quadrant, are:")
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
OptimalNumRefPoints_from_AllPotentialRefPoints = FindOptimalRefPoints(regionOfInterest, FilteredRefPoints, saveFigurePath_BLOSvsNRef_AllPotentialRefPoints)
# -------- Solidify reference points. --------
chosenRefPoints_Num = [i for i in range(OptimalNumRefPoints_from_AllPotentialRefPoints)] if config.useStableMinimum else [i for i in range(len(FilteredRefPoints.index))]
chosenRefPoints = FilteredRefPoints.loc[chosenRefPoints_Num].sort_values('Extinction_Value')

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
chosenRefPoints = FilteredRefPoints.loc[chosenRefPoints_After_Quadrants_Num].sort_values('Extinction_Value')

# ---- Log info
logging.info(loggingDivider)
logging.info('By analyzing the stability of calculated BLOS values as a function of number of reference points from 1 to the '
      'total number of reference points ({}):'.format(len(FilteredRefPoints)))
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

# -------- REASSESS STABILITY --------
'''
We are going to start the plot off with all of the chosen reference points
 - which are in order of increasing extinction.  They may have jumps but this is okay
However, we also want to include points which come after the chosen reference points
The following selects all of the chosen reference points and then adds any of the potential reference points with
extinction greater than the extinction of the last chosen reference point/
'''
RefPoints = chosenRefPoints[:-1].append(FilteredRefPoints.set_index('ID#').
                                        loc[list(chosenRefPoints['ID#'])[-1]:].reset_index())\
    .reset_index(drop=True)

DataNoRef = findTrendData(RefPoints, matchedRMExtinctionData, regionOfInterest)

# -------- CREATE A FIGURE --------

stabilityTrendGraph(DataNoRef, None)
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
# -------- SORT REF POINTS INTO THESE REGIONS. --------
Q1c, Q2c, Q3c, Q4c = rjl.sortQuadrants(list(chosenRefPoints.index), chosenRefPoints['Extinction_Index_x'], chosenRefPoints['Extinction_Index_y'], m, b, mPerp, bPerp)
# -------- SORT REF POINTS INTO THESE REGIONS. --------

# -------- DETERMINE WEIGHTING SCHEME --------
refRM = 0.0
refAvgErr = 0.0
refRMStd = 0.0
refExtinc = 0.0

if config.weightingScheme == "Quadrant Balance":
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