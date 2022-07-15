import sys
import subprocess
from configparser import ConfigParser

if len(sys.argv) < 2:
    print("Need a cloud name argument!")
    exit()

for i in range(1, len(sys.argv)):
    configStartSettings = ConfigParser()
    configStartSettings.read('configStartSettings.ini')
    #Cloud
    configStartSettings['Cloud']['Cloud'] = sys.argv[i]

    with open('configStartSettings.ini', 'w') as output_file:
        configStartSettings.write(output_file)

    script = "Run.py"
    subprocess.run(["python", script], shell=True)