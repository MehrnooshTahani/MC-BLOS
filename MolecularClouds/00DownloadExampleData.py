import os
import gzip
import shutil
import requests

import pandas as pd

import LocalLibraries.config as config

def download_files(urls, dir):
    outputs = []
    for url in urls:
        # Information
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

def unzip_gzs(files_in):
    files = [file for file in files_in if file.endswith('.gz')]
    outputs = []
    for file in files:
        # Information
        print("Unzipping: {}".format(file))
        # Unzip
        with gzip.open(file, 'rb') as file_in:
            with open(file.removesuffix('.gz'), 'wb') as file_out:
                shutil.copyfileobj(file_in, file_out)
                outputs.append(file.removesuffix('.gz'))
    return outputs

def addHeader(headerless_file, headerfile):
    headerless = pd.read_csv(headerless_file, delim_whitespace=True, header=None)
    header = pd.read_csv(headerfile, delim_whitespace=True)
    headerless.set_axis(header.columns, axis=1, inplace=True)
    headerless.to_csv(headerless_file, index=False, sep=config.dataSeparator)

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
rmcatalogue_urls = ['https://cdsarc.cds.unistra.fr/ftp/J/ApJ/702/1230/catalog.dat.gz']

columndensities = download_files(density_fits_file_urls, config.dir_data)
columndensities = unzip_gzs(columndensities)

rmcatalogues = download_files(rmcatalogue_urls, config.DataRMCatalogDir)
rmcatalogues = unzip_gzs(rmcatalogues)

addHeader(rmcatalogues[0], os.path.join(config.DataRMCatalogDir, 'RMCatalogueHeader.csv'))