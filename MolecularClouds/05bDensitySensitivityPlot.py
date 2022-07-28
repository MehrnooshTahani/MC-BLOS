"""
This is the second part of the fifth stage of the BLOSMapping method where the dependence on density is assessed.
    - In this part, the differences in the original BLOS and the BLOS calculated with varying electron abundances
    are plotted
"""
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from LocalLibraries.RegionOfInterest import Region
import LocalLibraries.config as config

import logging

# -------- CHOOSE THE REGION OF INTEREST --------
cloudName = config.cloud
regionOfInterest = Region(cloudName)
# -------- CHOOSE THE REGION OF INTEREST. --------

# -------- DEFINE FILES AND PATHS --------
#Input Files
CloudDensSensDir = config.CloudDensSensDir
DensVaryFileTemplate = config.template_BDensSensName
#Output Files
BDensSensPlotFile = config.BDensSensPlot
# -------- DEFINE FILES AND PATHS. --------

# -------- CONFIGURE LOGGING --------
LogFile = config.Script05bFile
loggingDivider = config.logSectionDivider
logging.basicConfig(filename=LogFile, filemode='w', format=config.logFormat, level=logging.INFO)
# -------- CONFIGURE LOGGING --------

# -------- EXTRACT ORIGINAL BLOS VALUES --------
InitPath = DensVaryFileTemplate.format(0) #DensBT0n0File
InitialBData = pd.read_csv(InitPath, sep=config.dataSeparator)
B = list(InitialBData['Magnetic_Field(uG)'])
# -------- EXTRACT ORIGINAL BLOS VALUES. --------

# -------- EXTRACT BLOS FOR EACH PERCENT OF THE INPUT DENSITY -------
p = [1, 2.5, 5, 10, 20, 30, 40, 50]  # Percent of the input density
percent = ['-{}'.format(i) for i in p[::-1]] + ['0'] + ['+{}'.format(i) for i in p]

# ---- Test to see if the files have nan value issues.
errPercent = []
errPercentFiles = []
for i, value in enumerate(percent):
    BScaledFilePath = DensVaryFileTemplate.format(value)
    BScaledTemp = pd.read_csv(BScaledFilePath, sep=config.dataSeparator)
    if BScaledTemp.isnull().values.any() and not config.useUncertaintyNans:
        errPercent.append(value)
        errPercentFiles.append(BScaledFilePath)

percent = [item for item in percent if item not in errPercent]

if len(errPercentFiles) > 0:
    messages = ['Warning: The following data have not been used due to a nan value as per config settings.',
                '{}'.format(errPercentFiles),
                'Please review the results.']
    logging.warning(loggingDivider)
    for message in messages:
        logging.warning(message)
        print(message)
# ---- Test to see if the files have nan value issues.

# Each row is a BLOS point, each column is the BLOS value corresponding to each percent of the input density
AllBScaled = np.zeros([len(B), len(percent)])

for i, value in enumerate(percent):
    BScaledFilePath = BScaledFilePath = DensVaryFileTemplate.format(value)
    BScaledTemp = list(pd.read_csv(BScaledFilePath, sep=config.dataSeparator)['Magnetic_Field(uG)'])
    AllBScaled[:, i] = BScaledTemp[:]
# -------- EXTRACT BLOS FOR EACH PERCENT OF THE INPUT DENSITY. -------

# -------- CHOOSE INDICES OF BLOS POINTS TO PLOT -------
numToPlot = int(config.densityPlotNumPoints)
AvMinToPlot = float(config.densityPlotMinExtinct)
AvMaxToPlot = float(config.densityPlotMaxExtinct)

indMin = list(np.where(np.array(InitialBData['Scaled_Extinction']) >= AvMinToPlot)[0])
indMax = list(np.where(np.array(InitialBData['Scaled_Extinction']) <= AvMaxToPlot)[0])
ind = list(set(indMin).intersection(indMax))
if len(ind) < numToPlot:
    indToPlot = ind
else:
    indToPlot = ind[:numToPlot]
# -------- CHOOSE INDICES OF BLOS POINTS TO PLOT. -------

# -------- CREATE A FIGURE -------
fig = plt.figure(figsize=(12, 12), dpi=120, facecolor='w', edgecolor='k')

plt.ylabel('Magnetic Field Difference (' + r'$ \mu G$)', fontsize=16)
plt.xlabel(r'$\frac{\Delta n}{n_0} (\%)$', fontsize=16, labelpad=20)
plt.title('B$_{LOS}$ Variation, ' + cloudName + ', T = T$_0$', fontsize=16)

x = np.arange(0, len(percent))
plt.xticks(x, percent)

for i, ind in enumerate(indToPlot):
    barloc = [item + 0.15 * int(i) for item in x]
    plt.bar(barloc, B[ind] - AllBScaled[ind], width=0.25, edgecolor='k', label=indToPlot[i])

# ---- Style the legend
plt.legend(loc='upper center', ncol=2)
# ---- Style the legend.
# -------- CREATE A FIGURE. -------

# ---- Display or save the figure
# plt.show()
plt.savefig(BDensSensPlotFile)
# ---- Display or save the figure.
message = 'Saving Density Sensitivity figure to ' + BDensSensPlotFile
logging.info(message)
print(message)
# -------- CREATE A FIGURE. --------
