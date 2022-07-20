import numpy as np
'''
Contains plots or plot element functions utilized in relation to plotting rotation measure data.
'''
# -------- FUNCTION DEFINITION --------
def p2RGB(values, size_cap = 1000, scale_factor = 1.0, alpha = 1.0):
    """
    Takes values and assigns them a marker colour and size for use in plotting. Red for negative, blue for positive.

    :param rm: The value, or list of values.
    :return:  A tuple of (colour, size) corresponding to the rotation measure. Note "colour" is a tuple of (RBG,alpha)
    """
    c = [(1, 0, 0, alpha) if item < 0 # Negative rotation measures assigned red
            else (0, 0, 1, alpha) if item > 0 # Positive rotation measures assigned blue
            else (0, 1, 0, alpha) # Zero-value rotation measures assigned green
            for item in values]  # Marker colour
    s = [abs(item)*scale_factor if item < size_cap else abs(size_cap)*scale_factor for item in values]

    return c, s
# -------- FUNCTION DEFINITION. --------

# -------- FUNCTION DEFINITION --------
def p2C(values, colour = (0, 1, 0), size_cap = 1000, scale_factor = 1.0, alpha = 1.0):
    """
    Takes rotation measure values and assigns them the green colour and a size for use in plotting rotation measure data

    :param rm: The rotation measure, or list of rotation measures
    :return:  A tuple of (colour, size) corresponding to the rotation measure. Note "colour" is a tuple of (RBG,alpha)
    """

    c = [(colour[0], colour[1], colour[2], alpha) for _ in range(len(values))]
    s = [abs(item)*scale_factor if item < size_cap else abs(size_cap)*scale_factor for item in values]

    # return the list of RGBA tuples and sizes
    return c, s
# -------- FUNCTION DEFINITION. --------