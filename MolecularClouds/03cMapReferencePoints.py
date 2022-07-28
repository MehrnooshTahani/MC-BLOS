import os

import math
import pandas as pd

from astropy.wcs import WCS
from astropy.io import fits

import matplotlib.pyplot as plt

import LocalLibraries.ConversionLibrary as cl
from LocalLibraries.RegionOfInterest import Region

import LocalLibraries.config as config
import LocalLibraries.PlotTemplates as pt
import LocalLibraries.PlotUtils as putil

import logging

def plotRefPoints(refPoints, hdu, regionOfInterest, title):
    '''
    Given a list of reference points and the data of the region in question,
    generates a basic plot of the region with the locations of the reference points.
    :param refPoints: A pandas datatable containing the reference point information.
    :param hdu: HDU entity corresponding to the region
    :param regionOfInterest: RegionOfInterest class corresponding to a given region of interest.
    :param title: Title of the plot.
    :return: fig, ax - the figure and plot axes of the plot.
    '''
    # -------- PREPARE TO PLOT REFERENCE POINTS --------
    labels = list(refPoints['ID#'])
    Ra = list(refPoints['Ra(deg)'])
    Dec = list(refPoints['Dec(deg)'])
    # ---- Convert Ra and Dec of reference points into pixel values of the fits file
    x, y = cl.RADec2xy(Ra, Dec, regionOfInterest.wcs)
    # ---- Convert Ra and Dec of reference points into pixel values of the fits file.
    # -------- PREPARE TO PLOT REFERENCE POINTS. --------

    # -------- CREATE A FIGURE - ALL REF POINTS MAP --------
    fig, ax = pt.extinctionPlot(hdu, regionOfInterest)

    plt.title(title, fontsize=12, y=1.08)
    plt.scatter(x, y, marker='o', facecolor='green', linewidth=.5, edgecolors='black', s=50)
    # ---- Annotate the chosen reference points
    pt.labelPoints(ax, labels, x, y, textFix=config.textFix)
    # ---- Annotate the chosen reference points
    # -------- CREATE A FIGURE - ALL REF POINTS MAP. --------
    return fig, ax

def refPointPlot(titleFragment, saveFragment, cloudName, refPoints, hdu, regionOfInterest):
    '''
    Wrapper function for commonly duplicated code in creating a reference point plot.
    :param titleFragment: Part of the title. String.
    :param saveFragment: Part of the save file name. String.
    :param cloudName: Part of the title. String.
    :param refPoints: Input reference point data to be mapped on the image.
    :param hdu: HDU image file of the region.
    :param regionOfInterest: Region information in a RegionOfInterest class.
    :return: Nothing.
    '''
    # -------- PREPARE TO PLOT REFERENCE POINTS --------
    title = titleFragment + 'Reference Points' + ' in the ' + cloudName + ' region\n'
    plotRefPoints(refPoints, hdu, regionOfInterest, title)
    # ---- Display or save the figure
    saveFigurePath_RefPointMap = saveFigureDir_RefPointMap + os.sep + 'RefPointMap_' + saveFragment + '.png'
    plt.savefig(saveFigurePath_RefPointMap)
    plt.close()
    # ---- Display or save the figure.
    # ---- Log info
    message = 'Saving the map: ' + title + ' to ' + saveFigurePath_RefPointMap
    logging.info(loggingDivider)
    logging.info(message)
    print(message)
    # ---- Log info
    # -------- CREATE A FIGURE - REF POINTS MAP. --------

# -------- LOAD THE REGION OF INTEREST --------
cloudName = config.cloud
regionOfInterest = Region(cloudName)
# -------- LOAD THE REGION OF INTEREST. --------

# -------- DEFINE FILES AND PATHS --------
# ---- Input Files
AllPotRefPointsFile = config.AllPotRefPointFile
ChosenRefPointFile = config.ChosenRefPointFile

NearRejectedRefPointsPath = config.NearExtinctRefPointFile
FarRejectedRefPointsPath = config.FarExtinctRefPointFile
AnomalousRejectedRefPointsPath = config.AnomRefPointFile
RejectedRefPointsPath = config.RejRefPointFile
RemainingRefPointsPath = config.RemainingRefPointFile
# ---- Input Files

# ---- Output Files
saveScriptLogPath = config.Script03cFile
saveFigureDir_RefPointMap = config.CloudPlotsDir

saveQuadrantFigurePath = config.QuadrantDivisionPlotFile #Todo?
saveFigurePath_BLOSvsNRef_AllPotentialRefPoints = config.BLOSvsNRef_AllPlotFile
saveFigurePath_BLOSvsNRef_ChosenPotentialRefPoints = config.BLOSvsNRef_ChosenPlotFile
# ---- Output Files

# -------- DEFINE FILES AND PATHS. --------

# -------- CONFIGURE LOGGING --------
logging.basicConfig(filename=saveScriptLogPath, filemode='w', format=config.logFormat, level=logging.INFO)
loggingDivider = config.logSectionDivider
# -------- CONFIGURE LOGGING --------

# -------- PREPROCESS FITS DATA TYPE. --------
# If fitsDataType is column density, then convert to visual extinction
if regionOfInterest.fitsDataType == 'HydrogenColumnDensity':
    regionOfInterest.hdu.data = regionOfInterest.hdu.data / config.VExtinct_2_Hcol
# -------- PREPROCESS FITS DATA TYPE. --------

# ---- LOAD AND UNPACK MATCHED RM AND EXTINCTION DATA
AllPotentialRefPoints = pd.read_csv(AllPotRefPointsFile, sep=config.dataSeparator)

NearRejectedRefPoints = pd.read_csv(NearRejectedRefPointsPath, sep=config.dataSeparator)
FarRejectedRefPoints = pd.read_csv(FarRejectedRefPointsPath, sep=config.dataSeparator)
AnomalousRejectedRefPoints = pd.read_csv(AnomalousRejectedRefPointsPath, sep=config.dataSeparator)
RejectedRefPoints = pd.read_csv(RejectedRefPointsPath, sep=config.dataSeparator)
RemainingRefPoints = pd.read_csv(RemainingRefPointsPath, sep=config.dataSeparator)

chosenRefPoints = pd.read_csv(ChosenRefPointFile, sep=config.dataSeparator)
# ---- LOAD AND UNPACK MATCHED RM AND EXTINCTION DATA
#======================================================================================================================
refPointPlot("All Potential ", "AllPotentialRefPoints", cloudName, AllPotentialRefPoints, regionOfInterest.hdu, regionOfInterest)
refPointPlot("Near-High Extinction Rejected ", "NearExtinctRejectedRefPoints", cloudName, NearRejectedRefPoints, regionOfInterest.hdu, regionOfInterest)
refPointPlot("Far from High Extinction Rejected ", "FarExtinctRejectedRefPoints", cloudName, FarRejectedRefPoints, regionOfInterest.hdu, regionOfInterest)
refPointPlot("Anomalous RM Rejected ", "AnomalousRMRejectedRefPoints", cloudName, AnomalousRejectedRefPoints, regionOfInterest.hdu, regionOfInterest)
refPointPlot("All Rejected ", "AllRejectedRefPoints", cloudName, RejectedRefPoints, regionOfInterest.hdu, regionOfInterest)
refPointPlot("All Remaining ", "AllRemainingRefPoints", cloudName, RemainingRefPoints, regionOfInterest.hdu, regionOfInterest)
refPointPlot("All Chosen ", "ChosenRefPoints", cloudName, chosenRefPoints, regionOfInterest.hdu, regionOfInterest)
#======================================================================================================================
# -------- PREPARE TO PLOT REMAINING AND REJECTED REFERENCE POINTS --------
refPoints = RemainingRefPoints
nearExtRefPoints = NearRejectedRefPoints
farExtRefPoints = FarRejectedRefPoints
anomRefPoints = AnomalousRejectedRefPoints
RejectedRefPoints = RejectedRefPoints

fig, ax = pt.extinctionPlot(regionOfInterest.hdu, regionOfInterest)
title = 'All Potential Reference Points Sorted in the ' + cloudName + ' region\n'
plt.title(title, fontsize=12, y=1.08)

# -------- PREPARE TO PLOT REFERENCE POINTS --------
labels = list(refPoints['ID#'])
Ra = list(refPoints['Ra(deg)'])
Dec = list(refPoints['Dec(deg)'])
RM = list(refPoints['Rotation_Measure(rad/m2)'])
# ---- Convert Ra and Dec of reference points into pixel values of the fits file
x, y = cl.RADec2xy(Ra, Dec, regionOfInterest.wcs)
# ---- Convert Ra and Dec of reference points into pixel values of the fits file.
c, s = putil.p2RGB(RM)
ax.scatter(x, y, marker='o', facecolor=c, s=s, edgecolors='black')
# -------- PREPARE TO PLOT REFERENCE POINTS. --------

# ---- Annotate the chosen reference points
pt.labelPoints(ax, labels, x, y, textFix=config.textFix)
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
xRej, yRej = cl.RADec2xy(RaRej, DecRej, regionOfInterest.wcs)
# ---- Convert Ra and Dec of reference points into pixel values of the fits file.
c, s = putil.p2C(RMRej, (1, 0, 1))
ax.scatter(xRej, yRej, marker='o', facecolor=c, s=s, edgecolors='black')
# -------- PREPARE TO PLOT REFERENCE POINTS. --------

# ---- Annotate the chosen reference points
pt.labelPoints(ax, labelsRej, xRej, yRej, textFix=config.textFix)
# ---- Annotate the chosen reference points
# -------- CREATE A FIGURE - ALL REF POINTS MAP. --------

# ---- Style the legend
marker1 = plt.scatter([], [], s=10, facecolor=(1, 1, 1, 0.7), edgecolor='black')
marker2 = plt.scatter([], [], s=50, facecolor=(1, 1, 1, 0.7), edgecolor='black')
marker3 = plt.scatter([], [], s=100, facecolor=(1, 1, 1, 0.7), edgecolor='black')
marker4 = plt.scatter([], [], s=200, facecolor=(1, 1, 1, 0.7), edgecolor='black')
marker5 = plt.scatter([], [], s=100, facecolor=(1, 0, 0, 0.7), edgecolor='black')
marker6 = plt.scatter([], [], s=100, facecolor=(0, 0, 1, 0.7), edgecolor='black')
marker7 = plt.scatter([], [], s=100, facecolor=(1, 0, 1, 0.7), edgecolor='black')
legend_markers = [marker1, marker2, marker3, marker4, marker5, marker6, marker7]

labels = [
    str(10) + ' rad m' + r'$^{-2}$',
    str(50) + ' rad m' + r'$^{-2}$',
    str(100) + ' rad m' + r'$^{-2}$',
    str(200) + ' rad m' + r'$^{-2}$',
    'Negative RM',
    'Positive RM',
    'Rejected Off Point']

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
#======================================================================================================================