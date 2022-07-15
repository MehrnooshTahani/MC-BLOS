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
#Output Files
CloudTempSensDir = config.CloudTempSensDir
# -------- DEFINE FILES AND PATHS. --------

# -------- CONFIGURE LOGGING --------
LogFile = config.Script05aFile
logging.basicConfig(filename=LogFile, filemode='w', format=config.logFormat, level=logging.INFO)
# -------- CONFIGURE LOGGING --------

# -------- READ REFERENCE POINT TABLE --------
MatchedRMExtinctTable = pd.read_csv(MatchedRMExtinctFile)
RefPointTable = pd.read_csv(ChosenRefPointFile)
RemainingTable = MREF.removeMatchingPoints(MatchedRMExtinctTable, RefPointTable)
RefData = pd.read_csv(ChosenRefDataFile)
fiducialRM, fiducialRMAvgErr, fiducialRMStd, fiducialExtinction = MREF.getRefValFromRefData(RefData)
# -------- READ REFERENCE POINT TABLE. --------

# -------- CALCULATE BLOS AS A FUNCTION OF PERCENT OF THE INPUT TEMPERATURE --------
p = [5, 10, 20]  # Percents of the input temperature

# Calculate BLOS at +/- these percents:
# eg ['-20', '-10', '-5', '0', '+5', '+10', '+20']
percent = ['-{}'.format(i) for i in p[::-1]] + ['0'] + ['+{}'.format(i) for i in p]
errPercent = []

for value in percent:
    AvAbundanceName = 'Av_T' + value + '_n0'
    AvAbundancePath = regionOfInterest.AvFileDir + os.sep + AvAbundanceName + '.out'
    saveFilePath = CloudTempSensDir + os.sep + 'B_' + AvAbundanceName + '.txt'
    try:
        B = CalculateB(AvAbundancePath, RemainingTable, fiducialRM, fiducialRMAvgErr, fiducialRMStd, fiducialExtinction)
        B.to_csv(saveFilePath, index=False)
    except:
        logging.warning("Error! The following percentage change could not be calculated: {}".format(value))
        print("Error! The following percentage change could not be calculated: {}".format(value))
        errPercent.append(value)

if len(errPercent) > 0:
    logging.info('-------------------------------------------------------------------------------')
    logging.warning('Warning: The following density changes have not been calculated due to an error.')
    logging.warning('{}'.format(errPercent))
    logging.warning('Please review the results.')
    logging.info('-------------------------------------------------------------------------------')

logging.info('Saving calculated magnetic field values in the folder: ' + CloudTempSensDir)
print('Saving calculated magnetic field values in the folder: ' + CloudTempSensDir)
# -------- CALCULATE BLOS AS A FUNCTION OF PERCENT OF THE INPUT TEMPERATURE. --------
