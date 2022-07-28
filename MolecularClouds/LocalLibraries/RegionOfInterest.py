"""
The zeroth stage of the BLOSMapping method is to define regions of interest.
 - The boundaries and parameters defined here will be used throughout the analysis

"""
import os
from astropy.io import fits
from astropy.wcs import WCS
from configparser import ConfigParser
from . import config as config
from . import util as util

class Region:
    def __init__(self, regionName):

        cloudParams = ConfigParser()
        regionDataFileLoc = os.path.join(config.dir_root, config.dir_data, config.dir_cloudParameters, regionName.lower() + '.ini')

        if not os.path.exists(regionDataFileLoc):
            print("The region file has not been found!")
            raise NameError("Region data file for given region name: {} not found! Check Data/CloudParameters to ensure it exists.".format(regionName))

        cloudParams.read(regionDataFileLoc)
        """ Load Region Data """
        # Distance to the region of interest:
        self.distance = cloudParams['Cloud Info'].getfloat('distance')  # CHECK THIS [pc]
        self.jeanslength = cloudParams['Cloud Info'].getfloat('cloudJeansLength')

        # Path to the fits file containing to the region of interest:
        self.fitsFilePath = os.path.join(config.dir_root, config.dir_data, cloudParams['Cloud Info'].get('fitsFileName'))
        self.fitsDataType = cloudParams['Cloud Info'].get('fitsDataType')

        # Read Fits File
        self.hdulist = fits.open(self.fitsFilePath)
        self.hdu = self.hdulist[0]
        self.wcs = WCS(self.hdu.header)

        # Pixel limits of the region of interest in the fits file:
        xmin = cloudParams['Cloud Info'].getfloat('xmin')
        xmax = cloudParams['Cloud Info'].getfloat('xmax')
        ymin = cloudParams['Cloud Info'].getfloat('ymin')
        ymax = cloudParams['Cloud Info'].getfloat('ymax')
        self.xmin, self.xmax, self.ymin, self.ymax = util.getBoxBounds(self.hdu.data, xmin, xmax, ymin, ymax)

        # Path to the fiducial extinction and electron abundance for the region of interest:
        self.n0 = cloudParams['Cloud Info'].get('n0')
        self.T0 = cloudParams['Cloud Info'].get('T0')
        self.G0 = cloudParams['Cloud Info'].get('G0')  # can be 1 for most clouds unless clouds with many type o and b stars
        Parameters = 'n' + self.n0 + '_T' + self.T0 + '_G' + self.G0
        self.AvFileDir = os.path.join(config.dir_root, config.dir_data, config.dir_chemAbundance, Parameters)
        self.AvFilePath = os.path.join(self.AvFileDir, 'Av_T0_n0.out')

        # Boundaries of the region of interest:
        raMin, raMax, decMin, decMax = util.getRaDecMinSec(xmin, xmax, ymin, ymax, self.wcs)
        self.raHoursMax = raMax.h
        self.raMinsMax = raMax.m
        self.raSecMax = raMax.s
        self.raHoursMin = raMin.h
        self.raMinsMin = raMin.m
        self.raSecMin = raMin.s
        self.decDegMax = decMax
        self.decDegMin = decMin
        '''
        self.raHoursMax = cloudParams['Cloud Info'].getfloat('raHoursmax')
        self.raMinsMax = cloudParams['Cloud Info'].getfloat('raMinsMax')
        self.raSecMax = cloudParams['Cloud Info'].getfloat('raSecMax')
        self.raHoursMin = cloudParams['Cloud Info'].getfloat('raHoursMin')
        self.raMinsMin = cloudParams['Cloud Info'].getfloat('raMinsMin')
        self.raSecMin = cloudParams['Cloud Info'].getfloat('raSecMin')
        self.decDegMax = cloudParams['Cloud Info'].getfloat('decDegMax')
        self.decDegMin = cloudParams['Cloud Info'].getfloat('decDegMin')
        '''

'''
TEMPLATE (with defaults)
        elif regionName.lower() == CLOUDNAME:
            # Distance to the region of interest:
            self.distance =  # [pc]
            # Path to the fits file containing to the region of interest:
            self.fitsFilePath = os.path.join(currentDir, '')
            self.fitsDataType = # 'HydrogenColumnDensity' or 'VisualExtinciton'
            # Pixel limits of the region of interest in the fits file:
            self.xmin = 'none'
            self.xmax = 'none'
            self.ymin = 'none'
            self.ymax = 'none'
            # Path to the fiducial extinction and electron abundance for the region of interest:
            self.n0 = ''
            self.T0 = ''
            self.G0 = ''
            Parameters = 'n' + self.n0 + '_T' + self.T0 + '_G' + self.G0
            self.AvFileDir = os.path.join(currentDir, 'Data/ChemicalAbundance/'.replace('/', os.sep) + Parameters + '/'.replace('/', os.sep))
            self.AvFilePath = os.path.join(currentDir, 'Data/ChemicalAbundance/'.replace('/', os.sep) + Parameters + '/Av_T0_n0.out'.replace('/', os.sep))
            # Boundaries of the region of interest:
            self.raHoursMax =
            self.raMinsMax =
            self.raSecMax =
            self.raHoursMin =
            self.raMinsMin =
            self.raSecMin =
            self.decDegMax =
            self.decDegMin =
'''
