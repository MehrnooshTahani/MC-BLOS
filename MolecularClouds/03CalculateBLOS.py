"""
This is the fourth stage of the BLOSMapping method where the BLOS values are calculated using the reference points selected in
the previous stage.  This file also produces a scatter plot of BLOS points.
"""
import os
import pandas as pd
import numpy as np
from astropy.wcs import WCS
from astropy.io import fits
import matplotlib.pyplot as plt
from LocalLibraries.RegionOfInterest import Region
from LocalLibraries.CalculateB import CalculateB
import LocalLibraries.MatchedRMExtinctionFunctions as MREF
import LocalLibraries.config as config
import LocalLibraries.PlotTemplates as pt
import math

import logging

# -------- FUNCTION DEFINITION --------
def B2RGB(b):
    """
    Takes BLOS values and assigns them a marker colour and size for use in plotting BLOS data

    :param b: The BLOS value, or list of BLOS values
    :return:  A tuple of (colour, size) corresponding to the rotation measure. Note "colour" is a tuple of (RBG,alpha)
    """
    c = []  # Marker colour
    s = []  # Marker size

    for item in b:
        if abs(item) < 1000:
            s.append(abs(item) / 2)
        elif abs(item) >= 1000:
            s.append(1000 / 2)

        alpha = 1  # Optional: set the transparency
        if int(np.sign(item)) == -1:
            c.append((1, 0, 0, alpha))  # Negative rotation measures assigned red
        if int(np.sign(item)) == 1:
            c.append((0, 0, 1, alpha))  # Positive rotation measures assigned blue
        if np.sign(item) == 0:
            c.append((0, 1, 0, alpha))  # Zero-value rotation measures assigned green

    # return the list of RGBA tuples and sizes
    return c, s
# -------- FUNCTION DEFINITION. --------

# -------- FUNCTION DEFINITION --------
def B2G(b, alpha = 1):
    """
    Takes BLOS values and assigns them a marker colour and size for use in plotting BLOS data

    :param b: The BLOS value, or list of BLOS values
    :return:  A tuple of (colour, size) corresponding to the rotation measure. Note "colour" is a tuple of (RBG,alpha)
    """
    c = []  # Marker colour
    s = []  # Marker size

    for item in b:
        if abs(item) < 1000:
            s.append(abs(item) / 2)
        elif abs(item) >= 1000:
            s.append(1000 / 2)

    c = [(0, 1, 0, alpha) for i in range(len(b))]

    # return the list of RGBA tuples and sizes
    return c, s
# -------- FUNCTION DEFINITION. --------

# -------- CHOOSE THE REGION OF INTEREST --------
cloudName = config.cloud
regionOfInterest = Region(cloudName)
# -------- CHOOSE THE REGION OF INTEREST. --------

# -------- DEFINE FILES AND PATHS --------
#Input Files
FilePath_ReferencePoints = config.ChosenRefPointFile
FilePath_ReferenceData = config.ChosenRefDataFile
FilePath_MatchedRMExtinc = config.MatchedRMExtinctionFile

#Output Files
saveFilePath_BLOSPoints = config.BLOSPointsFile
saveFigurePath_BLOSPointMap = config.BLOSPointsPlot
saveScriptLogPath = config.Script03File
# -------- DEFINE FILES AND PATHS. --------

# -------- CONFIGURE LOGGING --------
logging.basicConfig(filename=saveScriptLogPath, filemode='w', format=config.logFormat, level=logging.INFO)
# -------- CONFIGURE LOGGING --------

# -------- READ REFERENCE POINT TABLE --------
matchedRMExtincTable = pd.read_csv(FilePath_MatchedRMExtinc)
refPointTable = pd.read_csv(FilePath_ReferencePoints)
remainingTable = MREF.removeMatchingPoints(matchedRMExtincTable, refPointTable)
refData = pd.read_csv(FilePath_ReferenceData)
fiducialRM, fiducialRMAvgErr, fiducialRMStd, fiducialExtinction = MREF.getRefValFromRefData(refData)
# -------- READ REFERENCE POINT TABLE. --------

# -------- READ FITS FILE --------
hdulist = fits.open(regionOfInterest.fitsFilePath)
hdu = hdulist[0]
wcs = WCS(hdu.header)
# -------- READ FITS FILE. --------

# =====================================================================================================================

# -------- CALCULATE BLOS --------
BLOSData = CalculateB(regionOfInterest.AvFilePath, remainingTable, fiducialRM, fiducialRMAvgErr, fiducialRMStd, fiducialExtinction)
BLOSData.to_csv(saveFilePath_BLOSPoints, index=False)
logging.info('Saving calculated magnetic field values to '+saveFilePath_BLOSPoints)
print('Saving calculated magnetic field values to '+saveFilePath_BLOSPoints)
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
ax = fig.add_subplot(111, projection=wcs)

plt.title(r'$\rm{B}_{LOS}$' + ' in the '+cloudName+' region\n\n\n', fontsize=12, linespacing=1)
im = plt.imshow(hdu.data, origin='lower', cmap='BrBG', interpolation='nearest')

# ---- Convert Ra and Dec of points into pixel values of the fits file
x = []  # x pixel coordinate
y = []  # y pixel coordinate
for i in range(len(Ra)):
    pixelRow, pixelColumn = wcs.wcs_world2pix(Ra[i], Dec[i], 0)
    x.append(pixelRow)
    y.append(pixelColumn)
# ---- Convert Ra and Dec of points into pixel values of the fits file.
color, size = B2RGB(BLOS)
plt.scatter(x, y, s=size, facecolor=color, marker='o', linewidth=.5, edgecolors='black')

# ---- Annotate the BLOS Points
pt.labelPoints(ax, n, x, y)
#for i, txt in enumerate(n):
#    ax.annotate(txt, (x[i], y[i]), size=9, color='w')
# ---- Annotate the BLOS Points.

# -------- PREPARE TO PLOT REF BLOS POINTS --------
# ---- CALCULATE REF POINT BLOS.
#Utilized only for the plot which includes the reference points used to find the BLOS
RefBLOSData = CalculateB(regionOfInterest.AvFilePath, refPointTable, fiducialRM, fiducialRMAvgErr, fiducialRMStd, fiducialExtinction, NegativeExtinctionEntriesChange="None")
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
    pixelRow, pixelColumn = wcs.wcs_world2pix(RefRa[i], RefDec[i], 0)
    xRef.append(pixelRow)
    yRef.append(pixelColumn)
# ---- Convert Ra and Dec of points into pixel values of the fits file.
colorRef, sizeRef = B2G(RefBLOS)
plt.scatter(xRef, yRef, s=sizeRef, facecolor=colorRef, marker='o', linewidth=.5, edgecolors='black')

# ---- Annotate the BLOS Points
pt.labelPoints(ax, Refn, xRef, yRef, color = 'magenta')
#for i, txt in enumerate(Refn):
#    ax.annotate(txt, (xRef[i], yRef[i]), size=9, color='w')
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
plt.savefig(saveFigurePath_BLOSPointMap)
plt.close()
# ---- Display or save the figure.
logging.info('Saving BLOS figure to '+saveFigurePath_BLOSPointMap)
print('Saving BLOS figure to '+saveFigurePath_BLOSPointMap)
# -------- CREATE A FIGURE - BLOS POINT MAP. --------