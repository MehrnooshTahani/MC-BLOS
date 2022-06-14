"""
This is the fifth stage of the BLOSMapping method where the dependence on density is assessed.
    - All parameters except for density are held constant, and the magnetic field is calculated with electron abundances
    corresponding to changes of 0 and +/- 1, 2.5, 5, 10, 20, 20, 40, and 50 % the fiducial input density
"""
from LocalLibraries.CalculateB import CalculateB
import os
from MolecularClouds.LocalLibraries.RegionOfInterest import Region
import pandas as pd
import LocalLibraries.config as config

import LocalLibraries.MatchedRMExtinctionFunctions as MREF
import logging

# -------- CHOOSE THE REGION OF INTEREST --------
cloudName = config.cloud
regionOfInterest = Region(cloudName)
# -------- CHOOSE THE REGION OF INTEREST. --------

# -------- DEFINE FILES AND PATHS --------
MatchedRMExtincPath = os.path.join(config.dir_root, config.dir_fileOutput, config.cloud, config.prefix_RMExtinctionMatch + config.cloud + '.txt')
RefPointPath = os.path.join(config.dir_root, config.dir_fileOutput, config.cloud, config.prefix_selRefPoints + config.cloud + '.txt')
FilePath_ReferenceData = os.path.join(config.dir_root, config.dir_fileOutput, cloudName, config.prefix_refData + cloudName + '.txt')
saveFileDir = os.path.join(config.dir_root, config.dir_fileOutput, config.cloud, config.dir_densitySensitivity)
# -------- DEFINE FILES AND PATHS. --------

# -------- CONFIGURE LOGGING --------
saveScriptLogPath = os.path.join(config.dir_root, config.dir_fileOutput, cloudName, config.dir_logs, "Script5aLog.txt")
logging.basicConfig(filename=saveScriptLogPath, filemode='w', format=config.logFormat, level=logging.INFO)
# -------- CONFIGURE LOGGING --------

# -------- READ REFERENCE POINT TABLE --------
matchedRMExtincTable = pd.read_csv(MatchedRMExtincPath, sep='\t')
refPointTable = pd.read_csv(RefPointPath)
remainingTable = MREF.removeMatchingPoints(matchedRMExtincTable, refPointTable)
refData = pd.read_csv(FilePath_ReferenceData)
fiducialRM, fiducialRMAvgErr, fiducialRMStd, fiducialExtinction = MREF.getRefValFromRefData(refData)
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
    saveFilePath = saveFileDir + os.sep + 'B_' + AvAbundanceName + '.txt'
    try:
        B = CalculateB(AvAbundancePath, remainingTable, fiducialRM, fiducialRMAvgErr, fiducialRMStd, fiducialExtinction)
        B.to_csv(saveFilePath, index=False)
    except:
        print("Error! {}".format(value))
        errPercent.append(value)

if len(errPercent) > 0:
    logging.info('-------------------------------------------------------------------------------')
    logging.warning('Warning: The following density changes have not been calculated due to an error.')
    logging.warning('{}'.format(errPercent))
    logging.warning('Please review the results.')
    logging.info('-------------------------------------------------------------------------------')

logging.info('Saving calculated magnetic field values in the folder: '+saveFileDir)
print('Saving calculated magnetic field values in the folder: '+saveFileDir)
# -------- CALCULATE BLOS AS A FUNCTION OF PERCENT OF THE INPUT DENSITY. --------
