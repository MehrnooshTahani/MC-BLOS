"""
This generates interpolated RM values given an initial RM catalogue, useful for testing our code with.
"""

import scipy
import numpy as np
import matplotlib.pyplot as plt

import os
from astropy.io import fits
from astropy.wcs import WCS

import LocalLibraries.PlotTemplates as pt
from LocalLibraries.DataFile import DataFile
from LocalLibraries.RegionOfInterest import Region
import LocalLibraries.config as config
import LocalLibraries.RefJudgeLib as rjl

def interpRMMap(raDeg, decDeg, rmVal, hdu, method = 'cubic', fill = np.nan):
    '''
    Interpolates a map of the rotation measures within a region defined by a fits file.

    :param raDeg: Right ascension in degrees for known RM points. List or 1d array.
    :param decDeg: Declination in degrees for known RM points. List or 1d array.
    :param rmVal: Values of known RM points. List or 1d array.
    :param hdu: HDU specified by a given fits file. Used for coordinate translation and to produce a same size map.
    :param method: Default is set to cubic.
    :param fill: What to fill the region beyond the bound of the interpolated values with.
    :return: gridInterp - A 2d numpy array which contains the interpolated RM values across the gridded region.
        May contain np.nan values, unless fill is specified.
    '''
    wcs = WCS(hdu.header)
    regionHeight = hdu.data.shape[0]
    regionWidth = hdu.data.shape[1]

    points = []
    values = []
    for i in range(0, len(rmVal)):
        pixelRow, pixelColumn = wcs.wcs_world2pix(raDeg[i], decDeg[i], 0)

        #if np.isnan(pixelRow) or np.isnan(pixelColumn): continue #Meh way to handle this.

        pixelRow = int(pixelRow)
        pixelColumn = int(pixelColumn)

        points.append((pixelRow, pixelColumn))
        values.append(rmVal[i])

    y = np.arange(0, regionHeight)
    x = np.arange(0, regionWidth)

    xx, yy = np.meshgrid(x, y)
    griddataInterp = scipy.interpolate.griddata(points, values, (xx, yy), method, fill)
    return griddataInterp

def grid2Value(ra, dec, grid, wcs):
    '''
    Gives the value on a grid corresponding to a given right ascension and declination.

    :param ra: Right asension. numpy array
    :param dec: Declination. numpy array
    :param grid: The 2d grid in question. numpy array
    :param wcs: World coordinate system corresponding to the grid.
    :return: The value of that point on the grid.
    '''
    pixelRow, pixelColumn = wcs.wcs_world2pix(ra, dec, 0)
    pixelRow = pixelRow.astype(int)
    pixelColumn = pixelColumn.astype(int)
    return grid[pixelColumn, pixelRow]

def saveInterpResults(raRange, decRange, rmGenRes, saveFilePath):
    with open(saveFilePath, 'w') as f:
        for i in range(len(raRange)):
            for j in range(len(decRange)):
                raHours, raMins, raSecs = rjl.ra_deg2hms(raRange[i])
                raErrSecs = -1

                decDegs, decArcmins, decArcsecs = rjl.dec_deg2dms(decRange[j])
                decErrArcsecs = -1

                longitudeDegs = -1
                latitudeDegs = -1
                nvssStokesIs = -1
                stokesIErrs = -1
                AvePeakPIs = -1
                PIErrs = -1
                polarizationPercets = -1
                mErrPercents = -1
                rotationMeasures = rmGenRes[i, j]
                RMErrs = -1

                f.write("{} {} {} +/- {} {} {} {} +/- {} {} {} {} +/- {} {} +/- {} {} +/- {} {} +/- {} \n".format( \
                    raHours, raMins, raSecs, raErrSecs, decDegs, decArcmins, decArcsecs, decErrArcsecs, longitudeDegs, \
                    latitudeDegs, nvssStokesIs, stokesIErrs, AvePeakPIs, PIErrs, polarizationPercets, mErrPercents, \
                    rotationMeasures, RMErrs))

# -------- FUNCTION DEFINITION --------
def rm2RGB(rm):
    """
    Takes rotation measure values and assigns them a marker colour and size for use in plotting rotation measure data

    :param rm: The rotation measure, or list of rotation measures
    :return:  A tuple of (colour, size) corresponding to the rotation measure. Note "colour" is a tuple of (RBG,alpha)
    """
    c = []  # Marker colour
    s = []  # Marker size

    for item in rm:
        s.append(min(abs(item), 200000)) #Todo: This is a hard limit on the size so that the general direction and location of all the points can be seen when the results are utterly unreasonable.

        alpha = 1  # Optional: set the transparency
        if int(np.sign(item)) == -1:
            c.append((1, 0, 0, alpha))  # Negative rotation measures assigned red
        elif int(np.sign(item)) == 1:
            c.append((0, 0, 1, alpha))  # Positive rotation measures assigned blue
        elif np.sign(item) == 0:
            c.append((0, 1, 0, alpha))  # Zero-value rotation measures assigned green

    # return the list of RGBA tuples and sizes
    return c, s
# -------- FUNCTION DEFINITION. --------


# -------- CHOOSE THE REGION OF INTEREST --------
cloudName = config.cloud
regionOfInterest = Region(cloudName)
# -------- CHOOSE THE REGION OF INTEREST. --------

# -------- DEFINE FILES AND PATHS --------
RMCatalogPath = os.path.join(config.dir_root, config.dir_data, config.file_RMCatalogue)
saveFilePath = os.path.join(config.dir_root, config.dir_fileOutput, config.cloud, config.prefix_RMExtinctionMatch + config.cloud + '.txt')
# -------- DEFINE FILES AND PATHS. --------

# -------- READ FITS FILE --------
hdulist = fits.open(regionOfInterest.fitsFilePath)

#hdulist = fits.open(os.path.join(config.dir_root, config.dir_data, "test2.fits"))
#hdulist = fits.open(os.path.join(config.dir_root, config.dir_data, "COM_CompMap_IQU-thermaldust-gnilc-unires_2048_R3.00.fits"))
#print(os.path.join(config.dir_root, config.dir_data, "COM_CompMap_IQU-thermaldust-gnilc-unires_2048_R3.00.fits"))
#print(hdulist[0].data.shape)

hdu = hdulist[0]
wcs = WCS(hdu.header)
# -------- READ FITS FILE. --------

# -------- PREPROCESS FITS DATA TYPE. --------
data = rjl.deepCopy(hdu.data)

# If fitsDataType is column density, then convert to visual extinction
if regionOfInterest.fitsDataType == 'HydrogenColumnDensity':
    data = data / config.VExtinct_2_Hcol
# -------- PREPROCESS FITS DATA TYPE. --------

# -------- READ ROTATION MEASURE FILE --------
# Get all the rm points within the region of interest
'''
#Read only region info.
raHrMax = regionOfInterest.raHoursMax
raHrMin = regionOfInterest.raHoursMin
raMinMax = regionOfInterest.raMinsMax
raMinMin = regionOfInterest.raMinsMin
raSecMax = regionOfInterest.raSecMax
raSecMin = regionOfInterest.raSecMin

decDegMax = regionOfInterest.decDegMax
decDegMin = regionOfInterest.decDegMin
                  
#Read everything
raHrMax = 24
raHrMin = 0
raMinMax = 0
raMinMin = 0
raSecMax = 0
raSecMin = 0

decDegMax = 90
decDegMin = -90

#Read Area largely corresponding to the FITS file.
raHrMax, raMinMax, raSecMax = rjl.ra_deg2hms(wcs.wcs_pix2world(0, 0, 0)[0])
raHrMin, raMinMin, raSecMin = rjl.ra_deg2hms(wcs.wcs_pix2world(data.shape[1], 0, 0)[0])

decDegMax = wcs.wcs_pix2world(0, data.shape[0], 0)[1]
decDegMin = wcs.wcs_pix2world(0, 0, 0)[1]

#Read entire area corresponding to fits file, and a bit more. Need robust way to handle points not on the grid.
raHrMax, raMinMax, raSecMax = rjl.ra_deg2hms(max(wcs.wcs_pix2world(0, 0, 0)[0], wcs.wcs_pix2world(0, data.shape[0], 0)[0]))
raHrMin, raMinMin, raSecMin = rjl.ra_deg2hms(min(wcs.wcs_pix2world(data.shape[1], 0, 0)[0], wcs.wcs_pix2world(data.shape[1], data.shape[0], 0)[0]))

decDegMax = max(wcs.wcs_pix2world(0, data.shape[0], 0)[1], wcs.wcs_pix2world(data.shape[1], data.shape[0], 0)[1])
decDegMin = min(wcs.wcs_pix2world(0, 0, 0)[1], wcs.wcs_pix2world(data.shape[1], 0, 0)[1])
'''
print("Reading Catalogue")

raHrMax, raMinMax, raSecMax = rjl.ra_deg2hms(wcs.wcs_pix2world(0, 0, 0)[0])
raHrMin, raMinMin, raSecMin = rjl.ra_deg2hms(wcs.wcs_pix2world(data.shape[1], 0, 0)[0])

decDegMax = wcs.wcs_pix2world(0, data.shape[0], 0)[1]
decDegMin = wcs.wcs_pix2world(0, 0, 0)[1]

rmData = DataFile(RMCatalogPath, raHrMax, raMinMax, raSecMax,
                  raHrMin, raMinMin, raSecMin,
                  decDegMax, decDegMin)

raDeg = rmData.targetRaHourMinSecToDeg
decDeg = rmData.targetDecDegArcMinSecs
rmVal = rmData.targetRotationMeasures
rmErr = rmData.targetRMErrs

#Total number of points read.
print(len(rmVal))
# -------- READ ROTATION MEASURE FILE. --------

# -------- Generate interpolation function. --------

griddataInterp = interpRMMap(raDeg, decDeg, rmVal, hdu)

plt.imshow(griddataInterp, origin='lower', cmap='BrBG', interpolation='nearest')
plt.imshow(data, origin='lower', cmap='BrBG', interpolation='nearest', alpha=0.5)
plt.show()
plt.close()
# -------- Generate interpolation function. --------

# -------- Generate interpolation results. --------
print("Generating Interpolation Results")

raMax = rjl.ra_hms2deg(raHrMax, raMinMax, raSecMax)
raMin = rjl.ra_hms2deg(raHrMin, raMinMin, raSecMin)
raSpaceIntervals = 50
raRange = np.linspace(raMin, raMax, raSpaceIntervals)

decMax = decDegMax
decMin = decDegMin
decSpaceIntervals = 50
decRange = np.linspace(decMin, decMax, decSpaceIntervals)

decGrid, raGrid = np.meshgrid(decRange, raRange)

rmGenRes = grid2Value(raGrid, decGrid, griddataInterp, wcs)
rmGenRes[np.isnan(rmGenRes)] = 0
# -------- Generate interpolation results. --------

# -------- Save interpolation results. --------
print("Saving Interpolation Results")

saveInterpResults(raRange, decRange, rmGenRes, "Data/InterpRMTest.txt")

# -------- Save interpolation results. --------

print("Off to make the graph.")

# -------- PREPARE TO PLOT ROTATION MEASURES --------
# ---- Convert Ra and Dec of RMs into pixel values of the fits file
x = []  # x pixel coordinate of RM
y = []  # y pixel coordinate of RM
color = []
size = []
for i in range(len(raRange)):
    for j in range(len(decRange)):
        pixelRow, pixelColumn = wcs.wcs_world2pix(raRange[i], decRange[j], 0)
        x.append(pixelRow)
        y.append(pixelColumn)
        singleColour, singleSize = rm2RGB([rmGenRes[i, j]])
        color.append(singleColour[0])
        size.append(singleSize[0])

# ---- Convert Ra and Dec of RMs into pixel values of the fits file.

# -------- PREPARE TO PLOT ROTATION MEASURES. --------

# -------- CREATE A FIGURE --------
fig, ax = pt.extinctionPlot(hdu, regionOfInterest)

plt.title('Rotation Measure Data' + ' in the '+cloudName+' region\n', fontsize=12, y=1.08)
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

plt.show()
# -------- CREATE A FIGURE. --------
