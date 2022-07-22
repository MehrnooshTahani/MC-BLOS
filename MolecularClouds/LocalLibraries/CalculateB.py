"""
Contains the functions to calculate BLOS values.
"""
import math

import pandas as pd
import numpy as np
from . import config

def electronColumnDensity(Av, eAbundance, indLayerOfInterest, ScaledExtinction):
    '''
    Finds the electron column density.

    :param Av: The extinction of the cloud. List.
    :param eAbundance: The electron abundances per layer of the cloud. List.
    :param indLayerOfInterest: The layers of interest in the cloud. List.
    :param ScaledExtinction: The extinction corresponding to the layer cared about. List.
    :return: LayerNe: The electron column density for each of the input layers of interest. List.
    '''
    # -------- LOAD CONSTANT INFO FROM CONFIG --------
    conversionFactor = config.VExtinct_2_Hcol  # to convert extinction to H column density
    # -------- LOAD CONSTANT INFO FROM CONFIG --------

    # -------- CALCULATE THE TOTAL ELECTRON COLUMN DENSITY --------
    LayerNe = []
    # -------- Matched Extinction Value
    # For each BLOS point:
    for i, val in enumerate(indLayerOfInterest):
        # Temporary value
        tempSumAvSubXe = 0
        if math.isnan(val):
            tempSumAvSubXe = math.nan
        elif val != 0:
            for index3 in range(1, val):
                tempSumAvSubXe = tempSumAvSubXe + ((Av[index3] - Av[index3 - 1]) * eAbundance[index3])
            # Interpolate:
            xp = [Av[val], Av[val - 1]]
            fp = [eAbundance[val], eAbundance[val - 1]]
            interpAv = (ScaledExtinction[i] / 2)
            interpEAbund = np.interp(interpAv, xp, fp)
            tempSumAvSubXe = tempSumAvSubXe + ((Av[0]) * eAbundance[0]) + (interpAv - Av[val - 1]) * interpEAbund
        else:
            tempSumAvSubXe = tempSumAvSubXe + ((Av[0]) * eAbundance[0])
        LayerNe.append(tempSumAvSubXe * conversionFactor)
    return LayerNe
    # -------- Matched Extinction Value.

def findLayerOfInterest(Av, eAbundance, scaledExtinction):
    '''
    Finds the layer depth and the associated electron abundance of that layer given the extinction of
    :param Av: Per layer extinction value of the cloud. List/iterable.
    :param eAbundance: Per layer electron abundance of the cloud. List/iterable.
    :param scaledExtinction: A list of extinctions for which the user wants to find the layer depth and electron abundance for. List/iterable.
    :return:
        eAbundanceMatched: The electron abundance. List.
        indLayerOfInterest: The number of layers deep corresponding to the input extinction. List.
    '''
    # -------- FIND THE LAYER OF INTEREST --------
    eAbundanceMatched = []
    indLayerOfInterest = []

    # For each BLOS point:
    for i in range(0, len(scaledExtinction)):
        '''We want to find the layer that is closest in value and greater than the half the scaled 
         extinction value. Since Av is a list ordered from least to greatest, this corresponds to the first location 
         where Av is greater than half the scaled extinction value 
        '''
        try:
            ind = np.where(Av >= scaledExtinction[i] / 2)[0][0]
            indLayerOfInterest.append(ind)
            eAbundanceMatched.append(eAbundance[ind])
        except:
            indLayerOfInterest.append(math.nan)
            eAbundanceMatched.append(math.nan)

    return eAbundanceMatched, indLayerOfInterest
    # -------- FIND THE LAYER OF INTEREST. --------

# -------- FUNCTION DEFINITION --------
def CalculateB(AvAbundancePath, ExtincRMPoints, fiducialRM, fiducialRMAvgErr, fiducialRMStd, fiducialExtinction, NegativeExtinctionEntriesChange = "Delete"):
    """
            Takes files containing extinction, rotation measure data, and reference point data for the region of interest
            and calculates BLOS, returning a PANDAS accordingly.

            :param AvAbundancePath:  Path to extinction data produced by chemical evolution code
            :param ExtincRNPoints: Table (pandas dataframe) of non-reference points.
            :param fiducialRM: Reference RM, representing the galactic RM contribution. On positions have this subtracted from them. Float.
            :param fiducialRMAvgErr: Average Error of the Reference RM. Float.
            :param fiducialRMStd: Standard Deviation of the Reference RM. Float.
            :param fiducialExtinction: Reference extinction of the galactic contribution. On positions have this subtracted from them. Float.
            :param NegativeExtinctionEntriesChange: What to do about negative scaled extinction entries. Default is set to Delete. String.
            """

    # -------- SELECT EXTINCTION RM POINT DATA --------
    RMExtinctionData = ExtincRMPoints.copy().reset_index(drop=True)
    # -------- SELECT EXTINCTION RM POINT DATA --------

    # -------- CREATE BLOS TABLE --------
    cols = ['ID#', 'Ra(deg)', 'Dec(deg)', 'RM_Raw_Value', 'RM_Raw_Err', 'Scaled_RM', 'TotalRMScaledErrWithStDev',
            'TotalRMScaledErrWithAvgErr', 'Extinction', 'Scaled_Extinction', 'eAbundance',
            'BScaled_RM_ERR_with_0.05Uncty&StDev', 'BScaled_RM_ERR_with_0.05Uncty',
            'Raw_Magnetic_FieldMagnetic_Field(uG)', 'Magnetic_Field(uG)',
            'Reference_BField_RMErr(\u00B1)', 'BField_of_Min_Extinction', 'BField_of_Max_Extinction']
    BLOSData = pd.DataFrame(columns=cols)
    # -------- CREATE BLOS TABLE. --------

    # -------- ADD TO BLOS TABLE --------
    BLOSData['Ra(deg)'] = RMExtinctionData['Ra(deg)']
    BLOSData['Dec(deg)'] = RMExtinctionData['Dec(deg)']
    BLOSData['ID#'] = RMExtinctionData['ID#']  # Want to keep track of the 'original' index as well
    BLOSData['RM_Raw_Value'] = RMExtinctionData['Rotation_Measure(rad/m2)']
    BLOSData['RM_Raw_Err'] = RMExtinctionData['RM_Err(rad/m2)']
    BLOSData['Extinction'] = RMExtinctionData['Extinction_Value']
    # -------- ADD TO BLOS TABLE. --------

    # -------- SCALE THE RM AND EXTINCTION DATA --------
    BLOSData['Scaled_RM'] = RMExtinctionData['Rotation_Measure(rad/m2)'] - fiducialRM

    BLOSData['Scaled_Extinction'] = RMExtinctionData['Extinction_Value'] - fiducialExtinction
    Scaled_Min_Extinction_Value = RMExtinctionData['Min_Extinction_Value'] - fiducialExtinction
    Scaled_Max_Extinction_Value = RMExtinctionData['Max_Extinction_Value'] - fiducialExtinction
    # ---- Enforce the negative extinction criteria.

    # -------- SCALE THE RM AND EXTINCTION DATA. --------

    # -------- CALCULATE THE RM ERROR --------
    BLOSData['TotalRMScaledErrWithStDev'] = RMExtinctionData['RM_Err(rad/m2)'] + fiducialRMStd
    BLOSData['TotalRMScaledErrWithAvgErr'] = RMExtinctionData['RM_Err(rad/m2)'] + fiducialRMAvgErr
    # -------- CALCULATE THE RM ERROR. --------

    # -------- FIND THE LAYER OF INTEREST --------

    # -------- LOAD CONSTANT INFO FROM CONFIG --------
    conversionFactor = config.VExtinct_2_Hcol  # to convert extinction to H column density
    pcTocm = config.pcTocm
    # -------- LOAD CONSTANT INFO FROM CONFIG --------

    # -------- LOAD ABUNDANCE DATA
    AvAbundanceData = pd.read_csv(AvAbundancePath, delim_whitespace=True, skiprows=1)
    Av = AvAbundanceData["Av"]
    eAbundance = AvAbundanceData["e-"]
    # -------- LOAD ABUNDANCE DATA.

    eAbundanceMatched, indLayerOfInterest = findLayerOfInterest(Av, eAbundance, BLOSData['Scaled_Extinction'])
    _, indLayerOfInterest_MinExt = findLayerOfInterest(Av, eAbundance, Scaled_Min_Extinction_Value)
    _, indLayerOfInterest_MaxExt = findLayerOfInterest(Av, eAbundance, Scaled_Max_Extinction_Value)

    BLOSData['eAbundance'] = eAbundanceMatched
    # -------- FIND THE LAYER OF INTEREST. --------

    # -------- CALCULATE THE TOTAL ELECTRON COLUMN DENSITY --------
    LayerNe = electronColumnDensity(Av, eAbundance, indLayerOfInterest, BLOSData['Scaled_Extinction'])
    LayerNeMinExt = electronColumnDensity(Av, eAbundance, indLayerOfInterest_MinExt, Scaled_Min_Extinction_Value)
    LayerNeMaxExt = electronColumnDensity(Av, eAbundance, indLayerOfInterest_MaxExt, Scaled_Max_Extinction_Value)
    # -------- CALCULATE THE TOTAL ELECTRON COLUMN DENSITY. -------

    # -------- CALCULATE THE MAGNETIC FIELD --------
    BLOSData['Raw_Magnetic_FieldMagnetic_Field(uG)'] = BLOSData['RM_Raw_Value'] / (
            0.812 * np.array(LayerNe) * pcTocm * 2)

    BLOSData['Magnetic_Field(uG)'] = BLOSData['Scaled_RM'] / (
            0.812 * np.array(LayerNe) * pcTocm * 2)

    BLOSData['Reference_BField_RMErr(\u00B1)'] = (BLOSData['RM_Raw_Err'] / BLOSData['RM_Raw_Value']) \
                                                 * BLOSData['Magnetic_Field(uG)']

    BLOSData['BField_of_Min_Extinction'] = BLOSData['Scaled_RM'] / (0.812 * np.array(LayerNeMinExt) * pcTocm * 2)
    BLOSData['BField_of_Max_Extinction'] = BLOSData['Scaled_RM'] / (0.812 * np.array(LayerNeMaxExt) * pcTocm * 2)

    BLOSData['BScaled_RM_ERR_with_0.05Uncty&StDev'] = ((0.05 + fiducialRMStd)
                                                       * BLOSData['Magnetic_Field(uG)']) / \
                                                      BLOSData['Scaled_RM']

    BLOSData['BScaled_RM_ERR_with_0.05Uncty'] = (0.1 * BLOSData['Magnetic_Field(uG)']) \
                                                / BLOSData['Scaled_RM']
    # -------- CALCULATE THE MAGNETIC FIELD. --------

    # -------- CORRECT NEGATIVE SCALED EXTINCTION VALUES. --------
    if NegativeExtinctionEntriesChange == "Zero":
        negativeScaledExtinctionIndex = BLOSData[BLOSData['Scaled_Extinction'] < 0].index.tolist()
        BLOSData.loc[negativeScaledExtinctionIndex, 'Raw_Magnetic_FieldMagnetic_Field(uG)'] = 0
        BLOSData.loc[negativeScaledExtinctionIndex, 'Magnetic_Field(uG)'] = 0
        BLOSData.loc[negativeScaledExtinctionIndex, 'Reference_BField_RMErr(\u00B1)'] = 0
        BLOSData.loc[negativeScaledExtinctionIndex, 'BField_of_Min_Extinction'] = 0
        BLOSData.loc[negativeScaledExtinctionIndex, 'BField_of_Max_Extinction'] = 0
        BLOSData.loc[negativeScaledExtinctionIndex, 'BScaled_RM_ERR_with_0.05Uncty&StDev'] = 0
        BLOSData.loc[negativeScaledExtinctionIndex, 'BScaled_RM_ERR_with_0.05Uncty'] = 0

    elif NegativeExtinctionEntriesChange == "Delete":
        negativeScaledExtinctionIndex = BLOSData[BLOSData['Scaled_Extinction'] < 0].index.tolist()
        BLOSData.drop(negativeScaledExtinctionIndex, inplace=True)
    # -------- CORRECT NEGATIVE SCALED EXTINCTION VALUES. --------

    return BLOSData
