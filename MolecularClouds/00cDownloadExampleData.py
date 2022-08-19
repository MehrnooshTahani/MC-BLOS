'''
This is a convenience script used to download

This script's downloads can be modified by adding the url of the file you want added to the url lists below.
'''
import os
import gzip
import shutil
import zipfile
import requests

from itertools import zip_longest

import numpy as np
import pandas as pd

import LocalLibraries.ConversionLibrary as cl
import LocalLibraries.config as config

def download_files(urls, dir, print_status = True):
    '''
    Downloads the file specified in the list of URLs to the directory specified.
    :param urls: The list of urls of files to download. List of strings.
    :param dir: The directory to save the files to. String.
    :param print_status: Report what the function is currently doing at each step to the terminal. Useful for observing progress in large downloads.
    :return: outputs - file names (with full directory paths) of the files downloaded. List of strings.
    '''
    outputs = []
    for url in urls:
        # Information
        if print_status:
            print("Obtaining: {}".format(url))
        # Find the file name
        file_name = os.path.basename(url)
        file_name = os.path.join(dir, file_name)
        # Download the file from the URL
        req = requests.get(url, stream=True)
        with open(file_name, 'wb') as file:
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
        outputs.append(file_name)
    return outputs

def unzip_gzs(files_in, print_status = True):
    '''
    Unzips files with the specified names, if they are .gz files.
    :param files_in: List of files. List of strings.
    :param print_status: Report what the function is currently doing at each step to the terminal. Useful for observing progress in large unzips.
    :return: outputs - List of unzipped files. List of strings.
    '''
    files = [file for file in files_in if file.endswith('.gz')]
    outputs = []
    for file in files:
        # Information
        if print_status:
            print("Unzipping: {}".format(file))
        # Unzip
        with gzip.open(file, 'rb') as file_in:
            with open(file[:-len('.gz')], 'wb') as file_out:
                shutil.copyfileobj(file_in, file_out)
                outputs.append(file[:-len('.gz')])
    return outputs

def unzip(files_in, print_status = True):
    '''
    Unzips files with the specified names, if they are .gz files.
    :param files_in: List of files. List of strings.
    :param print_status: Report what the function is currently doing at each step to the terminal. Useful for observing progress in large unzips.
    :return: outputs - List of unzipped files. List of strings.
    '''
    files = [file for file in files_in if file.endswith('.zip')]
    outputs = []
    for file in files:
        # Information
        if print_status:
            print("Unzipping: {}".format(file))
        # Unzip
        with zipfile.ZipFile(file,"r") as file_in:
            file_in.extractall(os.path.dirname(file))
    return outputs

def addHeader(headerless_file, headerfile):
    '''
    Adds a header to the headerless data fil.
    :param headerless_file: The data file without a header.
    :param headerfile: The data file which consists of the header.
    :return: Nothing, the header is simply appended to the headerless file.
    '''
    headerless = pd.read_csv(headerless_file, delim_whitespace=True, header=None)
    header = pd.read_csv(headerfile, delim_whitespace=True)
    headerless.set_axis(header.columns, axis=1, inplace=True)
    headerless.to_csv(headerless_file, index=False, sep=config.dataSeparator)

def CameronToTaylorFormat(Cameron_Data_File):
    Cameron_Data = pd.read_csv(Cameron_Data_File, sep='\t', error_bad_lines=False, engine="python")

    ra = Cameron_Data['ra']
    dec = Cameron_Data['dec']

    raHours, raMins, raSecs = cl.ra_deg2hms(np.array(ra))
    decDegs, decArcmins, decArcsecs = cl.dec_deg2dms(np.array(dec))
    errHr, errMin, errSec = cl.ra_deg2hms(np.array(Cameron_Data['pos_err']))
    raErrSecs = decErrArcsecs = errSec + 60 * errMin + 60 * 60 * errHr
    longitudeDegs = Cameron_Data['l'] #Note: Cameron's galactic longitudes aren't shifted/are right
    latitudeDegs = Cameron_Data['b']
    nvssStokesIs = Cameron_Data['stokesI']
    stokesIErrs = Cameron_Data['stokesI_err']
    AvePeakPIs = Cameron_Data['polint']
    PIErrs = Cameron_Data['polint_err']
    polarizationPercents = Cameron_Data['fracpol']
    mErrPercents = Cameron_Data['fracpol_err']
    rotationMeasures = Cameron_Data['rm']
    RMErrs = Cameron_Data['rm_err']
    colsCameron = ['ra', 'dec', 'l', 'b', 'pos_err',
                   'rm', 'rm_err', 'rm_width', 'rm_width_err',
                   'complex_flag', 'complex_test', 'rm_method', 'ionosphere', 'Ncomp',
                   'stokesI', 'stokesI_err', 'spectral_index', 'spectral_index_err',
                   'reffreq_I', 'polint', 'polint_err', 'pol_bias', 'flux_type', 'aperture',
                   'fracpol', 'fracpol_err', 'polangle', 'polangle_err', 'reffreq_pol',
                   'stokesQ', 'stokesQ_err', 'stokesU', 'stokesU_err',
                   'derot_polangle', 'derot_polangle_err', 'stokesV', 'stokesV_err',
                   'beam_maj', 'beam_min', 'beam_pa', 'reffreq_beam', 'minfreq', 'maxfreq',
                   'channelwidth', 'Nchan', 'rmsf_fwhm', 'noise_chan',
                   'telescope', 'int_time', 'epoch', 'interval', 'leakage',
                   'beamdist', 'catalog', 'dataref', 'cat_id', 'type', 'notes']

    Taylor_columns = ['raHours','raMins','raSecs','raErrSecs','decDegs','decArcmins','decArcsecs','decErrArcsecs',
               'longitudeDegs','latitudeDegs','nvssStokesIs','stokesIErrs','AvePeakPIs','PIErrs',
               'polarizationPercents','mErrPercents','rotationMeasures','RMErrs']
    Taylor_data = list(zip_longest(raHours,raMins,raSecs,raErrSecs,decDegs,decArcmins,decArcsecs,decErrArcsecs,longitudeDegs,latitudeDegs,nvssStokesIs,stokesIErrs,AvePeakPIs,PIErrs,polarizationPercents,mErrPercents,rotationMeasures,RMErrs,fillvalue=''))
    Cameron_to_Taylor_frame = pd.DataFrame(Taylor_data, columns=Taylor_columns)
    Cameron_to_Taylor_frame.to_csv('Data\\RMCatalog\\Cameron(Taylor_Format).dat', sep='\t',  na_rep = 'nan', index=False)

density_fits_file_urls = ['http://www.herschel.fr/Phocea/file.php?class=astimg&file=66/HGBS_aquilaM2_column_density_map.fits.gz',
                          'http://www.herschel.fr/cea/gouldbelt/en/Phocea/file.php?class=astimg&file=66/HGBS_cep1157_column_density_map.fits',
                          'http://www.herschel.fr/Phocea/file.php?class=astimg&file=66/HGBS_chamI_hires_column_density_map.fits.gz',
                          'http://www.herschel.fr/Phocea/file.php?class=astimg&file=66/HGBS_chamII_III_hires_column_density_map.fits.gz',
                          'http://www.herschel.fr/Phocea/file.php?class=pere&file=Images/astImg/66/HGBS_craNS_column_density_map.fits.gz',
                          'http://www.herschel.fr/Phocea/file.php?class=pere&file=Images/astImg/66/HGBS_craNS_column_density_map.fits.gz',
                          'http://www.herschel.fr/Phocea/file.php?class=astimg&file=66/HGBS_ic5146_column_density_map.fits.gz',
                          'http://www.herschel.fr/cea/gouldbelt/en/Phocea/file.php?class=astimg&file=66/HGBS_lupI_column_density_map.fits.gz',
                          'http://www.herschel.fr/cea/gouldbelt/en/Phocea/file.php?class=astimg&file=66/HGBS_lupIII_column_density_map.fits.gz',
                          'http://www.herschel.fr/cea/gouldbelt/en/Phocea/file.php?class=astimg&file=66/HGBS_lupIV_column_density_map.fits.gz',
                          'http://www.herschel.fr/Phocea/file.php?class=astimg&file=66/HGBS_musca_column_density_map.fits.gz',
                          'http://www.herschel.fr/Phocea/file.php?class=astimg&file=66/HGBS_oph_l1688_column_density_map.fits.gz',
                          'http://www.herschel.fr/Phocea/file.php?class=astimg&file=66/HGBS_orionA_column_density_map.fits.gz',
                          'http://www.herschel.fr/Phocea/file.php?class=astimg&file=66/HGBS_orionB_column_density_map.fits.gz',
                          'http://www.herschel.fr/cea/gouldbelt/en/Phocea/file.php?class=astimg&file=66/HGBS_perseus_column_density_map.fits.gz',
                          'http://www.herschel.fr/Phocea/file.php?class=astimg&file=66/HGBS_pipe_column_density_map.fits.gz',
                          'http://www.herschel.fr/Phocea/file.php?class=astimg&file=66/HGBS_polaris_column_density_map.fits.gz',
                          'http://www.herschel.fr/Images/astImg/66/HGBS_taurus_L1495_column_density_map.fits.gz',
                          'http://www.herschel.fr/cea/gouldbelt/en/Phocea/file.php?class=astimg&file=66/HGBS_serpens_column_density_map.fits.gz']

rmcatalogue_urls = ['https://cdsarc.cds.unistra.fr/ftp/J/ApJ/702/1230/catalog.dat.gz',
                    'https://github.com/CIRADA-Tools/RMTable/raw/master/consolidated_catalog_ver1.0.1.tsv.zip']
#Get the column density maps.
columndensities = download_files(density_fits_file_urls, config.dir_data)
columndensities = unzip_gzs(columndensities)
#Get the rotation catalogue (Taylor 2009)
rmcatalogues = download_files(rmcatalogue_urls, config.DataRMCatalogDir)
unzip(rmcatalogues)
CameronToTaylorFormat(os.path.join(config.DataRMCatalogDir, 'consolidated_catalog_ver1.0.1.tsv'))
rmcatalogues = unzip_gzs(rmcatalogues)
#Append the appropriate header to the rotation measure catalogue (Taylor 2009)
addHeader(rmcatalogues[0], os.path.join(config.DataRMCatalogDir, 'RMCatalogueHeader.csv'))