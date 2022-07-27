"""
This is the fifth stage of the BLOSMapping method where the dependence on density is assessed.
    - All parameters except for density are held constant, and the magnetic field is calculated with electron abundances
    corresponding to changes of 0 and +/- 1, 2.5, 5, 10, 20, 20, 40, and 50 % the fiducial input density
"""
from LocalLibraries.CalculateB import CalculateB
import os
from LocalLibraries.RegionOfInterest import Region
import pandas as pd
import LocalLibraries.config as config

import LocalLibraries.MatchedRMExtinctionFunctions as MREF
import logging

# -------- CHOOSE THE REGION OF INTEREST --------
cloudName = config.cloud
regionOfInterest = Region(cloudName)
# -------- CHOOSE THE REGION OF INTEREST. --------

# -------- DEFINE FILES AND PATHS --------
#Input Files
MatchedRMExtinctFile = config.MatchedRMExtinctionFile
RefPointFile = config.ChosenRefPointFile
ChosenRefDataFile = config.ChosenRefDataFile

DensVaryFileTemplate = config.BDensSensFile
#Output Files
CloudDensSensDir = config.CloudDensSensDir
# -------- DEFINE FILES AND PATHS. --------

# -------- CONFIGURE LOGGING --------
LogFile = config.Script05aFile
loggingDivider = config.logSectionDivider
logging.basicConfig(filename=LogFile, filemode='w', format=config.logFormat, level=logging.INFO)
# -------- CONFIGURE LOGGING --------

# -------- READ REFERENCE POINT TABLE --------
MatchedRMExtinctTable = pd.read_csv(MatchedRMExtinctFile, sep=config.dataSeparator)
RefPointTable = pd.read_csv(RefPointFile, sep=config.dataSeparator)
RemainingTable = MREF.removeMatchingPoints(MatchedRMExtinctTable, RefPointTable)
RefData = pd.read_csv(ChosenRefDataFile, sep=config.dataSeparator)
fiducialRM, fiducialRMAvgErr, fiducialRMStd, fiducialExtinction = MREF.getRefValFromRefData(RefData)
# -------- READ REFERENCE POINT TABLE. --------

# -------- CALCULATE BLOS AS A FUNCTION OF PERCENT OF THE INPUT DENSITY --------
p = [1, 2.5, 5, 10, 20, 30, 40, 50]  # Percents of the input density

# Calculate BLOS at +/- these percents:
# eg ['-50', '-40', '-30', '-20', '-10', '-5', '-2.5', '-1', '0', '+1', '+2.5', '+5', '+10', '+20', '+30', '+40', '+50']
percent = ['-{}'.format(i) for i in p[::-1]] + ['0'] + ['+{}'.format(i) for i in p]
errPercent = []

for value in percent:
    AvAbundanceFile = config.template_AvAbundanceData.format(0, value)
    AvAbundancePath = os.path.join(regionOfInterest.AvFileDir, AvAbundanceFile)
    saveFilePath = DensVaryFileTemplate.format(value)
    B = CalculateB(AvAbundancePath, RemainingTable, fiducialRM, fiducialRMAvgErr, fiducialRMStd, fiducialExtinction)
    B.to_csv(saveFilePath, index=False, na_rep='nan', sep=config.dataSeparator)
    if B.isnull().values.any():
        errPercent.append(value)

        message = "Error! The following percentage change has invalid (nan) values: {}".format(value)
        logging.warning(message)
        print(message)

if len(errPercent) > 0:
    messages = [loggingDivider,
                'Warning: The following density changes have invalid values.',
                '{}'.format(errPercent),
                'Please review the results.',
                loggingDivider]
    for message in messages:
        logging.warning(message)
        print(message)

message = 'Saving calculated magnetic field values in the folder: ' + CloudDensSensDir
logging.info(message)
print(message)
# -------- CALCULATE BLOS AS A FUNCTION OF PERCENT OF THE INPUT DENSITY. --------
