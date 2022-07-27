import subprocess
scripts = ["00InstallPackages.py",
           "00MakeConfig.py",
           "00DownloadExampleData.py"]
for script in scripts:
    print("===========================================================")
    print("Script: {}".format(script))
    subprocess.run(["python", script], shell=True)