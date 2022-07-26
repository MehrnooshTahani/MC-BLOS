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

# -------- CONFIG FILE: STARTING VARIABLES. --------
configStartSettings = ConfigParser()
configStartSettings['Cloud'] = {
    'Cloud': 'Oriona',
    }
configStartSettings['Judgement - Extinction Map'] = {
    'Fill Initial Nan Data': 'Nan',
    'Use Filled Values in RM-Extinction Matching': False,
    'Interpolate Non-Physical (Negative) Extinction': True,
    'Interpolate Area': 'Local',
    'Interpolation Method': 'linear',
}
configStartSettings['Judgement - Off Points Av Threshold'] = {
    'Off-Disk Latitude': 15.,
    'On-Disk Galactic Extinction Threshold': 2.,
    'On-Disk Anti-Galactic Extinction Threshold': 1.5,
    'Off-Disk Extinction Threshold': 1.,
}
configStartSettings['Judgement - Off Points too Near/Far Cloud'] = {
    'Near High Extinction Multiplier': 2,
    'Far From High Extinction Multiplier': 28,
    'High Extinction Threshold Multiplier': 5,
    'Use Near High Extinction Exclusion': True,
    'Use Far High Extinction Exclusion': False,
}
configStartSettings['Judgement - Anomalous Off RM Values'] = {
    'Anomalous Values Standard Deviation (Greater Than or Equal To)': 3.,
    'Use Anomalous Value Removal': True,
}
configStartSettings['Judgement - Optimal Reference Points'] = {
    'Find Optimal Reference Points': True,
    'Minimum Reference Points to be Selected': 3,
    'Max Fraction Reference Points': 0.5,
}
configStartSettings['Judgement - Cloud Quadrant Sampling'] = {
    'Use Minimum Quadrant Sampling': True,
    'Minimum Points Per Quadrant': 1,
    'Weighting Scheme': 'None'
    }
configStartSettings['Judgement - Uncertainty Calculations'] = {
    'Use Nans in Uncertainty Calculations': False
}
configStartSettings['Plotting Options'] = {
    'Adjust Text Positions': True,

    'Density Plot Number of Points': 100,
    'Density Plot Minimum Extinction': 0.5,
    'Density Plot Maximum Extinction': 1.5,

    'Temperature Plot Number of Points': 100,
    'Temperature Plot Minimum Extinction': 0.5,
    'Temperature Plot Maximum Extinction': 1.5,
}
configStartSettings['Data Presentation'] = {
    'Separator': '\\t',
}
configStartSettings['Logging'] = {
    'Format': '%%(name)s - %%(levelname)s - %%(asctime)s - %%(message)s',
    'Section Divider': "====================================================================================================="
}
with open('configStartSettings.ini', 'w') as output_file:
    configStartSettings.write(output_file)
# -------- CONFIG FILE: STARTING VARIABLES. --------

# -------- CONFIG FILE: DIRECTORIES AND NAMES. --------
configDirectoryAndNames = ConfigParser()

configDirectoryAndNames['Output File Locations'] = {
    'Root': os.path.abspath(os.getcwd()),
    'File Output': 'FileOutput',
    'Plots': 'Plots',
    'Logs': 'Logs',
    'Density Sensitivity': 'DensitySensitivity',
    'Temperature Sensitivity': 'TemperatureSensitivity'
    }

configDirectoryAndNames['Output Files'] = {
    'RM Map': 'RMMap.png',

    'Matched RM-Extinction': 'MatchedRMExtinction.csv',
    'Filtered RM-Extinction': 'FilteredRMExtinction.csv',

    'Rejected Near High-Extinction RM-Extinction': 'NearHighExtRej.csv',
    'Rejected Far High-Extinction RM-Extinction': 'FarHighExtRej.csv',
    'Rejected Anomalous RM-Extinction': 'AnomRej.csv',
    'Rejected RM-Extinction': 'Rejected.csv',
    'Remaining RM-Extinction': 'Remaining.csv',

    'All Potential Reference Points': 'AllPotentialRefPoints.csv',
    'Selected Reference Points': 'SelectedRefPoints.csv',
    'Reference Data': 'ReferenceData.csv',

    'BLOS Point Data': 'BLOSPoints.csv',
    'BLOS Point Figure': 'BLOSPointMap.png',
    'BLOS Uncertainties': 'FinalBLOSResults.csv',

    'Optimal Reference Points': 'DataNoRef.csv'
    }

configDirectoryAndNames['Input File Locations'] = {
    'Input Data': 'Data',
    'Cloud Parameter Data': 'CloudParameters',
    'Chemical Abundance Data': 'ChemicalAbundance',
    'RM Catalogue Data': 'RMCatalogue'
    }

configDirectoryAndNames['Input Files'] = {
    #'RM Catalogue Resolution (Degrees)': 0.0125,
    'RM Catalogue': 'catalog.dat'
    }

with open('configDirectoryAndNames.ini', 'w') as output_file:
    configDirectoryAndNames.write(output_file)
# -------- CONFIG FILE: DIRECTORIES AND NAMES. --------

# -------- CONFIG FILE: CONSTANTS. --------
configConstants = ConfigParser()

configConstants['Conversion Factors'] = {
    'Visual Extinction to Hydrogen Column Density': 2.21e21,
    'Parsecs to Centimeters': 3.24078e-19
    }

with open('configConstants.ini', 'w') as output_file:
    configConstants.write(output_file)
# -------- CONFIG FILE: CONSTANTS. --------

# -------- TEMPLATE: EXAMPLE REGION. --------
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
# -------- TEMPLATE: EXAMPLE REGION. --------