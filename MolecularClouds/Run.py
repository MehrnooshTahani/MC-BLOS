import subprocess
scripts = ["00MakeDir.py",
           "01aRMMatching.py","01bRMMapping.py",
           "02aFilterReferencePoints.py","02bConsiderReferencePoints.py","02cMapReferencePoints.py",
           "03CalculateBLOS.py",
           "04aDensitySensitivity.py","04bDensitySensitivityPlot.py",
           "05aTempSensitivity.py","05bTempSensitivityPlot.py",
           "06UncertaintyAnalysis.py"]
for script in scripts:
    print("===========================================================")
    print("Script: {}".format(script))
    subprocess.run(["python", script], shell=True)
#subprocess.run(["python", "00MakeConfig.py"], shell=True)