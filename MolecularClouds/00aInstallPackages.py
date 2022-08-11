'''
Downloads and installs all the packages needed to run these scripts.
'''
import sys
import subprocess

#Install packages:
packages = ['numpy',
            'scipy',
            'astropy',
            'pandas',
            'matplotlib',
            'adjusttext',
            'requests',
            'sklearn']
commands = [[sys.executable, '-m', 'pip', 'install', '--upgrade', package] for package in packages]
subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], shell=True)
#Install all the packages.
for command in commands:
    subprocess.run(command, shell=True)

