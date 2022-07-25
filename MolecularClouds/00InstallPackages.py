import sys
import subprocess

#Install packages:
packages = ['numpy',
            'scipy',
            'astropy',
            'pandas',
            'matplotlib',
            'adjusttext']
commands = [[sys.executable, '-m', 'pip', 'install', package] for package in packages]
subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], shell=True)
for command in commands:
    subprocess.run(command, shell=True)

