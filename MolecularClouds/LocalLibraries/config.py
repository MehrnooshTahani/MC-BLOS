"""
In this file global variables which are used across all modules are defined.
They are adjusted in the Config[Setting].ini accordingly
"""
from configparser import ConfigParser
# -------- DEFINE STARTING VARIABLES. --------
configStartSettings = ConfigParser()
configStartSettings.read('configStartSettings.ini')
cloud = configStartSettings['Cloud'].get('Cloud')

doInterpExtinct = configStartSettings['Judgement'].getboolean('Interpolate Bad Extinction Values')

offDiskLatitude = configStartSettings['Judgement'].getfloat('Off Disk Latitude')
onDiskAvGalacticThresh = configStartSettings['Judgement'].getfloat('On Disk Galactic Extinction Threshold')
onDiskAvAntiGalacticThresh = configStartSettings['Judgement'].getfloat('On Disk Anti-Galactic Extinction Threshold')
offDiskAvThresh = configStartSettings['Judgement'].getfloat('Off Disk Extinction Threshold')

nearExtinctionMultiplier = configStartSettings['Judgement'].getint('Near High Extinction Multiplier')
farExtinctionMultiplier = configStartSettings['Judgement'].getint('Far High Extinction Multiplier')
highExtinctionThreshMultiplier = configStartSettings['Judgement'].getfloat('High Extinction Threshold Multiplier')
useNearExtinctionRemove = configStartSettings['Judgement'].getboolean('Use Near High Extinction Exclusion')
useFarExtinctionRemove = configStartSettings['Judgement'].getboolean('Use Far High Extinction Exclusion')

anomalousSTDNum = configStartSettings['Judgement'].getfloat('Anomalous Values Standard Deviation')
useAnomalousSTDNumRemove = configStartSettings['Judgement'].getboolean('Use Anomalous Values Exclusion')

useStableMinimum = configStartSettings['Judgement'].getboolean('Use Minimum Stable Points')
useQuadrantEnforce = configStartSettings['Judgement'].getboolean('Use Minimum Quadrant Sampling')
minPointsPerQuadrant = configStartSettings['Judgement'].getint('Minimum Points Per Quadrant')

weightingScheme = configStartSettings['Judgement'].get('Weighting Scheme')


densityPlotNumPoints = configStartSettings['Plotting Options'].getint('Density Plot Number of Points')
densityPlotMinExtinct = configStartSettings['Plotting Options'].getfloat('Density Plot Minimum Extinction')
densityPlotMaxExtinct = configStartSettings['Plotting Options'].getfloat('Density Plot Maximum Extinction')

tempPlotNumPoints = configStartSettings['Plotting Options'].getint('Temperature Plot Number of Points')
tempPlotMinExtinct = configStartSettings['Plotting Options'].getfloat('Temperature Plot Minimum Extinction')
tempPlotMaxExtinct = configStartSettings['Plotting Options'].getfloat('Temperature Plot Maximum Extinction')

logFormat = configStartSettings['Logging'].get('Format')
# -------- DEFINE STARTING VARIABLES. --------

# -------- DEFINE DIRECTORIES AND NAMES. --------
configDirectoryAndNames = ConfigParser()
configDirectoryAndNames.read('configDirectoryAndNames.ini')

#Output Directories
dir_root = configDirectoryAndNames['Output File Locations'].get('Root')
dir_fileOutput = configDirectoryAndNames['Output File Locations'].get('File Output')
dir_plots = configDirectoryAndNames['Output File Locations'].get('Plots')
dir_logs = configDirectoryAndNames['Output File Locations'].get('Logs')
dir_densitySensitivity = configDirectoryAndNames['Output File Locations'].get('Density Sensitivity')
dir_temperatureSensitivity = configDirectoryAndNames['Output File Locations'].get('Temperature Sensitivity')
#Output Name Prefixes
prefix_rmMapping = configDirectoryAndNames['Output File Prefixes'].get('RM Mapping')
prefix_RMExtinctionMatch = configDirectoryAndNames['Output File Prefixes'].get('RM-Extinction Matching')
prefix_allPotRefPoints = configDirectoryAndNames['Output File Prefixes'].get('All Potential Reference Points')
prefix_selRefPoints = configDirectoryAndNames['Output File Prefixes'].get('Selected Reference Points')
prefix_refData = configDirectoryAndNames['Output File Prefixes'].get('Reference Data')
prefix_BLOSPointData = configDirectoryAndNames['Output File Prefixes'].get('BLOS Point Data')
prefix_BLOSPointFig = configDirectoryAndNames['Output File Prefixes'].get('BLOS Point Figure')
prefix_BLOSUncertainty = configDirectoryAndNames['Output File Prefixes'].get('BLOS Uncertainties')
prefix_OptRefPoints = configDirectoryAndNames['Output File Prefixes'].get('Optimal Reference Points')
#Input Directories
dir_data = configDirectoryAndNames['Input File Locations'].get('Input Data')
dir_cloudParameters = configDirectoryAndNames['Input File Locations'].get('Cloud Parameter Data')
dir_chemAbundance = configDirectoryAndNames['Input File Locations'].get('Chemical Abundance Data')
#Input File Names
#resolution_RMCatalogue = configDirectoryAndNames['Input Files'].getfloat('RM Catalogue Resolution (Degrees)')
file_RMCatalogue = configDirectoryAndNames['Input Files'].get('RM Catalogue')
# -------- DEFINE DIRECTORIES AND NAMES. --------

# -------- DEFINE CONSTANTS. --------
configConstants = ConfigParser()
configConstants.read('configConstants.ini')

# Visual extinction to hydrogen column density.
VExtinct_2_Hcol = configConstants['Conversion Factors'].getfloat('Visual Extinction to Hydrogen Column Density')
# Parsec to cm
pcTocm = configConstants['Conversion Factors'].getfloat('Parsecs to Centimeters')
# -------- DEFINE CONSTANTS. --------
