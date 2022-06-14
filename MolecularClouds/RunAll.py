import subprocess

#subprocess.run(["python", "00ConfigureDirInfo.py"], shell=True)
subprocess.run(["python","00MakeDir.py"], shell=True)
subprocess.run(["python","01RMMapping.py"], shell=True)
subprocess.run(["python","02RMMatching.py"], shell=True)
subprocess.run(["python","03DetermineRefPoints.py"], shell=True)
subprocess.run(["python","04CalculateBLOS.py"], shell=True)
subprocess.run(["python","05aDensitySensitivity.py"], shell=True)
subprocess.run(["python","05bDensitySensitivityPlot.py"], shell=True)
subprocess.run(["python","06aTempSensitivity.py"], shell=True)
subprocess.run(["python","06bTempSensitivityPlot.py"], shell=True)
subprocess.run(["python","07UncertaintyAnalysis.py"], shell=True)
