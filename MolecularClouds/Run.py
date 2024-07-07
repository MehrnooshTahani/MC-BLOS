'''
Runs all the steps of the analysis utilizing the configuration file at hand.
'''
import sys
import subprocess
scripts = ["01MakeDir.py",
           "02aRMMatching.py","02bRMMapping.py",
           "03aFilterReferencePoints.py","03bConsiderReferencePoints.py","03cMapReferencePoints.py",
           "04CalculateBLOS.py",
           "05aDensitySensitivity.py","05bDensitySensitivityPlot.py",
           "06aTempSensitivity.py","06bTempSensitivityPlot.py",
           "07UncertaintyAnalysis.py"]
for script in scripts:
    print("===========================================================")
    print("Script: {}".format(script))
    subprocess.run([sys.executable, script], shell=False)
