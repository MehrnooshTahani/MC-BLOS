"""
The zeroth stage of the BLOSMapping method is to define regions of interest.
 - The boundaries and parameters defined here will be used throughout the analysis

"""
import os
from sys import exit
from configparser import ConfigParser
import MolecularClouds.LocalLibraries.config as config

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

        # Pixel limits of the region of interest in the fits file:
        self.xmin = cloudParams['Cloud Info'].getfloat('xmin')
        self.xmax = cloudParams['Cloud Info'].getfloat('xmax')
        self.ymin = cloudParams['Cloud Info'].getfloat('ymin')
        self.ymax = cloudParams['Cloud Info'].getfloat('ymax')

        # Path to the fiducial extinction and electron abundance for the region of interest:
        self.n0 = cloudParams['Cloud Info'].get('n0')
        self.T0 = cloudParams['Cloud Info'].get('T0')
        self.G0 = cloudParams['Cloud Info'].get('G0')  # can be 1 for most clouds unless clouds with many type o and b stars
        Parameters = 'n' + self.n0 + '_T' + self.T0 + '_G' + self.G0
        self.AvFileDir = os.path.join(config.dir_root, config.dir_data, config.dir_chemAbundance, Parameters)
        self.AvFilePath = os.path.join(config.dir_root, config.dir_data, config.dir_chemAbundance, Parameters, 'Av_T0_n0.out')

        # Boundaries of the region of interest:
        self.raHoursMax = cloudParams['Cloud Info'].getfloat('raHoursmax')
        self.raMinsMax = cloudParams['Cloud Info'].getfloat('raMinsMax')
        self.raSecMax = cloudParams['Cloud Info'].getfloat('raSecMax')
        self.raHoursMin = cloudParams['Cloud Info'].getfloat('raHoursMin')
        self.raMinsMin = cloudParams['Cloud Info'].getfloat('raMinsMin')
        self.raSecMin = cloudParams['Cloud Info'].getfloat('raSecMin')
        self.decDegMax = cloudParams['Cloud Info'].getfloat('decDegMax')
        self.decDegMin = cloudParams['Cloud Info'].getfloat('decDegMin')


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
