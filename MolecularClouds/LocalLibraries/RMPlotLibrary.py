import numpy as np
'''
Contains plots or plot element functions utilized in relation to plotting rotation measure data.
'''
# -------- FUNCTION DEFINITION --------
def rm2RGB(rm):
    """
    Takes rotation measure values and assigns them a marker colour and size for use in plotting rotation measure data

    :param rm: The rotation measure, or list of rotation measures
    :return:  A tuple of (colour, size) corresponding to the rotation measure. Note "colour" is a tuple of (RBG,alpha)
    """
    c = []  # Marker colour
    s = []  # Marker size

    for item in rm:
        s.append(abs(item))

        alpha = 1  # Optional: set the transparency
        if int(np.sign(item)) == -1:
            c.append((1, 0, 0, alpha))  # Negative rotation measures assigned red
        elif int(np.sign(item)) == 1:
            c.append((0, 0, 1, alpha))  # Positive rotation measures assigned blue
        elif np.sign(item) == 0:
            c.append((0, 1, 0, alpha))  # Zero-value rotation measures assigned green

    # return the list of RGBA tuples and sizes
    return c, s
# -------- FUNCTION DEFINITION. --------

# -------- FUNCTION DEFINITION --------
def rm2G(rm, alpha = 1):
    """
    Takes rotation measure values and assigns them a marker colour and size for use in plotting rotation measure data

    :param rm: The rotation measure, or list of rotation measures
    :return:  A tuple of (colour, size) corresponding to the rotation measure. Note "colour" is a tuple of (RBG,alpha)
    """
    c = []  # Marker colour
    s = []  # Marker size

    c = [(0, 1, 0, alpha) for i in range(len(rm))]
    s = np.abs(rm)

    # return the list of RGBA tuples and sizes
    return c, s
# -------- FUNCTION DEFINITION. --------