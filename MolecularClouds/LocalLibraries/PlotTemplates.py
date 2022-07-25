'''
Contains common plots or plot elements utilized in various scriPoints
'''

import matplotlib.pyplot as plt
import adjustText
import math

from astropy.wcs import WCS

def extinctionPlot(hdu, regionOfInterest):
    '''

    :param hdu: The HDU contianing the image data that is to be plotted. HDU object.
    :param regionOfInterest: RegionOfInterest object which gives data on where and what part of the HDU is to be plotted. RegionOfInterest Object.
    :return: fig, ax - the figure and axis of the plot. Matplotlib objects.
    '''
    fig, ax, im = heatPlot(hdu)
    equatorialCoords(ax)
    overlayCoords(ax)
    colourbar(regionOfInterest, im)
    setBoundsIfValid(ax, regionOfInterest.xmin, regionOfInterest.xmax, regionOfInterest.ymin, regionOfInterest.ymax)

    return fig, ax

def heatPlot(hdu):
    '''
    Creates a heat plot for the given HDU.

    :param hdu: The HDU image file.
    :return: fig, ax, im: The figure, axis, and image of the plot. Matplotlib objects.
    '''
    wcs = WCS(hdu.header)

    fig = plt.figure(figsize=(8, 8), dpi=120, facecolor='w', edgecolor='k')
    ax = fig.add_subplot(111, projection=wcs)
    im = plt.imshow(hdu.data, origin='lower', cmap='BrBG', interpolation='nearest')

    return fig, ax, im

def equatorialCoords(ax):
    '''
    Overlays the given axes with equatorial coordinates.
    :param ax: The axis of the plot. Matplotlib axis object.
    :return: Nothing, it applies it to the axis.
    '''
    # ---- Style the main axes and their grid
    ra = ax.coords[0]
    dec = ax.coords[1]
    ra.set_major_formatter('d')
    dec.set_major_formatter('d')
    ra.set_axislabel('RA (degree)')
    dec.set_axislabel('Dec (degree)')

    dec.set_ticks(number=10)
    ra.set_ticks(number=20)
    ra.display_minor_ticks(True)
    dec.display_minor_ticks(True)
    ra.set_minor_frequency(10)

    ra.grid(color='black', alpha=0.5, linestyle='solid')
    dec.grid(color='black', alpha=0.5, linestyle='solid')
    # ---- Style the main axes and their grid.

def overlayCoords(ax):
    '''
    Overlays galactic coordinates onto the axis.
    :param ax: The axis of the plot. Matplotlib axis object.
    :return: Nothing, it applies it to the axis.
    '''
    # ---- Style the overlay and its grid
    overlay = ax.get_coords_overlay('galactic')

    overlay[0].set_axislabel('Longitude')
    overlay[1].set_axislabel('Latitude')

    overlay[0].set_ticks(color='grey', number=20)
    overlay[1].set_ticks(color='grey', number=20)

    overlay.grid(color='grey', linestyle='solid', alpha=0.7)
    # ---- Style the overlay and its grid.


def colourbar(regionOfInterest, im):
    '''
    Sets the colour bar on the image for our region of interest.
    :param regionOfInterest: Used to obtain data on the fits data type. RegionOfInterest object.
    :param im: The matplotlib image object to make a colour bar for.
    :return: cb - the pointer to the colourbar object.
    '''
    cb = None
    # ---- Style the colour bar
    if regionOfInterest.fitsDataType == 'HydrogenColumnDensity':
        cb = plt.colorbar(im, ticklocation='right', fraction=0.02, pad=0.145, format='%.0e')
        cb.ax.set_title('Hydrogen Column Density', linespacing=0.5, fontsize=12)
    elif regionOfInterest.fitsDataType == 'VisualExtinction':
        cb = plt.colorbar(im, ticklocation='right', fraction=0.02, pad=0.145)
        cb.ax.set_title(' A' + r'$_V$', linespacing=0.5, fontsize=12)
    # ---- Style the colour bar.
    return cb

def setBoundsIfValid(ax, xmin, xmax, ymin, ymax):
    '''
    Sets the axis bounds if the given bounds are valid bounds.
    :param ax: The axis of the plot. Matplotlib axis object.
    :param xmin: The desired x minimum bound. int.
    :param xmax: The desired x maximum bound. int.
    :param ymin: The desired y minimum bound. int.
    :param ymax: The desired y maximum bound. int.
    :return: Nothing, it applies it to the axis.
    '''
    if not math.isnan(xmax) and not math.isnan(xmin):
        ax.set_xlim(xmin, xmax)
    if not math.isnan(ymax) and not math.isnan(ymin):
        ax.set_ylim(ymin, ymax)

def labelPoints(ax, labels, xCoords, yCoords, size = 9, color = 'w', textFix = True):
    '''
    Labels points on a given graph given by the axis.

    :param ax: The axis of the plot. Matplotlib axis object.
    :param labels: A set of labels for the points. List.
    :param xCoords: A set of x coordinates denoting where the points are. List.
    :param yCoords: A set of y coordinates denoting where the points are. List.
    :param size: The size of the text. Integer.
    :param color: The colour of the text. String.
    :return: text: A list of matlotlib text objects pointing to each of the labels. List.
    '''
    # ---- Annotate the chosen reference points
    text = []
    for i, label in enumerate(labels):
        # Each point is labelled in order of increasing extinction value
        # To label with ID number use: txt = ax.text(x_AllRef[i], y_AllRef[i], str(number), size=9, color='w')
        # txt = ax.text(x_AllRef[i], y_AllRef[i], str(i + 1), size=9, color='w')
        txt = ax.text(xCoords[i], yCoords[i], label, size=size, color=color)
        text.append(txt)
    if textFix:
        adjustText.adjust_text(text)
    return text
    # ---- Annotate the chosen reference points