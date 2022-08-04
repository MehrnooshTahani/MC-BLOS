"""
This is the sixth stage the BLOSMapping method where the dependence on temperature is assessed
    - All parameters except for temperature are held constant, and the magnetic field is calculated with electron
    abundances corresponding to a change of +/-  5, 10, and 20 % the fiducial input temperature
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
ChosenRefPointFile = config.ChosenRefPointFile
ChosenRefDataFile = config.ChosenRefDataFile

TempVaryTemplate = config.template_BTempSensName
#Output Files
CloudTempSensDir = config.CloudTempSensDir
# -------- DEFINE FILES AND PATHS. --------

# -------- CONFIGURE LOGGING --------
LogFile = config.Script06aFile
loggingDivider = config.logSectionDivider
logging.basicConfig(filename=LogFile, filemode='w', format=config.logFormat, level=logging.INFO)
# -------- CONFIGURE LOGGING --------

# -------- READ REFERENCE POINT TABLE --------
MatchedRMExtinctTable = pd.read_csv(MatchedRMExtinctFile, sep=config.dataSeparator)
RefPointTable = pd.read_csv(ChosenRefPointFile, sep=config.dataSeparator)
RemainingTable = MREF.rmMatchingPts(MatchedRMExtinctTable, RefPointTable)
RefData = pd.read_csv(ChosenRefDataFile, sep=config.dataSeparator)
fiducialRM, fiducialRMAvgErr, fiducialRMStd, fiducialExtinction = MREF.unpackRefData(RefData)
# -------- READ REFERENCE POINT TABLE. --------

# -------- CALCULATE BLOS AS A FUNCTION OF PERCENT OF THE INPUT TEMPERATURE --------
p = [5, 10, 20]  # Percents of the input temperature

# Calculate BLOS at +/- these percents:
# eg ['-20', '-10', '-5', '0', '+5', '+10', '+20']
percent = ['-{}'.format(i) for i in p[::-1]] + ['0'] + ['+{}'.format(i) for i in p]
errPercent = []

for value in percent:
    # Load the abundance file paths with the appropriate values.
    AvAbundanceFile = config.template_AvAbundanceData.format(value, 0)
    AvAbundancePath = os.path.join(regionOfInterest.AvFileDir, AvAbundanceFile)
    saveFilePath = TempVaryTemplate.format(value)
    # Calculate the magnetic fields given these paths
    B = CalculateB(AvAbundancePath, RemainingTable, fiducialRM, fiducialRMAvgErr, fiducialRMStd, fiducialExtinction, NegativeExtinctionEntriesChange = config.negScaledExtOption)
    B.to_csv(saveFilePath, index=False, na_rep=config.missingDataRep, sep=config.dataSeparator)
    # If there are any missing values in the calculation, warn the user.
    if B.isnull().values.any():
        errPercent.append(value)
        message = "Error! The following percentage change has invalid values: {}".format(value)
        logging.warning(message)
        print(message)
#If there are any missing values in the calculation, warn the user again, in a summary fashion.
if len(errPercent) > 0:
    messages = [loggingDivider,
                'Warning: The following density changes have invalid values.',
                '{}'.format(errPercent),
                'Please review the results.',
                loggingDivider]
    for message in messages:
        logging.warning(message)
        print(message)
#Log results and report to the user.
message = 'Saving calculated magnetic field values in the folder: ' + CloudTempSensDir
logging.info(message)
print(message)
# -------- CALCULATE BLOS AS A FUNCTION OF PERCENT OF THE INPUT TEMPERATURE. --------
