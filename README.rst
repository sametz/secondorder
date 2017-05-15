secondorder (pre-alpha)
***********************

**secondorder** will graphically simulate the NMR spectra for any number of coupled
spin-1/2 nuclei. The simulation requires the chemical shifts for all
nuclei, and all J coupling constants. The code has been tested for up to 8
spin-1/2 nuclei, but the only limitations should be computer memory,
processing time, and the screenspace required to enter all of the simulation
data.

The primary goal of the project is to provide a free, open-source spectrum
simulator suitable for educators as well as researchers (although the latter
are more likely to have access to proprietary software such as MNova that can
perform similar simulations).

A secondary, (overly?)ambitious goal is to provide code and documentation of
sufficient quality that it can serve as a tutorial for others on how to
simulate NMR spectra. The author is an organic chemist, not an NMR spectroscopist, and is
learning the required quantum mechanics "from scratch". I hope to improve my
understanding of the quantum mechanical foundation of NMR to the point where
I could explain it to another organic chemist.

Installation and Use
====================

The project is pre-alpha and subject to change. The master branch should
maintain a functional program. If you're curious, and have a Python 3
installation, you can download the project folders, install the requirements in requirements.txt if necessary, and run main.py from the command line.

Feedback
========

I welcome feedback on this project. Feel free to leave an issue on Github, or
contact me by email (mylastname at udel dot edu).

Acknowledgements
================

This project is inspired by Hans Reich's WINDNMR application. **secondorder**
initializes its simulations with the same variables as WINDNMR's defaults,
to verify that the simulation is performing correctly (since formal unit
testing is not implemented yet, hence the pre-alpha status).