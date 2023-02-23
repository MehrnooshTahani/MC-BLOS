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
avgExtMultiplier  = configStartSettings['Judgement - Off Points Av Threshold'].getboolean('Multiply with Average Extinction')
onDiskAvGalacticThresh = configStartSettings['Judgement - Off Points Av Threshold'].getfloat('On-Disk Galactic Extinction Threshold')
onDiskAvAntiGalacticThresh = configStartSettings['Judgement - Off Points Av Threshold'].getfloat('On-Disk Anti-Galactic Extinction Threshold')
offDiskAvThresh = configStartSettings['Judgement - Off Points Av Threshold'].getfloat('Off-Disk Extinction Threshold')

nearExtinctionMultiplier = configStartSettings['Judgement - Off Points too Near/Far Cloud'].getint('Near High Extinction Multiplier')
farExtinctionMultiplier = configStartSettings['Judgement - Off Points too Near/Far Cloud'].getint('Far From High Extinction Multiplier')
highExtinctionThreshMultiplier = configStartSettings['Judgement - Off Points too Near/Far Cloud'].getfloat('High Extinction Threshold Multiplier')
useNearExtinctionRemove = configStartSettings['Judgement - Off Points too Near/Far Cloud'].getboolean('Use Near High Extinction Exclusion')
useFarExtinctionRemove = configStartSettings['Judgement - Off Points too Near/Far Cloud'].getboolean('Use Far High Extinction Exclusion')

anomalousSTDNum = configStartSettings['Judgement - Anomalous Off RM Values'].getfloat('Anomalous Values Standard Deviation (Greater Than or Equal To)')
useAnomalousSTDNumRemove = configStartSettings['Judgement - Anomalous Off RM Values'].getboolean('Use Anomalous Value Removal')

UseOptRefPoints = configStartSettings['Judgement - Optimal Reference Points'].getboolean('Find Optimal Reference Points')
minRefPoints = configStartSettings['Judgement - Optimal Reference Points'].getint('Minimum Reference Points to be Selected')
maxFracPointNum = configStartSettings['Judgement - Optimal Reference Points'].getfloat('Max Fraction Reference Points')

useQuadrantEnforce = configStartSettings['Judgement - Cloud Quadrant Sampling'].getboolean('Use Minimum Quadrant Sampling')
minPointsPerQuadrant = configStartSettings['Judgement - Cloud Quadrant Sampling'].getint('Minimum Points Per Quadrant')
weightingScheme = configStartSettings['Judgement - Cloud Quadrant Sampling'].get('Weighting Scheme')

negScaledExtOption = configStartSettings['Judgement - Magnetic Field Calculations'].get("Negative Scaled Extinction Data")

useUncertaintyNans = configStartSettings['Judgement - Uncertainty Calculations'].getboolean("Use Nans in Uncertainty Calculations")

#Plotting Options
textFix = configStartSettings['Plotting Options'].getboolean('Adjust Text Positions')

densityPlotNumPoints = configStartSettings['Plotting Options'].getint('Density Plot Number of Points')
densityPlotMinExtinct = configStartSettings['Plotting Options'].getfloat('Density Plot Minimum Extinction')
densityPlotMaxExtinct = configStartSettings['Plotting Options'].getfloat('Density Plot Maximum Extinction')

tempPlotNumPoints = configStartSettings['Plotting Options'].getint('Temperature Plot Number of Points')
tempPlotMinExtinct = configStartSettings['Plotting Options'].getfloat('Temperature Plot Minimum Extinction')
tempPlotMaxExtinct = configStartSettings['Plotting Options'].getfloat('Temperature Plot Maximum Extinction')

#Data Presentation
dataSeparator = configStartSettings['Data Presentation'].get('Separator')
dataSeparator = bytes(dataSeparator, "utf-8").decode("unicode_escape")
missingDataRep = configStartSettings['Data Presentation'].get('Missing Data')

#Logging Options
logFormat = configStartSettings['Logging'].get('Format')
logSectionDivider = configStartSettings['Logging'].get('Section Divider')
# -------- DEFINE STARTING VARIABLES. --------

# -------- DEFINE DIRECTORIES AND NAMES. --------
configDirectoryAndNames = ConfigParser()
configDirectoryAndNames.read('configDirectoryAndNames.ini')

#Output Directories
dir_root = configDirectoryAndNames['Output Directories'].get('Root')
dir_fileOutput = configDirectoryAndNames['Output Directories'].get('File Output')
dir_plots = configDirectoryAndNames['Output Directories'].get('Plots')
dir_logs = configDirectoryAndNames['Output Directories'].get('Logs')
dir_densitySensitivity = configDirectoryAndNames['Output Directories'].get('Density Sensitivity')
dir_temperatureSensitivity = configDirectoryAndNames['Output Directories'].get('Temperature Sensitivity')
dir_intermediateData = configDirectoryAndNames['Output Directories'].get('Intermediate Data')
dir_finalData = configDirectoryAndNames['Output Directories'].get('Final Data')
#Output Files
file_rmMapping = configDirectoryAndNames['Output Files - Point Matching'].get('RM Map')
file_RMExtinctionMatch = configDirectoryAndNames['Output Files - Point Matching'].get('Matched RM-Extinction')

file_RegionThreshData = configDirectoryAndNames['Output Files - Point Filtering'].get('Region Threshold Data')
file_RMExtinctionNearRej = configDirectoryAndNames['Output Files - Point Filtering'].get('Rejected Near High-Extinction RM-Extinction')
file_RMExtinctionFarRej = configDirectoryAndNames['Output Files - Point Filtering'].get('Rejected Far High-Extinction RM-Extinction')
file_RMExtinctionAnomRej = configDirectoryAndNames['Output Files - Point Filtering'].get('Rejected Anomalous RM-Extinction')
file_RMExtinctionRej = configDirectoryAndNames['Output Files - Point Filtering'].get('Rejected RM-Extinction')
file_RMExtinctionFiltered = configDirectoryAndNames['Output Files - Point Filtering'].get('Filtered RM-Extinction')

file_allPotRefPoints = configDirectoryAndNames['Output Files - Reference Points'].get('All Potential Reference Points')
file_StabilityTrendRefPoints = configDirectoryAndNames['Output Files - Reference Points'].get('Stability Trend Reference Points')
file_QuadDivData = configDirectoryAndNames['Output Files - Reference Points'].get('Quadrant Division Data')
file_OptRefStabPlot = configDirectoryAndNames['Output Files - Reference Points'].get('Optimal Reference Points Stability Plot')
file_SelRefStabPlot = configDirectoryAndNames['Output Files - Reference Points'].get('Chosen Reference Points Stability Plot')
file_QuadRefPlot = configDirectoryAndNames['Output Files - Reference Points'].get('Potential Reference Points Quadrant Plot')
file_selRefPoints = configDirectoryAndNames['Output Files - Reference Points'].get('Selected Reference Points')
file_refData = configDirectoryAndNames['Output Files - Reference Points'].get('Reference Data')

plotName_AllPotRefPtsPlot = configDirectoryAndNames['Output Files - Reference Point Plot Titles'].get('All Potential Reference Points')
plotName_NearHighExtRejPlot = configDirectoryAndNames['Output Files - Reference Point Plot Titles'].get('Near-High Extinction Rejected Points')
plotName_FarHighExtRejPlot = configDirectoryAndNames['Output Files - Reference Point Plot Titles'].get('Far from High Extinction Rejected Points')
plotName_AnomRMPlot = configDirectoryAndNames['Output Files - Reference Point Plot Titles'].get('Anomalous RM Rejected Points')
plotName_AllRejPlot = configDirectoryAndNames['Output Files - Reference Point Plot Titles'].get('All Rejected Points')
plotName_AllRemainPlot = configDirectoryAndNames['Output Files - Reference Point Plot Titles'].get('All Remaining Points')
plotName_AllChosenPlot = configDirectoryAndNames['Output Files - Reference Point Plot Titles'].get('All Chosen Points')
plotName_AllRefAndRejPlot = configDirectoryAndNames['Output Files - Reference Point Plot Titles'].get('All Remaining and Rejected Reference Points')
plotName_QuadDivPlot = configDirectoryAndNames['Output Files - Reference Point Plot Titles'].get('Quadrant Division Plot')
plotName_ExtinctionThresholdPlot = configDirectoryAndNames['Output Files - Reference Point Plot Titles'].get('Extinction Threshold Plot')

file_AllPotRefPtsPlot = configDirectoryAndNames['Output Files - Reference Point Plot File Names'].get('All Potential Reference Points')
file_NearHighExtRejPlot = configDirectoryAndNames['Output Files - Reference Point Plot File Names'].get('Near-High Extinction Rejected Points')
file_FarHighExtRejPlot = configDirectoryAndNames['Output Files - Reference Point Plot File Names'].get('Far from High Extinction Rejected Points')
file_AnomRMPlot = configDirectoryAndNames['Output Files - Reference Point Plot File Names'].get('Anomalous RM Rejected Points')
file_AllRejPlot = configDirectoryAndNames['Output Files - Reference Point Plot File Names'].get('All Rejected Points')
file_AllRemainPlot = configDirectoryAndNames['Output Files - Reference Point Plot File Names'].get('All Remaining Points')
file_AllChosenPlot = configDirectoryAndNames['Output Files - Reference Point Plot File Names'].get('All Chosen Points')
file_AllRefAndRejPlot = configDirectoryAndNames['Output Files - Reference Point Plot File Names'].get('All Remaining and Rejected Reference Points')
file_ExtRefPlot = configDirectoryAndNames['Output Files - Reference Point Plot File Names'].get('Extinction-Reference Points Plot')

file_BLOSDensUncertaintyTemplate = configDirectoryAndNames['Output Files - BLOS Uncertainties'].get('BLOS Density Uncertainty Data')
file_BLOSDensUncertaintyPlot = configDirectoryAndNames['Output Files - BLOS Uncertainties'].get('BLOS Density Uncertainty Plot')
file_BLOSTempUncertaintyTemplate = configDirectoryAndNames['Output Files - BLOS Uncertainties'].get('BLOS Temperature Uncertainty Data')
file_BLOSTempUncertaintyPlot = configDirectoryAndNames['Output Files - BLOS Uncertainties'].get('BLOS Temperature Uncertainty Plot')

file_BLOSPointData = configDirectoryAndNames['Output Files - BLOS Final'].get('BLOS Point Data')
file_BLOSPointFig = configDirectoryAndNames['Output Files - BLOS Final'].get('BLOS Point Figure')
file_BLOSUncertainty = configDirectoryAndNames['Output Files - BLOS Final'].get('BLOS Uncertainties')

file_logscript01 = configDirectoryAndNames['Output Files - Logs'].get('01')
file_logscript02a = configDirectoryAndNames['Output Files - Logs'].get('02a')
file_logscript02b = configDirectoryAndNames['Output Files - Logs'].get('02b')
file_logscript03a = configDirectoryAndNames['Output Files - Logs'].get('03a')
file_logscript03b = configDirectoryAndNames['Output Files - Logs'].get('03b')
file_logscript03c = configDirectoryAndNames['Output Files - Logs'].get('03c')
file_logscript04 = configDirectoryAndNames['Output Files - Logs'].get('04')
file_logscript05a = configDirectoryAndNames['Output Files - Logs'].get('05a')
file_logscript05b = configDirectoryAndNames['Output Files - Logs'].get('05b')
file_logscript06a = configDirectoryAndNames['Output Files - Logs'].get('06a')
file_logscript06b = configDirectoryAndNames['Output Files - Logs'].get('06b')
file_logscript07 = configDirectoryAndNames['Output Files - Logs'].get('07')

#Input Directories
dir_data = configDirectoryAndNames['Input Directories'].get('Input Data')
dir_cloudParameters = configDirectoryAndNames['Input Directories'].get('Cloud Parameter Data')
dir_chemAbundance = configDirectoryAndNames['Input Directories'].get('Chemical Abundance Data')
dir_RMCatalog = configDirectoryAndNames['Input Directories'].get('RM Catalogue Data')

#Input Files
file_RMCatalogue = configDirectoryAndNames['Input Files'].get('RM Catalogue')
template_AvAbundanceData = configDirectoryAndNames['Input Files'].get('AvAbundance Template')
# -------- DEFINE DIRECTORIES AND NAMES. --------

# -------- DEFINE DIRECTORIES/FILE STRUCTURE ALIASES. --------
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
CloudIntermediateDataDir = os.path.join(CloudOutputDir, dir_intermediateData)
CloudFinalDataDir = os.path.join(CloudOutputDir, dir_finalData)

MatchedRMExtinctionFile = os.path.join(CloudFinalDataDir, file_RMExtinctionMatch)
AllPotRefPointFile = os.path.join(CloudFinalDataDir, file_allPotRefPoints)

FilteredRefPointsFile = os.path.join(CloudIntermediateDataDir, file_RMExtinctionFiltered)
ExtinctionCoordDataFile = os.path.join(CloudIntermediateDataDir, file_RegionThreshData)

NearExtinctRefPointFile = os.path.join(CloudIntermediateDataDir, file_RMExtinctionNearRej)
FarExtinctRefPointFile = os.path.join(CloudIntermediateDataDir, file_RMExtinctionFarRej)
AnomRefPointFile = os.path.join(CloudIntermediateDataDir, file_RMExtinctionAnomRej)
RejRefPointFile = os.path.join(CloudIntermediateDataDir, file_RMExtinctionRej)

ChosenRefPointFile = os.path.join(CloudFinalDataDir, file_selRefPoints)
ChosenRefDataFile = os.path.join(CloudFinalDataDir, file_refData)

AllPotRefPtsPlotFile = os.path.join(CloudPlotsDir, file_AllPotRefPtsPlot)
NearHighExtRejPlotFile = os.path.join(CloudPlotsDir, file_NearHighExtRejPlot)
FarHighExtRejPlotFile = os.path.join(CloudPlotsDir, file_FarHighExtRejPlot)
AnomRMPlotFile = os.path.join(CloudPlotsDir, file_AnomRMPlot)
AllRejPlotFile = os.path.join(CloudPlotsDir, file_AllRejPlot)
AllRemainPlotFile = os.path.join(CloudPlotsDir, file_AllRemainPlot)
AllChosenPlotFile = os.path.join(CloudPlotsDir, file_AllChosenPlot)
AllRefAndRejPlotFile = os.path.join(CloudPlotsDir, file_AllRefAndRejPlot)
ExtinctionPlotFile = os.path.join(CloudPlotsDir, file_ExtRefPlot)

StabilityTrendDataTablePath = os.path.join(CloudIntermediateDataDir, file_StabilityTrendRefPoints)
QuadDivDataFile = os.path.join(CloudIntermediateDataDir, file_QuadDivData)

BLOSPointsFile = os.path.join(CloudFinalDataDir, file_BLOSPointData)
BLOSUncertaintyFile = os.path.join(CloudFinalDataDir, file_BLOSUncertainty)

MatchedRMExtinctionPlotFile = os.path.join(CloudPlotsDir, file_rmMapping)
QuadrantDivisionPlotFile = os.path.join(CloudPlotsDir, file_QuadRefPlot)
BLOSvsNRef_AllPlotFile = os.path.join(CloudPlotsDir, file_OptRefStabPlot)
BLOSvsNRef_ChosenPlotFile = os.path.join(CloudPlotsDir, file_SelRefStabPlot)
BLOSPointsPlot = os.path.join(CloudPlotsDir, file_BLOSPointFig)

template_BDensSensName = os.path.join(CloudDensSensDir, file_BLOSDensUncertaintyTemplate)
template_BTempSensName = os.path.join(CloudTempSensDir, file_BLOSTempUncertaintyTemplate)
BDensSensPlot = os.path.join(CloudPlotsDir, file_BLOSDensUncertaintyPlot)
BTempSensPlot = os.path.join(CloudPlotsDir, file_BLOSTempUncertaintyPlot)

Script01File = os.path.join(CloudLogsDir, file_logscript01)
Script02aFile = os.path.join(CloudLogsDir, file_logscript02a)
Script02bFile = os.path.join(CloudLogsDir, file_logscript02b)
Script03aFile = os.path.join(CloudLogsDir, file_logscript03a)
Script03bFile = os.path.join(CloudLogsDir, file_logscript03b)
Script03cFile = os.path.join(CloudLogsDir, file_logscript03c)
Script04File = os.path.join(CloudLogsDir, file_logscript04)
Script05aFile = os.path.join(CloudLogsDir, file_logscript05a)
Script05bFile = os.path.join(CloudLogsDir, file_logscript05b)
Script06aFile = os.path.join(CloudLogsDir, file_logscript06a)
Script06bFile = os.path.join(CloudLogsDir, file_logscript06b)
Script07File = os.path.join(CloudLogsDir, file_logscript07)
# -------- DEFINE DIRECTORIES/FILE STRUCTURE ALIASES. --------

# -------- DEFINE CONSTANTS. --------
configConstants = ConfigParser()
configConstants.read('configConstants.ini')

# Visual extinction to hydrogen column density.
VExtinct_2_Hcol = configConstants['Conversion Factors'].getfloat('Visual Extinction to Hydrogen Column Density')
# Parsec to cm
pcTocm = configConstants['Conversion Factors'].getfloat('Parsecs to Centimeters')
# -------- DEFINE CONSTANTS. --------
