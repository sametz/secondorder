"""A test model consisting of a simple function."""

import numpy as np


def powerplot(base, exponent):
    """
    Calculates data points for plotting the function: y = (base * x) ** exponent
    Arguments: base and exponent as floats
    Returns: two numpy arrays of x and y coordinates.
    """
    x = np.linspace(0, 10, 800)
    y = (x * base) ** exponent
    return x, y
