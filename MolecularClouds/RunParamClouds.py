'''
Runs all the steps of the analysis utilizing the clouds as specified in the command line arguments.
'''
import os
import sys
import subprocess
from configparser import ConfigParser

if len(sys.argv) < 3:
    print("Need a config argument!")
    print("Need a cloud name argument!")
    print("There should be two or more arguments.")
    print("Format is [config] [cloud] ... [cloud]")
    exit()
#Obtain and read the changed config.
configName = sys.argv[1]
configStartSettings = ConfigParser()
configStartSettings.read(configName)
#Read and remember the original config.
configOriginalSettings = ConfigParser()
configOriginalSettings.read('configStartSettings.ini')
#Save the changed config to the original.
with open('configStartSettings.ini', 'w') as output_file:
    configStartSettings.write(output_file)
#Change the currently used config to point to the main config file.
configStartSettings = ConfigParser()
configStartSettings.read('configStartSettings.ini')

for i in range(2, len(sys.argv)):
    #Change the cloud.
    configStartSettings['Cloud']['Cloud'] = sys.argv[i]
    with open('configStartSettings.ini', 'w') as output_file:
        configStartSettings.write(output_file)
    #Run the analysis.
    script = "Run.py"
    subprocess.run(["python", script], shell=True)

#Rename the output folder with the changed config name.
configFolderSettings = ConfigParser()
configFolderSettings.read('configDirectoryAndNames.ini')
outputFolder = os.path.join(configFolderSettings['Output File Locations']['root'], configFolderSettings['Output File Locations']['file output'])
outputFolderRenamed = os.path.join(configFolderSettings['Output File Locations']['root'], configFolderSettings['Output File Locations']['file output'] + configName)
os.rename(outputFolder, outputFolderRenamed)
#Restore original settings.
with open('configStartSettings.ini', 'w') as output_file:
    configOriginalSettings.write(output_file)