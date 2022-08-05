"""
The regions of interest class loads in the data from the regions of interest files as well as derivative data.
 - The boundaries and parameters defined here will be used throughout the analysis
"""
import os
from astropy.io import fits
from astropy.wcs import WCS

from configparser import ConfigParser

from . import ConversionLibrary as cl
from . import config as config
from . import BoxBounds as bb

class Region:
    def __init__(self, regionName):
        # -------- Load the region data file, and raise an error if it doesn't exist. --------
        cloudParams = ConfigParser()
        regionDataFileLoc = os.path.join(config.DataCloudParamsDir, regionName.lower() + '.ini')
        if not os.path.exists(regionDataFileLoc):
            message = "Region data file for given region name: {} not found! Check {} to ensure it exists.".format(regionName, config.DataCloudParamsDir)
            raise NameError(message)
        cloudParams.read(regionDataFileLoc)
        # -------- Load the region data file, and raise an error if it doesn't exist. --------

        # -------- Load Region Data --------
        # Distance to the region of interest:
        self.distance = cloudParams['Cloud Info'].getfloat('distance')  # [pc]
        self.jeanslength = cloudParams['Cloud Info'].getfloat('cloudJeansLength')

        # Path to the fits file containing to the region of interest:
        self.fitsFilePath = os.path.join(config.dir_root, config.dir_data, cloudParams['Cloud Info'].get('fitsFileName'))
        self.fitsDataType = cloudParams['Cloud Info'].get('fitsDataType')

        # Read Fits File
        self.hdulist = fits.open(self.fitsFilePath)
        self.hdu = self.hdulist[0]
        self.wcs = WCS(self.hdu.header)
        #Adjust in case it's hydrogen column density data.
        self.hdu.data = self.hdu.data / config.VExtinct_2_Hcol if self.fitsDataType == 'HydrogenColumnDensity' else self.hdu.data

        # Pixel limits of the region of interest in the fits file:
        xmin = cloudParams['Cloud Info'].getfloat('xmin')
        xmax = cloudParams['Cloud Info'].getfloat('xmax')
        ymin = cloudParams['Cloud Info'].getfloat('ymin')
        ymax = cloudParams['Cloud Info'].getfloat('ymax')
        self.xmin, self.xmax, self.ymin, self.ymax = bb.getBoxBounds(self.hdu.data, xmin, xmax, ymin, ymax) #Utilizing the function to ensure the loaded bounds are valid.

        # Path to the fiducial extinction and electron abundance for the region of interest:
        self.n0 = cloudParams['Cloud Info'].get('n0')
        self.T0 = cloudParams['Cloud Info'].get('T0')
        self.G0 = cloudParams['Cloud Info'].get('G0')  # can be 1 for most clouds unless clouds with many type o and b stars
        Parameters = 'n' + self.n0 + '_T' + self.T0 + '_G' + self.G0
        self.AvFileDir = os.path.join(config.DataChemAbundanceDir, Parameters)
        self.AvFilePath = os.path.join(self.AvFileDir, config.template_AvAbundanceData.format(0, 0))
        # -------- Load Region Data --------

        # -------- Compute Derivative Data --------
        # Ra-Dec Boundaries of the region of interest:
        raMin, raMax, decMin, decMax = cl.getRaDecMinSec(self.xmin, self.xmax, self.ymin, self.ymax, self.wcs)
        self.raHoursMax = raMax.h
        self.raMinsMax = raMax.m
        self.raSecMax = raMax.s
        self.raHoursMin = raMin.h
        self.raMinsMin = raMin.m
        self.raSecMin = raMin.s
        self.decDegMax = decMax
        self.decDegMin = decMin
        # -------- Compute Derivative Data --------