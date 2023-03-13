'''
Downloads and installs all the packages needed to run these scripts.
'''
import sys
import subprocess

#Install packages:
packages = ['numpy==1.19.5',
            'scipy==1.5.4',
            'astropy==4.1',
            'pandas==1.1.5',
            'matplotlib==3.3.4',
            'adjusttext==0.7.3',
            'requests==2.27.1',
            'sklearn==0.0']
commands = [[sys.executable, '-m', 'pip', 'install', '--force-reinstall', package] for package in packages]
subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], shell=False)
#Install all the packages.
for command in commands:
    subprocess.run(command, shell=False)


