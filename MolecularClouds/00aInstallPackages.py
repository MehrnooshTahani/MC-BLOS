'''
Downloads and installs all the packages needed to run these scripts.
'''
import sys
import subprocess

#Install packages:
'''packages = ['numpy<=1.24.2',
            'scipy<=1.10.1',
            'astropy<=5.2.1',
            'pandas<=1.5.3',
            'matplotlib<=3.7.1',
            'adjusttext==0.7.3',
            'requests<=2.28.2',
            'sklearn==0.0']'''
packages = ['numpy',
            'scipy',
            'astropy',
            'pandas<=1.1.5',
            'matplotlib',
            'adjusttext==0.7.3',
            'requests',
            'sklearn==0.0']
commands = [[sys.executable, '-m', 'pip', 'install', '--force-reinstall', package] for package in packages]
subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], shell=False)
#subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'setuptools'], shell=False)
#subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'wheel'], shell=False)
#subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'cython'], shell=False)
#Install all the packages.
for command in commands:
    subprocess.run(command, shell=False)


