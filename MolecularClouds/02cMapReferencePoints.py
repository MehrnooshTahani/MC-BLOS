import os

import pandas as pd
import numpy as np
import math

from astropy.wcs import WCS
from astropy.io import fits
from astropy.coordinates import SkyCoord

import matplotlib.pyplot as plt

import LocalLibraries.ConversionLibrary as cl
from LocalLibraries.RegionOfInterest import Region

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

# -------- Filtered rm and extinction data
FilteredRMExtincPath = os.path.join(config.dir_root, config.dir_fileOutput, cloudName, config.prefix_RMExtinctionFiltered + cloudName + '.txt')
# -------- Filtered rm and extinction data.

NearRejectedRefPointsPath = os.path.join(config.dir_root, config.dir_fileOutput, cloudName, config.prefix_RMExtinctionNearRej + cloudName + '.txt')
FarRejectedRefPointsPath = os.path.join(config.dir_root, config.dir_fileOutput, cloudName, config.prefix_RMExtinctionFarRej + cloudName + '.txt')
AnomalousRejectedRefPointsPath = os.path.join(config.dir_root, config.dir_fileOutput, cloudName, config.prefix_RMExtinctionAnomRej + cloudName + '.txt')
RejectedRefPointsPath = os.path.join(config.dir_root, config.dir_fileOutput, cloudName, config.prefix_RMExtinctionRej + cloudName + '.txt')
RemainingRefPointsPath = os.path.join(config.dir_root, config.dir_fileOutput, cloudName, config.prefix_RMExtinctionRemaining + cloudName + '.txt')

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
AllPotentialRefPoints = pd.read_csv(saveFilePath_ALlPotentialRefPoints)

NearRejectedRefPoints = pd.read_csv(NearRejectedRefPointsPath)
FarRejectedRefPoints = pd.read_csv(FarRejectedRefPointsPath)
AnomalousRejectedRefPoints = pd.read_csv(AnomalousRejectedRefPointsPath)
RejectedRefPoints = pd.read_csv(RejectedRefPointsPath)
RemainingRefPoints = pd.read_csv(RemainingRefPointsPath)
# ---- LOAD AND UNPACK MATCHED RM AND EXTINCTION DATA

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
# -------- PREPARE TO PLOT NEAR HIGH EXTINCTION REJECTED REFERENCE POINTS --------
title = 'All Near-High Extinction Rejected Reference Points' + ' in the ' + cloudName + ' region\n'
plotRefPoints(NearRejectedRefPoints, hdu, regionOfInterest, title)
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
title = 'All Too Far from High Extinction Rejected Reference Points' + ' in the ' + cloudName + ' region\n'
plotRefPoints(FarRejectedRefPoints, hdu, regionOfInterest, title)
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
# -------- PREPARE TO PLOT ANOMALOUS REJECTED REFERENCE POINTS --------
title = 'All Anomalous RM Rejected Reference Points' + ' in the ' + cloudName + ' region\n'
plotRefPoints(AnomalousRejectedRefPoints, hdu, regionOfInterest, title)
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
refPoints = RemainingRefPoints
nearExtRefPoints = NearRejectedRefPoints
farExtRefPoints = FarRejectedRefPoints
anomRefPoints = AnomalousRejectedRefPoints
RejectedRefPoints = RejectedRefPoints

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

labelsRej = [str(i) for i in list(RejectedRefPoints['ID#'])]
labelsRejAdditions = dict.fromkeys(labelsRej, "")
for i in idsNear: labelsRejAdditions[i] += ",n"
for i in idsFar: labelsRejAdditions[i] += ",f"
for i in idsAnom: labelsRejAdditions[i] += ",a"
labelsRej = [label + labelsRejAdditions[label] for label in labelsRej]

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