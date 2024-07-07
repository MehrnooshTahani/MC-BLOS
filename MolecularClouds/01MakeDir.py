"""
This is the first stage of the BLOSMapping method where the necessary directories are made

    - When run, the file will check for the region of interest.  It will then check to see of this region of
    interest has a folder yet. If not it will make the needed folders and sub-folders.
"""
import os
import LocalLibraries.config as config
import logging

# -------- CHOOSE THE REGION OF INTEREST --------
cloudName = config.cloud
# -------- CHOOSE THE REGION OF INTEREST. --------

# -------- MAKE DIRECTORIES FOR THE REGION OF INTEREST --------
# Check if there is a file output directory already; if not make one
#   - this will house the results for all regions of interest
os.chdir(config.dir_root)
InHome = os.listdir(config.dir_root)
if config.dir_fileOutput not in InHome:
    os.mkdir(config.dir_fileOutput)

# Move into the FileOutput directory
os.chdir(config.dir_fileOutput)

# Check if there is a directory for the specified region of interest already; if not make one
InFileOutput = os.listdir()
InFileOutput = [item.lower() for item in InFileOutput]
if cloudName.lower() not in InFileOutput:
    os.mkdir(cloudName)
    # Move into the directory for the region of interest and make subsequent directories to house its results
    os.chdir(cloudName)
    os.mkdir(config.dir_plots)
    os.mkdir(config.dir_logs)
    os.mkdir(config.dir_densitySensitivity)
    os.mkdir(config.dir_temperatureSensitivity)
    os.mkdir(config.dir_intermediateData)
    os.mkdir(config.dir_finalData)

# ---- CONFIGURE LOGGING
scriptLogFile = config.Script01File
logging.basicConfig(filename=scriptLogFile, filemode='w', format=config.logFormat, level=logging.INFO)
# ---- CONFIGURE LOGGING

# ---- LOG RESULTS
messages = ['Folder {} with sub-folders:'.format(cloudName),
            '\t' + config.dir_plots,
            '\t' + config.dir_logs,
            '\t' + config.dir_densitySensitivity,
            '\t' + config.dir_temperatureSensitivity,
            '\t' + config.dir_intermediateData,
            '\t' + config.dir_finalData,
            'Created in {}'.format(os.path.join(config.dir_root, config.dir_fileOutput))]
for message in messages:
    logging.info(message)
    print(message)
# ---- LOG RESULTS

# -------- MAKE DIRECTORIES FOR THE REGION OF INTEREST. --------
