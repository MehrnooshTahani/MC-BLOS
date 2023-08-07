import os
import math
from configparser import ConfigParser

'''
This script initializes the default config files and their values.
- Run this script if there are no configuration files present, or you wish to reset those files.
- Do not run this script if there are configuration files present and you wish to keep those values.

The format of the code below is config['config section'] = {
    '# = Comment': '',
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
    '# = Fill Initial Nan Data: What to interpret missing values in the extinction map as. Valid values include Zero, Average, Inf, Interpolate, Nan': '',
    'Fill Initial Nan Data': 'Nan',
    'Use Filled Values in RM-Extinction Matching': False,
    'Interpolate Non-Physical (Negative) Extinction': True,

    '# = Interpolate Area: What areas of the extinction map to interpolate. Valid values include Local, All. Local only interpolates a matched point with nan values and its surroundings, whilst All interpolates the entire map for all of its nan values. Warning: All can be very costly!': '',
    'Interpolate Area': 'Local',
    '# = Interpolation Method: How the interpolation should be done. Valid values include nearest, linear, cubic': '',
    'Interpolation Method': 'linear',
}
configStartSettings['Judgement - Off Points Av Threshold'] = {
    'Off-Disk Latitude': 15.,
    '# = Multiply with Average Extinction: Whether the following thresholds should be seen as absolute, or as multiples of the average extinction in the fits file. True or False.': '',
    'Multiply with Average Extinction': False,
    'On-Disk Galactic Extinction Threshold': 1.75,
    'On-Disk Anti-Galactic Extinction Threshold': 1.5,
    'Off-Disk Extinction Threshold': 1.0,
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
    'Max Fraction Reference Points': 1,
}
configStartSettings['Judgement - Cloud Quadrant Sampling'] = {
    'Use Minimum Quadrant Sampling': True,
    'Minimum Points Per Quadrant': 1,
    '# = Weighting Scheme: How the RMoff values should be weighted. Valid values include None, Quadrant': '',
    'Weighting Scheme': 'None'
    }
configStartSettings['Judgement - On Point Extinction Multiple of Off Point Average Multiplier'] = {
    'On Point Extinction Multiple of Off Point Average Multiplier': 1.0
}
configStartSettings['Judgement - Magnetic Field Calculations'] = {
    '# = Negative Scaled Extinction Data: What to do with non-physical negative scaled extinction points in calculating magnetic fields. Valid values include Delete, Zero, None': 'Delete',
    'Negative Scaled Extinction Data': 'Delete'
}
configStartSettings['Judgement - Uncertainty Calculations'] = {
    'Use Nans in Uncertainty Calculations': False
}

configStartSettings['Judgement - User Judgement'] = {
    'Use Manual User Selection of Reference Points': False
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
    '# = What to separate data with. In a csv this is usually \',\'.': '',
    'Separator': '\\t',
    '# = What to represent missing data with. Usually nan or nothing at all': '',
    'Missing Data': 'nan'
}
configStartSettings['Logging'] = {
    '# = Format: How each line of log info should be prefixed. See https://docs.python.org/3/library/logging.html#formatter-objects for more details.': '',
    'Format': '%%(name)s - %%(levelname)s - %%(asctime)s - %%(message)s',
    '# = Section Divider: The line that divides logging information within a script. ': '',
    'Section Divider': "====================================================================================================="
}
with open('configStartSettings.ini', 'w') as output_file:
    configStartSettings.write(output_file)
# -------- CONFIG FILE: STARTING VARIABLES. --------

# -------- CONFIG FILE: DIRECTORIES AND NAMES. --------
configDirectoryAndNames = ConfigParser()

configDirectoryAndNames['Output Directories'] = {
    'Root': os.path.abspath(os.getcwd()),
    'File Output': 'FileOutput',
    'Plots': 'Plots',
    'Logs': 'Logs',
    'Density Sensitivity': 'DensitySensitivity',
    'Temperature Sensitivity': 'TemperatureSensitivity',
    'Intermediate Data': 'IntermediateData',
    'Final Data': 'FinalData'
}
configDirectoryAndNames['Output Files - Point Matching'] = {
    'RM Map': 'RMMap.png',
    'Matched RM-Extinction': 'MatchedRMExtinction.csv'
}
configDirectoryAndNames['Output Files - Point Filtering'] = {
    'Region Threshold Data': 'RegionThresholdData.csv',
    'Rejected Near High-Extinction RM-Extinction': 'NearHighExtRej.csv',
    'Rejected Far High-Extinction RM-Extinction': 'FarHighExtRej.csv',
    'Rejected Anomalous RM-Extinction': 'AnomRej.csv',
    'Rejected RM-Extinction': 'Rejected.csv',
    'Filtered RM-Extinction': 'FilteredPotRefPoints.csv',
}
configDirectoryAndNames['Output Files - Reference Points'] = {
    'All Potential Reference Points': 'AllPotentialRefPoints.csv',
    'Selected Reference Points': 'SelectedRefPoints.csv',
    'Quadrant Division Data': 'QuadrantDivisionData.csv',
    'Stability Trend Reference Points': 'TrendDataTable.csv',
    'Optimal Reference Points Stability Plot': 'BLOS_vs_NRef_AllPotentialRefPoints.png',
    'Chosen Reference Points Stability Plot': 'BLOS_vs_NRef_ChosenRefPoints.png',
    'Potential Reference Points Quadrant Plot': 'QuadrantDivisionPlot.png',
    'Reference Data': 'ReferenceData.csv'
}
configDirectoryAndNames['Output Files - Reference Point Plot Titles'] = {
    'All Matched RM-Extinction Points': 'All RM Points in the Region with ID',
    'All Potential Reference Points': 'All Potential Reference Points',
    'Near-High Extinction Rejected Points': 'Near-High Extinction Rejected Points',
    'Far from High Extinction Rejected Points': 'Far from High Extinction Rejected Points',
    'Anomalous RM Rejected Points': 'Anomalous RM Rejected Points',
    'All Rejected Points': 'All Rejected Points',
    'All Remaining Points': 'All Remaining Points',
    'All Chosen Points': 'All Chosen Points',
    'All Remaining and Rejected Reference Points': 'All Remaining and Rejected Reference',
    'Quadrant Division Plot': 'Quadrant Division Plot',
    'Extinction Threshold Plot': 'Extinction Threshold Plot'
}
configDirectoryAndNames['Output Files - Reference Point Plot File Names'] = {
    'All Matched RM-Extinction Points': 'AllRMPtsInRegion.png',
    'All Potential Reference Points': 'AllPotRefPts.png',
    'Near-High Extinction Rejected Points': 'Filter_NearHighExt.png',
    'Far from High Extinction Rejected Points': 'Filter_FarHighExt.png',
    'Anomalous RM Rejected Points': 'Filter_AnomRM.png',
    'All Rejected Points': 'Filter_AllRej.png',
    'All Remaining Points': 'Filter_AllRemaining.png',
    'All Chosen Points': 'ChosenRefPoints.png',
    'All Remaining and Rejected Reference Points': 'AllPotRefPointCategorized.png',
    'Extinction-Reference Points Plot': 'ExtRefPts.png'
}
configDirectoryAndNames['Output Files - BLOS Uncertainties'] = {
    'BLOS Density Uncertainty Data': 'B_Av_T0_n{}.csv',
    'BLOS Density Uncertainty Plot': 'BDensitySensitivity.png',

    'BLOS Temperature Uncertainty Data': 'B_Av_T{}_n0.csv',
    'BLOS Temperature Uncertainty Plot': 'BTemperatureSensitivity.png'
}
configDirectoryAndNames['Output Files - BLOS Final'] = {
    'BLOS Point Data': 'BLOSPoints.csv',
    'BLOS Point Figure': 'BLOSPointMap.png',
    'BLOS Uncertainties': 'FinalBLOSResults.csv',
}
configDirectoryAndNames['Output Files - Logs'] = {
    '01': '01.txt',
    '02a': '02a.txt',
    '02b': '02b.txt',
    '03a': '03a.txt',
    '03b': '03b.txt',
    '03c': '03c.txt',
    '04': '04.txt',
    '05a': '05a.txt',
    '05b': '05b.txt',
    '06a': '06a.txt',
    '06b': '06b.txt',
    '07': '07.txt',
}
configDirectoryAndNames['Input Directories'] = {
    'Input Data': 'Data',
    'Cloud Parameter Data': 'CloudParameters',
    'Chemical Abundance Data': 'ChemicalAbundance',
    'RM Catalogue Data': 'RMCatalog'
}
configDirectoryAndNames['Input Files'] = {
    #'RM Catalogue Resolution (Degrees)': 0.0125,
    '# = RM Catalogue: The name of the rotation measure catalog, formatted in TAYLOR style currently. Valid default catalogs: catalog.dat, Cameron.dat. Cameron catalog is converted to Taylor and is not rigorously tested, please verify before using.': '',
    'RM Catalogue': 'catalog.dat',
    'AvAbundance Template': 'Av_T{}_n{}.out'
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
    '# = Physical line-of-sight distances in parsec': '',
    'distance': 0,
    'cloudJeansLength': 1,

    '# = Name of the fits file with the map corresponding to the region': '',
    'fitsFileName': '',
    'fitsDataType': 'HydrogenColumnDensity',

    '# = Pixels in the fits file corresponding to the region': '',
    'xmin': math.nan,
    'xmax': math.nan,
    'ymin': math.nan,
    'ymax': math.nan,

    '# = Chemical code parameters for the cloud': '',
    'n0': '',
    'T0': '',
    'G0': ''
}
with open('Data\\CloudParameters\\0- cloudTemplate.ini', 'w') as output_file:
    cloudInfoExport.write(output_file)
# -------- TEMPLATE: EXAMPLE REGION. --------