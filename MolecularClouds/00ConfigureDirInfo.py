import os
import math
from configparser import ConfigParser

'''
This script initializes the default config files and their values.
- Run this script if there are no configuration files present, or you wish to reset those files.
- Do not run this script if there are configuration files present and you wish to keep those values.

The format of the code below is config['config section'] = {
    'key': value,
    'key': value
}
'''

# -------- DEFINE STARTING VARIABLES. --------
configStartSettings = ConfigParser()
configStartSettings['Cloud'] = {
    'Cloud': 'Oriona',
    }
configStartSettings['Judgement'] = {
    'Fill Missing Data': 'Nan',
    'Interpolate Bad Extinction Values': True,
    'Interpolate All': False,
    'Interpolation Method': 'linear',

    'Off Disk Latitude': 15.,
    'On Disk Galactic Extinction Threshold': 2.,
    'On Disk Anti-Galactic Extinction Threshold': 1.5,
    'Off Disk Extinction Threshold': 1.,

    'Near High Extinction Multiplier': 7,
    'Far High Extinction Multiplier': 28,
    'High Extinction Threshold Multiplier': 5,
    'Use Near High Extinction Exclusion': True,
    'Use Far High Extinction Exclusion': True,

    'Anomalous Values Standard Deviation': 3.,
    'Use Anomalous Values Exclusion': True,

    'Use Minimum Stable Points': True,

    'Use Minimum Quadrant Sampling': True,
    'Minimum Points Per Quadrant': 1,

    'Weighting Scheme': 'None'
    }
configStartSettings['Plotting Options'] = {
    'Density Plot Number of Points': 100,
    'Density Plot Minimum Extinction': 0.5,
    'Density Plot Maximum Extinction': 1.5,

    'Temperature Plot Number of Points': 100,
    'Temperature Plot Minimum Extinction': 0.5,
    'Temperature Plot Maximum Extinction': 1.5,
}
configStartSettings['Logging'] = {
    'Format': '%%(name)s - %%(levelname)s - %%(asctime)s - %%(message)s'
}
with open('configStartSettings.ini', 'w') as output_file:
    configStartSettings.write(output_file)
# -------- DEFINE STARTING VARIABLES. --------

# -------- DEFINE DIRECTORIES AND NAMES. --------
configDirectoryAndNames = ConfigParser()

configDirectoryAndNames['Output File Locations'] = {
    'Root': os.path.abspath(os.getcwd()),
    'File Output': 'FileOutput',
    'Plots': 'Plots',
    'Logs': 'Logs',
    'Density Sensitivity': 'DensitySensitivity',
    'Temperature Sensitivity': 'TemperatureSensitivity'
    }

configDirectoryAndNames['Output File Prefixes'] = {
    'RM Mapping': 'RMMapping',

    'RM-Extinction Matching': 'MatchedRMExtinction',
    'RM-Extinction Filtering': 'FilteredRMExtinction',

    'Near High-Extinction Rejected RM-Extinction': 'NearHighExtRej',
    'Far High-Extinction Rejected RM-Extinction': 'FarHighExtRej',
    'Anomalous Rejected RM-Extinction': 'AnomRej',
    'Rejected RM-Extinction': 'Rejected',
    'Remaining RM-Extinction': 'Remaining',

    'All Potential Reference Points': 'AllPotentialRefPoints',
    'Selected Reference Points': 'RefPoints',
    'Reference Data': 'ReferenceData',

    'BLOS Point Data': 'BLOSPoints',
    'BLOS Point Figure': 'BLOSPointMap',
    'BLOS Uncertainties': 'FinalBLOSResults',

    'Optimal Reference Points': 'DataNoRef'
    }

configDirectoryAndNames['Input File Locations'] = {
    'Input Data': 'Data',
    'Cloud Parameter Data': 'CloudParameters',
    'Chemical Abundance Data': 'ChemicalAbundance'
    }

configDirectoryAndNames['Input Files'] = {
    #'RM Catalogue Resolution (Degrees)': 0.0125,
    'RM Catalogue': 'RMCatalogue.txt'
    }

with open('configDirectoryAndNames.ini', 'w') as output_file:
    configDirectoryAndNames.write(output_file)
# -------- DEFINE DIRECTORIES AND NAMES. --------

# -------- DEFINE CONSTANTS. --------
configConstants = ConfigParser()

configConstants['Conversion Factors'] = {
    'Visual Extinction to Hydrogen Column Density': 2.21e21,
    'Parsecs to Centimeters': 3.24078e-19
    }

with open('configConstants.ini', 'w') as output_file:
    configConstants.write(output_file)
# -------- DEFINE CONSTANTS. --------

# -------- DEFINE EXAMPLE REGION. --------
cloudInfoExport = ConfigParser()
cloudInfoExport['Cloud Info'] = {
    'distance': 0,
    'cloudJeansLength': 1,

    'fitsFileName': '',
    'fitsDataType': 'HydrogenColumnDensity',

    'xmin': math.nan,
    'xmax': math.nan,
    'ymin': math.nan,
    'ymax': math.nan,

    'n0': '',
    'T0': '',
    'G0': '',

    'raHoursMax': 0,
    'raMinsMax': 0,
    'raSecMax': 0,
    'raHoursMin': 0,
    'raMinsMin': 0,
    'raSecMin': 0,
    'decDegMax': 0,
    'decDegMin': 0,
}
with open('cloudTemplate.ini', 'w') as output_file:
    cloudInfoExport.write(output_file)
# -------- DEFINE EXAMPLE REGION. --------