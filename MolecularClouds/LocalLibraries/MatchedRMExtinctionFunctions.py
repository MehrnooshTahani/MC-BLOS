import numpy as np
'''
Contains functions commonly performed on the MatchedRMExtinction dataset and related files.
'''
# -------- REMOVE REFERENCE POINTS FROM THE MATCHED RM AND EXTINCTION DATA. --------
def unpackRefData(refData):
    '''
    Unpacks the reference values from the reference value PANDAS table.

    :param refData: A PANDAS table which contains the reference values, generated in script 3.
    :return: fiducialRM, fiducialRMAvgErr, fiducialRMStd, fiducialExtinction - the extracted reference values.
    '''
    fiducialRM = refData['Reference RM'][0]
    fiducialRMAvgErr = refData['Reference RM AvgErr'][0]
    # Standard error of the sampled mean:
    fiducialRMStd = refData['Reference RM Std'][0]
    fiducialExtinction = refData['Reference Extinction'][0]
    return fiducialRM, fiducialRMAvgErr, fiducialRMStd, fiducialExtinction

def calcFiducialVals(refData):
    '''
    Calculates the reference values from the reference points PANDAS table. Assumes no weighting.
    :param refData: Table with the Reference Point information. PANDAS table.
    :return: fiducialRM, fiducialRMAvgErr, fiducialRMStd, fiducialExtinction - the calculated reference values.
    '''
    # -------- FIND FIDUCIAL REFERENCE VALUES --------
    fiducialRM = np.mean(refData['Rotation_Measure(rad/m2)'])
    fiducialRMAvgErr = np.mean(refData['RM_Err(rad/m2)'])
    # Standard error of the sampled mean:
    fiducialRMStd = np.std(refData['Rotation_Measure(rad/m2)'], ddof=1) / np.sqrt(len(refData['Rotation_Measure(rad/m2)']))
    fiducialExtinction = np.mean(refData['Extinction_Value'])
    # -------- FIND FIDUCIAL REFERENCE VALUES. --------
    return fiducialRM, fiducialRMAvgErr, fiducialRMStd, fiducialExtinction

def rmMatchingPts(ExtincRMTable, refRMTable):
    '''
    Given two matched RM extinction tables, returns a new table with the elements the second has in common with the first removed.
    :param ExtincRMTable: The first table, to have elements removed from.
    :param refRMTable: The second table, to have its elements removed from the first.
    :return: RMExtinctionData: A table with the entries of the first and none of the second.
    '''
    # -------- LOAD MATCHED RM AND EXTINCTION DATA
    AllMatchedRMExtinctionData = ExtincRMTable.copy()
    # -------- LOAD MATCHED RM AND EXTINCTION DATA.

    # -------- REMOVE REFERENCE POINTS FROM THE MATCHED RM AND EXTINCTION DATA --------
    # The rm points used as reference points should not be used to calculate BLOS
    ind = refRMTable['ID#']  # Indices of the reference points
    RMExtinctionData = AllMatchedRMExtinctionData.drop(ind).reset_index(drop=True)
    return RMExtinctionData