"""
This is the seventh stage of the BLOSMapping method where the uncertainties in the BLOS values are calculated
"""
import pandas as pd
from LocalLibraries.RegionOfInterest import Region
import LocalLibraries.config as config

import logging

# -------- FUNCTION DEFINITION --------
def extinctionChemUncertainties(B, BHigher, BLower):
    '''
    Finds the biggest difference between B and the input values.
    :param B: The magnetic field
    :param BHigher: The higher magnetic field variance
    :param BLower: The lower magnetic field variance
    :return: upperDelta, lowerDelta - the difference between B and the higher/lower of the three values.
    '''
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

DensVaryNameTemplate = config.template_BDensSensName
TempVaryNameTemplate = config.template_BTempSensName
#Output Files
BLOSUncertaintyFile = config.BLOSUncertaintyFile
# -------- DEFINE FILES AND PATHS --------

# -------- CONFIGURE LOGGING --------
LogFile = config.Script07File
loggingDivider = config.logSectionDivider
logging.basicConfig(filename=LogFile, filemode='w', format=config.logFormat, level=logging.INFO)
# -------- CONFIGURE LOGGING --------

# -------- READ BLOS DATA--------
BData = pd.read_csv(BLOSPointsFile, sep=config.dataSeparator)
# -------- READ BLOS DATA. --------

# -------- CREATE A TABLE FOR THE UNCERTAINTY DATA --------
cols = ['ID#', 'Ra(deg)', 'Dec(deg)', 'Extinction', 'Magnetic_Field(uG)', 'TotalUpperBUncertainty', 'TotalLowerBUncertainty']
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

TotalRMErrStDevinB = (BData['Magnetic_Field(uG)']) * (BData['TotalRMScaledErrWithStDev'] /BData['Scaled_RM'])

# -------- CALCULATE UNCERTAINTIES --------
# ---- Establish values and parameters
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
# ---- Establish values and parameters

# ---- Check to see if there's any missing data in the density variance data we intend to use. If so, depending on the config option, skip to the next one, or just use it.
errDensPercent = []
for densPercent in DensPercent:
    BData_DensityIncreasePath = DensVaryNameTemplate.format("+{}".format(densPercent))
    BData_DensityDecreasePath = DensVaryNameTemplate.format("-{}".format(densPercent))
    BData_DensityIncrease = pd.read_csv(BData_DensityIncreasePath, sep=config.dataSeparator)
    BData_DensityDecrease = pd.read_csv(BData_DensityDecreasePath, sep=config.dataSeparator)

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
    for message in messages:
        logging.warning(message)
        print(message)
# ---- Check to see if there's any missing data in the density variance data we intend to use. If so, depending on the config option, skip to the next one, or just use it.

# ---- Check to see if there's any missing data in the temperature variance data we intend to use. If so, depending on the config option, skip to the next one, or just use it.
errTempPercent = []
for tempPercent in TempPercent:
    BData_TempIncreasePath = TempVaryNameTemplate.format("+{}".format(tempPercent))
    BData_TempDecreasePath = TempVaryNameTemplate.format("-{}".format(tempPercent))
    BData_TempIncrease = pd.read_csv(BData_TempIncreasePath, sep=config.dataSeparator)
    BData_TempDecrease = pd.read_csv(BData_TempDecreasePath, sep=config.dataSeparator)

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
    for message in messages:
        logging.warning(message)
        print(message)
# ---- Check to see if there's any missing data in the temperature variance data we intend to use. If so, depending on the config option, skip to the next one, or just use it.

# ---- Check to see if no data can be loaded due to the config settings above removing nan valued entries.
if BChemDensDecrease is None or BChemDensIncrease is None or BChemTempDecrease is None or BChemTempIncrease is None:
    messages = ['Warning: There is insufficient data to calculate the uncertainty with!',
                'Make sure the last two scripts (5, 6) were run before this script.',
                'This script will fail.',
                'Please review the results.',]
    logging.warning(loggingDivider)
    for message in messages:
        logging.warning(message)
        print(message)
# ---- Check to see if no data can be loaded due to the config settings above removing nan valued entries.

# ---- Find the uncertainty for each row of data.
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
    #Avoid overestimating the uncertainty. The propagated uncertainty should not cause the uncertainty to be able to flip the sign, if it cannot already do that.
    BUpperUncertainty = abs(BData['Magnetic_Field(uG)'][index]+1) if abs(BUpperUncertainty) > abs(BData['Magnetic_Field(uG)'][index]) and BData['Scaled_RM'][index] < 0 else BUpperUncertainty #TotalRMErrStDevinB[index] if abs(BUpperUncertainty) > abs(BData['Magnetic_Field(uG)'][index]) and BData['Scaled_RM'][index] < 0 else BUpperUncertainty
    BLowerUncertainty = abs(BData['Magnetic_Field(uG)'][index]-1) if abs(BLowerUncertainty) > abs(BData['Magnetic_Field(uG)'][index]) and BData['Scaled_RM'][index] > 0 else BLowerUncertainty #TotalRMErrStDevinB[index] if abs(BLowerUncertainty) > abs(BData['Magnetic_Field(uG)'][index]) and BData['Scaled_RM'][index] > 0 else BLowerUncertainty
    #Append the uncertainty to the list.
    BTotalUpperUncertainty.append("{0:.0f}".format(BUpperUncertainty))
    BTotalLowerUncertainty.append("{0:.0f}".format(BLowerUncertainty))

FinalBLOSResults['TotalUpperBUncertainty'] = BTotalUpperUncertainty
FinalBLOSResults['TotalLowerBUncertainty'] = BTotalLowerUncertainty
# ---- Find the uncertainty for each row of data.
# -------- CALCULATE UNCERTAINTIES. --------

# -------- SAVE FINAL BLOS RESULTS --------
FinalBLOSResults.to_csv(BLOSUncertaintyFile, index=False, na_rep=config.missingDataRep, sep=config.dataSeparator)
message = 'Saving calculated magnetic field values and associated uncertainties to ' + BLOSUncertaintyFile
logging.info(message)
print(message)
# -------- SAVE FINAL BLOS RESULTS --------
