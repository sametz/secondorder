"""
Functions for converting the simlated spectra from nmrmath into
lineshapes for plotting.
"""

#import matplotlib.pyplot as plt
import numpy as np


def lorentz(v, v0, I, w):
    """
    A lorentz function that takes linewidth at half intensity (w) as a
    parameter.
    :param v: Array of values at which to evaluate distribution.
    :param v0: Center of the distribution.
    :param w: Peak width at half max intensity

    :returns: Distribution evaluated at points in x.
    """
    return I * ((0.5 * w) ** 2 / ((0.5 * w) ** 2 + (v - v0) ** 2))


def add_signals(linspace, peaklist, w):
    """
    Given a numpy linspace a spectrum as a list of (frequency, intensity)
    tuples, and a linewidth, returns an array of y coordinates for the
    lineshape.

    :param linspace: a numpy linspace of x coordinates for the lineshape.
    :param peaklist: a list of (frequency, intensity) tuples
    :param w: peak width at half maximum intensity
    :returns: array of y coordinates for the lineshape
    """
    result = lorentz(linspace, peaklist[0][0], peaklist[0][1], w)
    for v, i in peaklist[1:]:
        result += lorentz(linspace, v, i, w)
    return result



# scheduled for deletion
# def lorentz2(v, v0, I, Q=1):
#     """
#     Modified Lorentzian function. T2 replaced by separate inputs for intensity
#     and line width.
#     :param v:  the current frequency being calculated (x coordinate)
#     :param v0: the exact frequency of the signal that is
#         being converted to a Lorentzian distribution
#     :param I:  max intensity
#     :param Q:  fudge factor for line width (defaults to 1)
#     """
#     pi = np.pi
#     return I / (pi * (1 + (Q**2) * ((v - v0)**2)))
#
#
# def adder(x, plist, Q=2):
#     """
#     :param x: the x coordinate (relative frequency in Hz)
#     :param plist: a list of tuples of peak data (frequency, intensity)
#     :param Q: the line width "fudge factor" used by lorentz2
#     returns: the sum of the peak Lorentzian functions at x
#     """
#     total = 0
#     for v, i in plist:
#         total += lorentz2(x, v, i, Q)
#     return total
#
#
# def tkplot_old(spectrum, y=4):
#     spectrum.sort()
#     r_limit = spectrum[-1][0] + 50
#     l_limit = spectrum[0][0] - 50
#     x = np.linspace(l_limit, r_limit, 2400)
#     y = adder(x, spectrum, Q=y)
#     return x, y


def tkplot(spectrum, w=0.5):
    spectrum.sort()
    r_limit = spectrum[-1][0] + 50
    l_limit = spectrum[0][0] - 50
    x = np.linspace(l_limit, r_limit, 2400)
    y = add_signals(x, spectrum, w)
    return x, y

# nmr plot function retained for now--may be useful for tests.

# def nmrplot(spectrum, y=1):
#     """
#     A no-frills routine that plots spectral simulation data.
#     :param spectrum: A list of (frequency, intensity) tuples
#     :param y: max intensity
#     """
#     spectrum.sort()  # Could become costly with larger spectra
#     l_limit = spectrum[0][0] - 50
#     r_limit = spectrum[-1][0] + 50
#     x = np.linspace(l_limit, r_limit, 800)
#     plt.ylim(-0.1, y)
#     plt.gca().invert_xaxis()  # reverses the x axis
#     # noinspection PyTypeChecker
#     plt.plot(x, adder(x, spectrum, Q=4))
#
#     plt.show()
#     return
