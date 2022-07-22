import os
import sys
import subprocess
from configparser import ConfigParser

if len(sys.argv) < 3:
    print("Need a config argument!")
    print("Need a cloud name argument!")
    exit()

configName = sys.argv[1]
configStartSettings = ConfigParser()
configStartSettings.read(configName)
with open('configStartSettings.ini', 'w') as output_file:
    configStartSettings.write(output_file)

for i in range(2, len(sys.argv)):
    configStartSettings = ConfigParser()
    configStartSettings.read('configStartSettings.ini')
    #Cloud
    configStartSettings['Cloud']['Cloud'] = sys.argv[i]

    with open('configStartSettings.ini', 'w') as output_file:
        configStartSettings.write(output_file)

    script = "Run.py"
    subprocess.run(["python", script], shell=True)

configFolderSettings = ConfigParser()
configFolderSettings.read('configDirectoryAndNames.ini')
outputFolder = os.path.join(configFolderSettings['Output File Locations']['root'], configFolderSettings['Output File Locations']['file output'])
outputFolderRenamed = os.path.join(configFolderSettings['Output File Locations']['root'], configFolderSettings['Output File Locations']['file output'] + configName)
os.rename(outputFolder, outputFolderRenamed)