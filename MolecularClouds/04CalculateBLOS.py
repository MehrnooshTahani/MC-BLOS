"""
This is the fourth stage of the BLOSMapping method where the BLOS values are calculated using the reference points selected in
the previous stage.  This file also produces a scatter plot of BLOS points.
"""
import math
import pandas as pd

import matplotlib.pyplot as plt
from LocalLibraries.RegionOfInterest import Region
from LocalLibraries.CalculateB import CalculateB

import LocalLibraries.MatchedRMExtinctionFunctions as MREF
import LocalLibraries.config as config
import LocalLibraries.PlotTemplates as pt
import LocalLibraries.PlotUtils as putil

import logging

# -------- CHOOSE THE REGION OF INTEREST --------
cloudName = config.cloud
regionOfInterest = Region(cloudName)
# -------- CHOOSE THE REGION OF INTEREST. --------

# -------- DEFINE FILES AND PATHS --------
#Input Files
ChosenRefPointFile = config.ChosenRefPointFile
ChosenRefDataFile = config.ChosenRefDataFile
MatchedRMExtinctFile = config.MatchedRMExtinctionFile

#Output Files
BLOSPointsFile = config.BLOSPointsFile
BLOSPointsPlotFile = config.BLOSPointsPlot
LogFile = config.Script04File
# -------- DEFINE FILES AND PATHS. --------

# -------- CONFIGURE LOGGING --------
logging.basicConfig(filename=LogFile, filemode='w', format=config.logFormat, level=logging.INFO)
# -------- CONFIGURE LOGGING --------

# -------- READ REFERENCE POINT TABLE --------
MatchedRMExtinctTable = pd.read_csv(MatchedRMExtinctFile, sep=config.dataSeparator)
RefPointTable = pd.read_csv(ChosenRefPointFile, sep=config.dataSeparator)
RemainingPointTable = MREF.rmMatchingPts(MatchedRMExtinctTable, RefPointTable)
RefData = pd.read_csv(ChosenRefDataFile, sep=config.dataSeparator)
fiducialRM, fiducialRMAvgErr, fiducialRMStd, fiducialExtinction = MREF.unpackRefData(RefData)
# -------- READ REFERENCE POINT TABLE. --------

# =====================================================================================================================

# -------- CALCULATE BLOS --------
BLOSData = CalculateB(regionOfInterest.AvFilePath, RemainingPointTable, fiducialRM, fiducialRMAvgErr, fiducialRMStd, fiducialExtinction, NegativeExtinctionEntriesChange = config.negScaledExtOption)
BLOSData.to_csv(BLOSPointsFile, index=False, na_rep=config.missingDataRep, sep=config.dataSeparator)

message = 'Saving calculated magnetic field values to ' + BLOSPointsFile
logging.info(message)
print(message)
# -------- CALCULATE BLOS. --------

# =====================================================================================================================

# -------- PREPARE TO PLOT BLOS POINTS --------
n = list(BLOSData['ID#'])
Ra = list(BLOSData['Ra(deg)'])
Dec = list(BLOSData['Dec(deg)'])
BLOS = list(BLOSData['Magnetic_Field(uG)'])
# -------- PREPARE TO PLOT BLOS POINTS. --------
#
# -------- CREATE A FIGURE - BLOS POINT MAP --------
fig = plt.figure(figsize=(12, 10), dpi=120, facecolor='w', edgecolor='k')
ax = fig.add_subplot(111, projection=regionOfInterest.wcs)

plt.title(r'$\rm{B}_{LOS}$' + ' in the {} region\n\n\n'.format(cloudName), fontsize=12, linespacing=1)
im = plt.imshow(regionOfInterest.hdu.data, origin='lower', cmap='BrBG', interpolation='nearest')

# ---- Convert Ra and Dec of points into pixel values of the fits file
x = []  # x pixel coordinate
y = []  # y pixel coordinate
for i in range(len(Ra)):
    pixelRow, pixelColumn = regionOfInterest.wcs.wcs_world2pix(Ra[i], Dec[i], 0)
    x.append(pixelRow)
    y.append(pixelColumn)
# ---- Convert Ra and Dec of points into pixel values of the fits file.
color, size = putil.p2RGB(BLOS, size_cap=1000, scale_factor=0.5)
plt.scatter(x, y, s=size, facecolor=color, marker='o', linewidth=.5, edgecolors='black')

# ---- Annotate the BLOS Points
pt.labelPoints(ax, n, x, y, textFix = config.textFix)
# ---- Annotate the BLOS Points.

# -------- PREPARE TO PLOT REF BLOS POINTS --------
# ---- CALCULATE REF POINT BLOS.
#Utilized only for the plot which includes the reference points used to find the BLOS
RefBLOSData = CalculateB(regionOfInterest.AvFilePath, RefPointTable, fiducialRM, fiducialRMAvgErr, fiducialRMStd, fiducialExtinction, NegativeExtinctionEntriesChange="None")
# ---- CALCULATE REF POINT BLOS.

Refn = list(RefBLOSData['ID#'])
RefRa = list(RefBLOSData['Ra(deg)'])
RefDec = list(RefBLOSData['Dec(deg)'])
RefBLOS = list(RefBLOSData['Magnetic_Field(uG)'])

# -------- PREPARE TO PLOT REF BLOS POINTS. --------
# ---- Convert Ra and Dec of points into pixel values of the fits file
xRef = []  # x pixel coordinate
yRef = []  # y pixel coordinate
for i in range(len(RefRa)):
    pixelRow, pixelColumn = regionOfInterest.wcs.wcs_world2pix(RefRa[i], RefDec[i], 0)
    xRef.append(pixelRow)
    yRef.append(pixelColumn)
# ---- Convert Ra and Dec of points into pixel values of the fits file.
colorRef, sizeRef = putil.p2C(RefBLOS, colour=(0, 1, 0), size_cap=1000, scale_factor=0.5)
plt.scatter(xRef, yRef, s=sizeRef, facecolor=colorRef, marker='o', linewidth=.5, edgecolors='black')

# ---- Annotate the BLOS Points
pt.labelPoints(ax, Refn, xRef, yRef, color = 'magenta', textFix=config.textFix)
# ---- Annotate the BLOS Points.

# ---- Style the main axes and their grid
if not math.isnan(regionOfInterest.xmax) and not math.isnan(regionOfInterest.xmin):
    ax.set_xlim(regionOfInterest.xmin, regionOfInterest.xmax)
if not math.isnan(regionOfInterest.ymax) and not math.isnan(regionOfInterest.ymin):
    ax.set_ylim(regionOfInterest.ymin, regionOfInterest.ymax)

ra = ax.coords[0]
dec = ax.coords[1]
ra.set_major_formatter('d')
dec.set_major_formatter('d')
ra.set_axislabel('RA (degree)')
dec.set_axislabel('Dec (degree)')

dec.set_ticks(number=10)
ra.set_ticks(number=20)
ra.display_minor_ticks(True)
dec.display_minor_ticks(True)
ra.set_minor_frequency(10)

ra.grid(color='black', alpha=0.5, linestyle='solid')
dec.grid(color='black', alpha=0.5, linestyle='solid')
# ---- Style the main axes and their grid.

# ---- Style the overlay and its grid
overlay = ax.get_coords_overlay('galactic')

overlay[0].set_axislabel('Longitude')
overlay[1].set_axislabel('Latitude')

overlay[0].set_ticks(color='grey', number=20)
overlay[1].set_ticks(color='grey', number=20)

overlay.grid(color='grey', linestyle='solid', alpha=0.7)
# ---- Style the overlay and its grid.

# ---- Style the colour bar
if regionOfInterest.fitsDataType == 'HydrogenColumnDensity':
    cb = plt.colorbar(im, ticklocation='right', fraction=0.02, pad=0.145, format='%.0e')
    cb.ax.set_title('Hydrogen Column Density', linespacing=0.5, fontsize=12)
elif regionOfInterest.fitsDataType == 'VisualExtinction':
    cb = plt.colorbar(im, ticklocation='right', fraction=0.02, pad=0.145)
    cb.ax.set_title(' A' + r'$_V$', linespacing=0.5, fontsize=12)
# ---- Style the colour bar.

# ---- Style the legend
marker1 = plt.scatter([], [], s=10/2, facecolor=(1, 1, 1, 0.7), edgecolor='black')
marker2 = plt.scatter([], [], s=100/2, facecolor=(1, 1, 1, 0.7), edgecolor='black')
marker3 = plt.scatter([], [], s=500/2, facecolor=(1, 1, 1, 0.7), edgecolor='black')
marker4 = plt.scatter([], [], s=1000/2, facecolor=(1, 1, 1, 0.7), edgecolor='black')
marker5 = plt.scatter([], [], s=100, facecolor=(1, 0, 0, 0.7), edgecolor='black')
marker6 = plt.scatter([], [], s=100, facecolor=(0, 0, 1, 0.7), edgecolor='black')
marker7 = plt.scatter([], [], s=100, facecolor=(0, 1, 0, 0.7), edgecolor='black')
legend_markers = [marker1, marker2, marker4, marker5, marker6, marker7]

labels = [
    str(10)+r'$\mu G$',
    str(100)+r'$\mu G$',
    str(1000) + "+"+r'$\mu G$',
    'Away from us',
    'Towards us',
    'Off points'
    ]

legend = plt.legend(handles=legend_markers, labels=labels, scatterpoints=1, ncol=2)

frame = legend.get_frame()
frame.set_facecolor('1')
frame.set_alpha(0.4)
# ---- Style the legend.

# ---- Style the textbox
offPointsText = "RM_Off: {:+.4f} rad/m^2 \nAv_Off: {:+.4f} mag".format(fiducialRM, fiducialExtinction)
props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
ax.text(0.02, 0.98, offPointsText, transform=ax.transAxes, fontsize=10, verticalalignment='top', bbox=props)
# ---- Style the textbox

# ---- Display or save the figure
# plt.show()
plt.savefig(BLOSPointsPlotFile)
plt.close()
# ---- Display or save the figure.
message = 'Saving BLOS figure to ' + BLOSPointsPlotFile
logging.info(message)
print(message)
# -------- CREATE A FIGURE - BLOS POINT MAP. --------
