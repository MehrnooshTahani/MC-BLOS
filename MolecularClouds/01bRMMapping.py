"""
This is an optional part of the first stage meant to provide more information only.

This file maps the RMs on the extinction files to get an understanding of the rotation measure coverage
of the region of interest.
"""
import matplotlib.pyplot as plt

from astropy.wcs import WCS
from astropy.io import fits

from LocalLibraries.RMCatalog import RMCatalog
from LocalLibraries.RegionOfInterest import Region
import LocalLibraries.config as config
import LocalLibraries.PlotTemplates as pt
import LocalLibraries.RMPlotLibrary as rmpl
import LocalLibraries.ConversionLibrary as cl

import os
import logging

# -------- CHOOSE THE REGION OF INTEREST --------
cloudName = config.cloud
regionOfInterest = Region(cloudName)
# -------- CHOOSE THE REGION OF INTEREST. --------

# -------- DEFINE FILES AND PATHS --------
RMCatalogPath = os.path.join(config.dir_root, config.dir_data, config.file_RMCatalogue)
saveFigurePath = os.path.join(config.dir_root, config.dir_fileOutput, config.cloud, config.dir_plots, config.prefix_rmMapping + config.cloud + '.png')
# -------- DEFINE FILES AND PATHS. --------

# -------- CONFIGURE LOGGING --------
saveScriptLogPath = os.path.join(config.dir_root, config.dir_fileOutput, cloudName, config.dir_logs, "Script1bLog.txt")
logging.basicConfig(filename=saveScriptLogPath, filemode='w', format=config.logFormat, level=logging.INFO)
# -------- CONFIGURE LOGGING --------

# -------- READ FITS FILE --------
hdulist = fits.open(regionOfInterest.fitsFilePath)
hdu = hdulist[0]
wcs = WCS(hdu.header)
# -------- READ FITS FILE. --------

# -------- READ ROTATION MEASURE FILE --------
# Get all the rm points within the region of interest
rmData = RMCatalog(RMCatalogPath, regionOfInterest.raHoursMax, regionOfInterest.raMinsMax, regionOfInterest.raSecMax,
                   regionOfInterest.raHoursMin, regionOfInterest.raMinsMin, regionOfInterest.raSecMin,
                   regionOfInterest.decDegMax, regionOfInterest.decDegMin)
# -------- READ ROTATION MEASURE FILE. --------

# -------- PREPARE TO PLOT ROTATION MEASURES --------

# ---- Convert Ra and Dec of RMs into pixel values of the fits file
x, y = cl.RADec2xy(rmData.targetRaHourMinSecToDeg, rmData.targetDecDegArcMinSecs, wcs)
# ---- Convert Ra and Dec of RMs into pixel values of the fits file.

# ---- Determine the color and size of the RM points on the plot.
color, size = rmpl.rm2RGB(rmData.targetRotationMeasures)
# ---- Determine the color and size of the RM points on the plot.

# -------- PREPARE TO PLOT ROTATION MEASURES. --------

# -------- CREATE A FIGURE --------

# ---- Generate a basic

#Basic extinction plot given the region of interest and image.
fig, ax = pt.extinctionPlot(hdu, regionOfInterest)

#Plot title
plotTitle = 'Rotation Measure Data' + ' in the ' + cloudName + ' region\n'
plt.title(plotTitle, fontsize=12, y=1.08)

#Plot the RM points on the image.
plt.scatter(x, y, marker='o', s=size, facecolor=color, linewidth=.5, edgecolors='black')

# ---- Style the legend
marker1 = plt.scatter([], [], s=10, facecolor=(1, 1, 1, 0.7), edgecolor='black')
marker2 = plt.scatter([], [], s=50, facecolor=(1, 1, 1, 0.7), edgecolor='black')
marker3 = plt.scatter([], [], s=100, facecolor=(1, 1, 1, 0.7), edgecolor='black')
marker4 = plt.scatter([], [], s=200, facecolor=(1, 1, 1, 0.7), edgecolor='black')
marker5 = plt.scatter([], [], s=100, facecolor=(1, 0, 0, 0.7), edgecolor='black')
marker6 = plt.scatter([], [], s=100, facecolor=(0, 0, 1, 0.7), edgecolor='black')
legend_markers = [marker1, marker2, marker3, marker4, marker5, marker6]

labels = [
    str(10) + ' rad m' + r'$^{-2}$',
    str(50) + ' rad m' + r'$^{-2}$',
    str(100) + ' rad m' + r'$^{-2}$',
    str(200) + ' rad m' + r'$^{-2}$',
    'Negative RM',
    'Positive RM', ]

legend = plt.legend(handles=legend_markers, labels=labels, scatterpoints=1)

frame = legend.get_frame()
frame.set_facecolor('1')
frame.set_alpha(0.4)
# ---- Style the legend.

plt.savefig(saveFigurePath, bbox_inches='tight')
print('Saving RM Matching figure to '+saveFigurePath)
logging.info('Saving RM Matching figure to '+saveFigurePath)
# -------- CREATE A FIGURE. --------
