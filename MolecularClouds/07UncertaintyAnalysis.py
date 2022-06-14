"""
This is the seventh stage of the BLOSMapping method where the uncertainties in the BLOS values are calculated
"""
import os
import pandas as pd
from LocalLibraries.RegionOfInterest import Region
import LocalLibraries.config as config

import logging

# -------- FUNCTION DEFINITION --------
def extinctionChemUncertainties(B, BHigher, BLower):
    if max(B, BHigher, BLower) == B:
        BLowerValue = min(BHigher, BLower)
        BHigherValue = B
    elif min(B, BHigher, BLower) == B:
        BHigherValue = max(BHigher, BLower)
        BLowerValue = B
    else:
        BHigherValue = max(BHigher, BLower)
        BLowerValue = min(BHigher, BLower)

    upperDelta = BHigherValue - B
    lowerDelta = B - BLowerValue

    return upperDelta, lowerDelta
# -------- FUNCTION DEFINITION. --------


# -------- CHOOSE THE REGION OF INTEREST --------
cloudName = config.cloud
regionOfInterest = Region(cloudName)
# -------- CHOOSE THE REGION OF INTEREST. --------

# -------- DEFINE FILES AND PATHS --------
BFilePath = os.path.join(config.dir_root, config.dir_fileOutput, config.cloud, config.prefix_BLOSPointData + config.cloud + '.txt')

BData_DensityPathFragment = os.path.join(config.dir_root, config.dir_fileOutput, config.cloud, config.dir_densitySensitivity)
BData_TempPathFragment = os.path.join(config.dir_root, config.dir_fileOutput, config.cloud, config.dir_temperatureSensitivity)

#BData_Density50IncreasePath = os.path.join(config.dir_root, config.dir_fileOutput, config.cloud, config.dir_densitySensitivity, 'B_Av_T0_n+50.txt')
#BData_Density50DecreasePath = os.path.join(config.dir_root, config.dir_fileOutput, config.cloud, config.dir_densitySensitivity, 'B_Av_T0_n-50.txt')
#BData_Temp20IncreasePath = os.path.join(config.dir_root, config.dir_fileOutput, config.cloud, config.dir_temperatureSensitivity, 'B_Av_T+20_n0.txt')
#BData_Temp20DecreasePath = os.path.join(config.dir_root, config.dir_fileOutput, config.cloud, config.dir_temperatureSensitivity, 'B_Av_T-20_n0.txt')

saveFilePath = os.path.join(config.dir_root, config.dir_fileOutput, config.cloud, config.prefix_BLOSUncertainty + cloudName + '.txt')
# -------- DEFINE FILES AND PATHS --------

# -------- CONFIGURE LOGGING --------
saveScriptLogPath = os.path.join(config.dir_root, config.dir_fileOutput, cloudName, config.dir_logs, "Script7Log.txt")
logging.basicConfig(filename=saveScriptLogPath, filemode='w', format=config.logFormat, level=logging.INFO)
# -------- CONFIGURE LOGGING --------

# -------- READ BLOS DATA--------
BData = pd.read_csv(BFilePath)
# -------- READ BLOS DATA. --------

# -------- CREATE A TABLE FOR THE UNCERTAINTY DATA --------
cols = ['ID#', 'Ra(deg)', 'Dec(deg)', 'Extinction', 'Magnetic_Field(uG)',
        'TotalUpperBUncertainty', 'TotalLowerBUncertainty']
FinalBLOSResults = pd.DataFrame(columns=cols)
# -------- CREATE A TABLE FOR THE UNCERTAINTY DATA. --------

# -------- COPY OVER B DATA --------
# To round, use .round() eg:) FinalBLOSResults['Ra(deg)'] = BData['Ra(deg)'].round(2)
FinalBLOSResults['ID#'] = BData['ID#']
FinalBLOSResults['Ra(deg)'] = BData['Ra(deg)']
FinalBLOSResults['Dec(deg)'] = BData['Dec(deg)']
FinalBLOSResults['Extinction'] = BData['Extinction']
FinalBLOSResults['Magnetic_Field(uG)'] = BData['Magnetic_Field(uG)']
# -------- COPY OVER B DATA. --------

TotalRMErrStDevinB = (BData['Magnetic_Field(uG)']) * (BData['TotalRMScaledErrWithStDev'] /
                                                                         BData['Scaled_RM'])

# -------- CALCULATE UNCERTAINTIES --------
BTotalUpperUncertainty = []
BTotalLowerUncertainty = []

BChemDensIncrease = None
BChemDensDecrease = None
BChemTempIncrease = None
BChemTempDecrease = None

DensPercent = [1, 2.5, 5, 10, 20, 30, 40, 50]
DensPercent = DensPercent[::-1]
TempPercent = [5, 10, 20]
TempPercent = TempPercent[::-1]

errDensPercent = []
for densPercent in DensPercent:
    try:
        BData_DensityIncreasePath = os.path.join(BData_DensityPathFragment, "B_Av_T0_n+{}.txt".format(densPercent))
        BData_DensityDecreasePath = os.path.join(BData_DensityPathFragment, "B_Av_T0_n-{}.txt".format(densPercent))
        BChemDensIncrease = list(pd.read_csv(BData_DensityIncreasePath)['Magnetic_Field(uG)'])
        BChemDensDecrease = list(pd.read_csv(BData_DensityDecreasePath)['Magnetic_Field(uG)'])
        break
    except:
        errDensPercent.append(densPercent)

if len(errDensPercent) > 0:
    logging.info('-------------------------------------------------------------------------------')
    logging.warning('Warning: The following density changes percentages were not used to calculate the uncertainty due to an error.')
    logging.warning('{}'.format(errDensPercent))
    logging.warning('Please review the results.')
    logging.info('-------------------------------------------------------------------------------')

errTempPercent = []
for tempPercent in TempPercent:
    try:
        BData_TempIncreasePath = os.path.join(BData_TempPathFragment, "B_Av_T+{}_n0.txt".format(tempPercent))
        BData_TempDecreasePath = os.path.join(BData_TempPathFragment, "B_Av_T-{}_n0.txt".format(tempPercent))
        BChemTempIncrease = list(pd.read_csv(BData_TempIncreasePath)['Magnetic_Field(uG)'])
        BChemTempDecrease = list(pd.read_csv(BData_TempDecreasePath)['Magnetic_Field(uG)'])
        break
    except:
        errTempPercent.append(tempPercent)

if len(errTempPercent) > 0:
    logging.info('-------------------------------------------------------------------------------')
    logging.warning('Warning: The following temperature changes percentages were not used to calculate the uncertainty due to an error.')
    logging.warning('{}'.format(errTempPercent))
    logging.warning('Please review the results.')
    logging.info('-------------------------------------------------------------------------------')

if BChemDensDecrease is None or BChemDensIncrease is None or BChemTempDecrease is None or BChemTempIncrease is None:
    logging.info('-------------------------------------------------------------------------------')
    logging.warning(
        'Warning: There is insufficient data to calculate the uncertainty with!')
    logging.warning('Make sure the last two scripts (5, 6) were run before this script.')
    logging.warning('This script will fail.')
    logging.warning('Please review the results.')
    logging.info('-------------------------------------------------------------------------------')

for index in range(len(BData)):
    upperDeltaBExt, lowerDeltaBExt = extinctionChemUncertainties(
        BData['Magnetic_Field(uG)'][index], BData['BField_of_Min_Extinction'][index],
        BData['BField_of_Max_Extinction'][index])

    upperDeltaBChemDens, lowerDeltaBChemDens = extinctionChemUncertainties(
        BData['Magnetic_Field(uG)'][index], BChemDensIncrease[index], BChemDensDecrease[index])

    upperDeltaBChemTemp, lowerDeltaBChemTemp = extinctionChemUncertainties(
        BData['Magnetic_Field(uG)'][index], BChemTempIncrease[index], BChemTempDecrease[index])

    # Calculate uncertainties
    BTotalUpperUncertainty.append("{0:.0f}".format(round(((TotalRMErrStDevinB[index]) ** 2 + upperDeltaBExt ** 2
                                                          + upperDeltaBChemDens ** 2 + upperDeltaBChemTemp ** 2) ** (
                                                                 1 / 2), 0)))

    BTotalLowerUncertainty.append("{0:.0f}".format(round(((TotalRMErrStDevinB[index]) ** 2 + lowerDeltaBExt ** 2
                                                          + lowerDeltaBChemDens ** 2 + lowerDeltaBChemTemp ** 2) ** (
                                                                 1 / 2), 0)))

FinalBLOSResults['TotalUpperBUncertainty'] = BTotalUpperUncertainty
FinalBLOSResults['TotalLowerBUncertainty'] = BTotalLowerUncertainty
# -------- CALCULATE UNCERTAINTIES. --------

# -------- SAVE FINAL BLOS RESULTS --------
FinalBLOSResults.to_csv(saveFilePath, index=False)

logging.info('Saving calculated magnetic field values and associated uncertainties to '+saveFilePath)
print('Saving calculated magnetic field values and associated uncertainties to '+saveFilePath)
# -------- SAVE FINAL BLOS RESULTS --------
