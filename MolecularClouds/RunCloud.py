'''
Runs all the steps of the analysis utilizing the clouds as specified in the command line arguments.
'''
import sys
import subprocess
from configparser import ConfigParser

if len(sys.argv) < 2:
    print("Need a cloud name argument!")
    exit()

#Read the config file and remember the original value.
configStartSettings = ConfigParser()
configStartSettings.read('configStartSettings.ini')
origCloud = configStartSettings['Cloud']['Cloud']

for i in range(1, len(sys.argv)):
    #Change the Cloud
    configStartSettings['Cloud']['Cloud'] = sys.argv[i]
    with open('configStartSettings.ini', 'w') as output_file:
        configStartSettings.write(output_file)

    script = "Run.py"
    subprocess.run([sys.executable, script], shell=False)

#Restore to original settings.
configStartSettings['Cloud']['Cloud'] = origCloud
with open('configStartSettings.ini', 'w') as output_file:
    configStartSettings.write(output_file)