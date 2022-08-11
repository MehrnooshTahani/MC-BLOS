'''
Runs all the pre-analysis steps which need to be run only once.
'''
import subprocess
scripts = ["00aInstallPackages.py",
           "00bMakeConfig.py",
           "00cDownloadExampleData.py"]
for script in scripts:
    print("===========================================================")
    print("Script: {}".format(script))
    subprocess.run(["python", script], shell=True)