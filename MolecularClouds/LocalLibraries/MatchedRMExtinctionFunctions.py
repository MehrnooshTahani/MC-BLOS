import numpy as np
import pandas as pd

# -------- REMOVE REFERENCE POINTS FROM THE MATCHED RM AND EXTINCTION DATA. --------
def getRefValFromRefData(refData):
    fiducialRM = refData['Reference RM'][0]
    fiducialRMAvgErr = refData['Reference RM AvgErr'][0]
    # Standard error of the sampled mean:
    fiducialRMStd = refData['Reference RM Std'][0]
    fiducialExtinction = refData['Reference Extinction'][0]
    return fiducialRM, fiducialRMAvgErr, fiducialRMStd, fiducialExtinction

def getFiducialValues(refData):
    # -------- FIND FIDUCIAL REFERENCE VALUES --------
    fiducialRM = np.mean(refData['Rotation_Measure(rad/m2)'])
    fiducialRMAvgErr = np.mean(refData['RM_Err(rad/m2)'])
    # Standard error of the sampled mean:
    fiducialRMStd = np.std(refData['Rotation_Measure(rad/m2)'], ddof=1) / np.sqrt(
        len(refData['Rotation_Measure(rad/m2)']))
    fiducialExtinction = np.mean(refData['Extinction_Value'])
    # -------- FIND FIDUCIAL REFERENCE VALUES. --------
    return fiducialRM, fiducialRMAvgErr, fiducialRMStd, fiducialExtinction

def removeMatchingPoints(ExtincRMTable, refRMTable):
    # -------- LOAD MATCHED RM AND EXTINCTION DATA
    AllMatchedRMExtinctionData = ExtincRMTable.copy()
    # -------- LOAD MATCHED RM AND EXTINCTION DATA.

    # -------- REMOVE REFERENCE POINTS FROM THE MATCHED RM AND EXTINCTION DATA --------
    # The rm points used as reference points should not be used to calculate BLOS
    ind = refRMTable['ID#']  # Indices of the reference points
    RMExtinctionData = AllMatchedRMExtinctionData.drop(ind).reset_index(drop=True)
    return RMExtinctionData