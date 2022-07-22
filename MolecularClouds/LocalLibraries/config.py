"""
Loads global variables which are used across all modules.
Adjusted in the Config[Setting].ini.
"""
import os
from configparser import ConfigParser
# -------- DEFINE STARTING VARIABLES. --------
configStartSettings = ConfigParser()
configStartSettings.read('configStartSettings.ini')
#Cloud
cloud = configStartSettings['Cloud'].get('Cloud')

#Judgement
fillMissingExtinct = configStartSettings['Judgement - Extinction Map'].get('Fill Initial Nan Data')
useFillExtinct = configStartSettings['Judgement - Extinction Map'].getboolean('Use Filled Values in RM-Extinction Matching')
doInterpExtinct = configStartSettings['Judgement - Extinction Map'].getboolean('Interpolate Negative Extinction Values')
interpRegion = configStartSettings['Judgement - Extinction Map'].get('Interpolate Area')
interpMethod = configStartSettings['Judgement - Extinction Map'].get('Interpolation Method')

offDiskLatitude = configStartSettings['Judgement - Off Points Av Threshold'].getfloat('Off-Disk Latitude')
onDiskAvGalacticThresh = configStartSettings['Judgement - Off Points Av Threshold'].getfloat('On-Disk Galactic Extinction Threshold')
onDiskAvAntiGalacticThresh = configStartSettings['Judgement - Off Points Av Threshold'].getfloat('On-Disk Anti-Galactic Extinction Threshold')
offDiskAvThresh = configStartSettings['Judgement - Off Points Av Threshold'].getfloat('Off-Disk Extinction Threshold')

nearExtinctionMultiplier = configStartSettings['Judgement - Off Points too Near/Far Cloud'].getint('Near High Extinction Multiplier')
farExtinctionMultiplier = configStartSettings['Judgement - Off Points too Near/Far Cloud'].getint('Far High Extinction Multiplier')
highExtinctionThreshMultiplier = configStartSettings['Judgement - Off Points too Near/Far Cloud'].getfloat('High Extinction Threshold Multiplier')
useNearExtinctionRemove = configStartSettings['Judgement - Off Points too Near/Far Cloud'].getboolean('Use Near High Extinction Exclusion')
useFarExtinctionRemove = configStartSettings['Judgement - Off Points too Near/Far Cloud'].getboolean('Use Far High Extinction Exclusion')

anomalousSTDNum = configStartSettings['Judgement - Anomalous Off RM Values'].getfloat('Anomalous Values Standard Deviation')
useAnomalousSTDNumRemove = configStartSettings['Judgement - Anomalous Off RM Values'].getboolean('Use Anomalous Values Exclusion')

UseOptRefPts = configStartSettings['Judgement - Optimal Reference Points'].getboolean('Find Optimal Reference Points')
minRefPts = configStartSettings['Judgement - Optimal Reference Points'].getint('Minimum Reference Points to be Selected')
maxFracPointNum = configStartSettings['Judgement - Optimal Reference Points'].getfloat('Max Fraction Reference Points')

useQuadrantEnforce = configStartSettings['Judgement - Cloud Quadrant Sampling'].getboolean('Use Minimum Quadrant Sampling')
minPointsPerQuadrant = configStartSettings['Judgement - Cloud Quadrant Sampling'].getint('Minimum Points Per Quadrant')
weightingScheme = configStartSettings['Judgement - Cloud Quadrant Sampling'].get('Weighting Scheme')

useUncertaintyNans = configStartSettings['Judgement - Uncertainty Calculations'].getboolean("Use Nans in Uncertainty Calculations")

#Plotting Options
textFix = configStartSettings['Plotting Options'].getboolean('Adjust Text Positions')

densityPlotNumPoints = configStartSettings['Plotting Options'].getint('Density Plot Number of Points')
densityPlotMinExtinct = configStartSettings['Plotting Options'].getfloat('Density Plot Minimum Extinction')
densityPlotMaxExtinct = configStartSettings['Plotting Options'].getfloat('Density Plot Maximum Extinction')

tempPlotNumPoints = configStartSettings['Plotting Options'].getint('Temperature Plot Number of Points')
tempPlotMinExtinct = configStartSettings['Plotting Options'].getfloat('Temperature Plot Minimum Extinction')
tempPlotMaxExtinct = configStartSettings['Plotting Options'].getfloat('Temperature Plot Maximum Extinction')

#Logging Options
logFormat = configStartSettings['Logging'].get('Format')
logSectionDivider = configStartSettings['Logging'].get('Section Divider')
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
#Output Files
file_rmMapping = configDirectoryAndNames['Output Files'].get('RM Mapping')
file_RMExtinctionMatch = configDirectoryAndNames['Output Files'].get('RM-Extinction Matching')
file_RMExtinctionFiltered = configDirectoryAndNames['Output Files'].get('RM-Extinction Filtering')

file_RMExtinctionNearRej = configDirectoryAndNames['Output Files'].get('Near High-Extinction Rejected RM-Extinction')
file_RMExtinctionFarRej = configDirectoryAndNames['Output Files'].get('Far High-Extinction Rejected RM-Extinction')
file_RMExtinctionAnomRej = configDirectoryAndNames['Output Files'].get('Anomalous Rejected RM-Extinction')
file_RMExtinctionRej = configDirectoryAndNames['Output Files'].get('Rejected RM-Extinction')
file_RMExtinctionRemaining = configDirectoryAndNames['Output Files'].get('Remaining RM-Extinction')

file_allPotRefPoints = configDirectoryAndNames['Output Files'].get('All Potential Reference Points')
file_selRefPoints = configDirectoryAndNames['Output Files'].get('Selected Reference Points')
file_refData = configDirectoryAndNames['Output Files'].get('Reference Data')

file_BLOSPointData = configDirectoryAndNames['Output Files'].get('BLOS Point Data')
file_BLOSPointFig = configDirectoryAndNames['Output Files'].get('BLOS Point Figure')
file_BLOSUncertainty = configDirectoryAndNames['Output Files'].get('BLOS Uncertainties')
file_OptRefPoints = configDirectoryAndNames['Output Files'].get('Optimal Reference Points')
#Input Directories
dir_data = configDirectoryAndNames['Input File Locations'].get('Input Data')
dir_cloudParameters = configDirectoryAndNames['Input File Locations'].get('Cloud Parameter Data')
dir_chemAbundance = configDirectoryAndNames['Input File Locations'].get('Chemical Abundance Data')
dir_RMCatalog = configDirectoryAndNames['Input File Locations'].get('RM Catalogue Data')
#Input Files
#resolution_RMCatalogue = configDirectoryAndNames['Input Files'].getfloat('RM Catalogue Resolution (Degrees)')
file_RMCatalogue = configDirectoryAndNames['Input Files'].get('RM Catalogue')
# -------- DEFINE DIRECTORIES AND NAMES. --------

# -------- DEFINE DIRECTORIES/FILE STRUCTURE. --------
#Base Folders
DataDir = os.path.join(dir_root, dir_data)
FileOutputDir = os.path.join(dir_root, dir_fileOutput)
#Input
DataChemAbundanceDir = os.path.join(DataDir, dir_chemAbundance)
DataCloudParamsDir = os.path.join(DataDir, dir_cloudParameters)
DataRMCatalogDir = os.path.join(DataDir, dir_RMCatalog)

DataRMCatalogFile = os.path.join(DataRMCatalogDir, file_RMCatalogue)
#Output
CloudOutputDir = os.path.join(FileOutputDir, cloud)

CloudDensSensDir = os.path.join(CloudOutputDir, dir_densitySensitivity)
CloudLogsDir = os.path.join(CloudOutputDir, dir_logs)
CloudPlotsDir = os.path.join(CloudOutputDir, dir_plots)
CloudTempSensDir = os.path.join(CloudOutputDir, dir_temperatureSensitivity)

MatchedRMExtinctionFile = os.path.join(CloudOutputDir, file_RMExtinctionMatch)
FilteredRMExtinctionFile = os.path.join(CloudOutputDir, file_RMExtinctionFiltered)

AllPotRefPointFile = os.path.join(CloudOutputDir, file_allPotRefPoints)

NearExtinctRefPointFile = os.path.join(CloudOutputDir, file_RMExtinctionNearRej)
FarExtinctRefPointFile = os.path.join(CloudOutputDir, file_RMExtinctionFarRej)
AnomRefPointFile = os.path.join(CloudOutputDir, file_RMExtinctionAnomRej)
RejRefPointFile = os.path.join(CloudOutputDir, file_RMExtinctionRej)
RemainingRefPointFile = os.path.join(CloudOutputDir, file_RMExtinctionRemaining)

ChosenRefPointFile = os.path.join(CloudOutputDir, file_selRefPoints)
ChosenRefDataFile = os.path.join(CloudOutputDir, file_refData)

DataNoRefFile = os.path.join(CloudOutputDir, file_OptRefPoints)

BLOSPointsFile = os.path.join(CloudOutputDir, file_BLOSPointData)
BLOSUncertaintyFile = os.path.join(CloudOutputDir, file_BLOSUncertainty)

DensBT0n0File = os.path.join(CloudDensSensDir, 'B_Av_T0_n0.txt')

TempBT0n0File = os.path.join(CloudTempSensDir, 'B_Av_T0_n0.txt')

MatchedRMExtinctionPlotFile = os.path.join(CloudPlotsDir, file_rmMapping)
QuadrantDivisionPlotFile = os.path.join(CloudPlotsDir, 'QuadrantDivision.png')
BLOSvsNRef_AllPlotFile = os.path.join(CloudPlotsDir, 'BLOS_vs_NRef_AllPotentialRefPoints.png')
BLOSvsNRef_ChosenPlotFile = os.path.join(CloudPlotsDir, 'BLOS_vs_NRef_ChosenRefPoints.png')
BLOSPointsPlot = os.path.join(CloudPlotsDir, file_BLOSPointFig)
BDensSensPlot = os.path.join(CloudPlotsDir, 'BDensitySensitivity.png')
BTempSensPlot = os.path.join(CloudPlotsDir, 'BTemperatureSensitivity.png')

Script00File = os.path.join(CloudLogsDir, "00.txt")
Script01aFile = os.path.join(CloudLogsDir, "01a.txt")
Script01bFile = os.path.join(CloudLogsDir, "01b.txt")
Script02aFile = os.path.join(CloudLogsDir, "02a.txt")
Script02bFile = os.path.join(CloudLogsDir, "02b.txt")
Script02cFile = os.path.join(CloudLogsDir, "02c.txt")
Script03File = os.path.join(CloudLogsDir, "03.txt")
Script04aFile = os.path.join(CloudLogsDir, "04a.txt")
Script04bFile = os.path.join(CloudLogsDir, "04b.txt")
Script05aFile = os.path.join(CloudLogsDir, "05a.txt")
Script05bFile = os.path.join(CloudLogsDir, "05b.txt")
Script06File = os.path.join(CloudLogsDir, "06.txt")
# -------- DEFINE DIRECTORIES/FILE STRUCTURE. --------

# -------- DEFINE CONSTANTS. --------
configConstants = ConfigParser()
configConstants.read('configConstants.ini')

# Visual extinction to hydrogen column density.
VExtinct_2_Hcol = configConstants['Conversion Factors'].getfloat('Visual Extinction to Hydrogen Column Density')
# Parsec to cm
pcTocm = configConstants['Conversion Factors'].getfloat('Parsecs to Centimeters')
# -------- DEFINE CONSTANTS. --------
