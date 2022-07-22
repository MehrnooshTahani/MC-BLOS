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
#Output Files
CloudDensSensDir = config.CloudDensSensDir
# -------- DEFINE FILES AND PATHS. --------

# -------- CONFIGURE LOGGING --------
LogFile = config.Script04aFile
logging.basicConfig(filename=LogFile, filemode='w', format=config.logFormat, level=logging.INFO)
# -------- CONFIGURE LOGGING --------

# -------- READ REFERENCE POINT TABLE --------
MatchedRMExtinctTable = pd.read_csv(MatchedRMExtinctFile)
RefPointTable = pd.read_csv(RefPointFile)
RemainingTable = MREF.removeMatchingPoints(MatchedRMExtinctTable, RefPointTable)
RefData = pd.read_csv(ChosenRefDataFile)
fiducialRM, fiducialRMAvgErr, fiducialRMStd, fiducialExtinction = MREF.getRefValFromRefData(RefData)
# -------- READ REFERENCE POINT TABLE. --------

# -------- CALCULATE BLOS AS A FUNCTION OF PERCENT OF THE INPUT DENSITY --------
p = [1, 2.5, 5, 10, 20, 30, 40, 50]  # Percents of the input density

# Calculate BLOS at +/- these percents:
# eg ['-50', '-40', '-30', '-20', '-10', '-5', '-2.5', '-1', '0', '+1', '+2.5', '+5', '+10', '+20', '+30', '+40', '+50']
percent = ['-{}'.format(i) for i in p[::-1]] + ['0'] + ['+{}'.format(i) for i in p]
errPercent = []

for value in percent:
    AvAbundanceName = 'Av_T0_n' + value
    AvAbundancePath = regionOfInterest.AvFileDir + os.sep + AvAbundanceName + '.out'
    saveFilePath = CloudDensSensDir + os.sep + 'B_' + AvAbundanceName + '.txt'
    B = CalculateB(AvAbundancePath, RemainingTable, fiducialRM, fiducialRMAvgErr, fiducialRMStd, fiducialExtinction)
    B.to_csv(saveFilePath, index=False, na_rep='nan')
    if B.isnull().values.any():
        logging.warning("Error! The following percentage change has invalid values: {}".format(value))
        print("Error! The following percentage change has invalid values: {}".format(value))
        errPercent.append(value)

if len(errPercent) > 0:
    logging.info('-------------------------------------------------------------------------------')
    logging.warning('Warning: The following density changes have invalid values.')
    logging.warning('{}'.format(errPercent))
    logging.warning('Please review the results.')
    logging.info('-------------------------------------------------------------------------------')

logging.info('Saving calculated magnetic field values in the folder: ' + CloudDensSensDir)
print('Saving calculated magnetic field values in the folder: ' + CloudDensSensDir)
# -------- CALCULATE BLOS AS A FUNCTION OF PERCENT OF THE INPUT DENSITY. --------
