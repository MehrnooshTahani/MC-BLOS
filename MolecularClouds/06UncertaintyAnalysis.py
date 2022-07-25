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
#Input Files
BLOSPointsFile = config.BLOSPointsFile

CloudDensSensDir = config.CloudDensSensDir
CloudTempSensDir = config.CloudTempSensDir
#Output Files
BLOSUncertaintyFile = config.BLOSUncertaintyFile
# -------- DEFINE FILES AND PATHS --------

# -------- CONFIGURE LOGGING --------
LogFile = config.Script06File
loggingDivider = config.logSectionDivider
logging.basicConfig(filename=LogFile, filemode='w', format=config.logFormat, level=logging.INFO)
# -------- CONFIGURE LOGGING --------

# -------- READ BLOS DATA--------
BData = pd.read_csv(BLOSPointsFile)
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
    BData_DensityIncreasePath = os.path.join(CloudDensSensDir, "B_Av_T0_n+{}.txt".format(densPercent))
    BData_DensityDecreasePath = os.path.join(CloudDensSensDir, "B_Av_T0_n-{}.txt".format(densPercent))
    BData_DensityIncrease = pd.read_csv(BData_DensityIncreasePath)
    BData_DensityDecrease = pd.read_csv(BData_DensityDecreasePath)

    BChemDensIncrease = list(BData_DensityIncrease['Magnetic_Field(uG)'])
    BChemDensDecrease = list(BData_DensityDecrease['Magnetic_Field(uG)'])

    if (BData_DensityIncrease.isnull().values.any() or BData_DensityDecrease.isnull().values.any()) and config.useUncertaintyNans is False:
        errDensPercent.append(densPercent)
    else:
        break

if len(errDensPercent) > 0:
    messages = ['Warning: The following density changes percentages (+-) were not used to calculate the uncertainty.',
                '{}'.format(errDensPercent),
                'A percentage change file associated with the percentage has a nan value.',
                'The config policy on using nan values in uncertainty calculations is set to: {}.'.format(config.useUncertaintyNans),
                'Ex. 50 means that at least one of -50 or 50 percent changes have an error.',
                'Please review the results.']
    logging.warning(loggingDivider)
    map(logging.warning, messages)

errTempPercent = []
for tempPercent in TempPercent:
    BData_TempIncreasePath = os.path.join(CloudTempSensDir, "B_Av_T+{}_n0.txt".format(tempPercent))
    BData_TempDecreasePath = os.path.join(CloudTempSensDir, "B_Av_T-{}_n0.txt".format(tempPercent))
    BData_TempIncrease = pd.read_csv(BData_TempIncreasePath)
    BData_TempDecrease = pd.read_csv(BData_TempDecreasePath)

    BChemTempIncrease = list(BData_TempIncrease['Magnetic_Field(uG)'])
    BChemTempDecrease = list(BData_TempDecrease['Magnetic_Field(uG)'])

    if BData_TempIncrease.isnull().values.any() or BData_TempDecrease.isnull().values.any() and config.useUncertaintyNans is False:
        errTempPercent.append(tempPercent)
    else:
        break

if len(errTempPercent) > 0:
    messages = ['Warning: The following temperature changes percentages (+-) were not used to calculate the uncertainty.',
                '{}'.format(errTempPercent),
                'A percentage change file associated with the percentage has a nan value.',
                'The config policy on using nan values in uncertainty calculations is set to: {}.'.format(config.useUncertaintyNans),
                'Ex. 20 means that at least one of -20 or 20 percent changes have an error.',
                'Please review the results.']
    logging.warning(loggingDivider)
    map(logging.warning, messages)

if BChemDensDecrease is None or BChemDensIncrease is None or BChemTempDecrease is None or BChemTempIncrease is None:
    messages = ['Warning: There is insufficient data to calculate the uncertainty with!',
                'Make sure the last two scriPoints (5, 6) were run before this script.',
                'This script will fail.',
                'Please review the results.',]
    logging.warning(loggingDivider)
    map(logging.warning, messages)

#Find the uncertainty for each row of data.
for index in range(len(BData)):
    #Identify the uncertainty.
    upperDeltaBExt, lowerDeltaBExt = extinctionChemUncertainties(
        BData['Magnetic_Field(uG)'][index], BData['BField_of_Min_Extinction'][index],
        BData['BField_of_Max_Extinction'][index])
    upperDeltaBChemDens, lowerDeltaBChemDens = extinctionChemUncertainties(
        BData['Magnetic_Field(uG)'][index], BChemDensIncrease[index], BChemDensDecrease[index])
    upperDeltaBChemTemp, lowerDeltaBChemTemp = extinctionChemUncertainties(
        BData['Magnetic_Field(uG)'][index], BChemTempIncrease[index], BChemTempDecrease[index])
    # Calculate uncertainties
    BUpperUncertainty = round(((TotalRMErrStDevinB[index]) ** 2 + upperDeltaBExt ** 2 + upperDeltaBChemDens ** 2 + upperDeltaBChemTemp ** 2) ** (1 / 2), 0)
    BLowerUncertainty = round(((TotalRMErrStDevinB[index]) ** 2 + lowerDeltaBExt ** 2 + lowerDeltaBChemDens ** 2 + lowerDeltaBChemTemp ** 2) ** (1 / 2), 0)
    #Avoid overestimating the uncertainty. The propagated uncertainty
    BUpperUncertainty = TotalRMErrStDevinB[index] if abs(BUpperUncertainty) > abs(BData['Magnetic_Field(uG)'][index]) and BData['Scaled_RM'][index] < 0 else BUpperUncertainty
    BLowerUncertainty = TotalRMErrStDevinB[index] if abs(BLowerUncertainty) > abs(BData['Magnetic_Field(uG)'][index]) and BData['Scaled_RM'][index] > 0 else BLowerUncertainty
    #Append the uncertainty to the list.
    BTotalUpperUncertainty.append("{0:.0f}".format(BUpperUncertainty))
    BTotalLowerUncertainty.append("{0:.0f}".format(BLowerUncertainty))

FinalBLOSResults['TotalUpperBUncertainty'] = BTotalUpperUncertainty
FinalBLOSResults['TotalLowerBUncertainty'] = BTotalLowerUncertainty
# -------- CALCULATE UNCERTAINTIES. --------

# -------- SAVE FINAL BLOS RESULTS --------
FinalBLOSResults.to_csv(BLOSUncertaintyFile, index=False, na_rep='nan')
message = 'Saving calculated magnetic field values and associated uncertainties to ' + BLOSUncertaintyFile
logging.info(message)
print(message)
# -------- SAVE FINAL BLOS RESULTS --------
