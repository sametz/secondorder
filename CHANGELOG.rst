##########
Change Log
##########

All notable changes to this project will be documented in this file.

The format is inspired by `Keep a Changelog <http://keepachangelog.com/en/0.3.0/>`_ and tries to adhere to `Semantic Versioning <http://semver.org>`_. The author interprets the terms below as follows:

* **pre-alpha status**: the app runs, but there is no formal unit or functional testing.


* **alpha status**: pre-alpha, plus implementation of unit and functional tests.


* **beta status**: alpha, plus documentation, implementation of all anticipated Version 1.0.0 features, and installation requirements.


* **release candidate status**: beta, plus standalone executable(s) for Windows, Mac OS X, and Linux.


* **Version 1.0.0 release**: a minimal app suitable for educational use and not requiring execution from the command line interface.

0.4.0 - 2017-10-01 (alpha)
--------------------------

Added
^^^^^

* Linewidth ("W") variable implemented (on toolbar to the left of the "Enter Js" button)

* Implemented a "SpinBox" widget for numerical entries, with up/down arrows for incrementing/decrementing the value in the entry box

Known Issue
***********

The spectrum refresh lags behind spinbox changes by one click.
Focusing away from the changed entry should force a refresh.

Changed
^^^^^^^

Code was massively reorganized and refactored.

0.3.0 - 2017-07-26 (alpha)
--------------------------

Added
^^^^^

* tests/model/test_nmrmath.py and test_nmrplot.py to test the model's output against accepted results (stored in tests/model/accepted_data.py)

Changed
^^^^^^^

* Lorentzian refactored to take a parameter (w) for width of peak at half height, allowing future implementation of this parameter in the GUI.

* Refactored routine that computes the total spectrum by adding the Lorentzian lineshapes for each signal (model.nmrplot.add_signals).

0.2.0 - 2017-05-19 (pre-alpha)
------------------------------

Added
^^^^^

* Default values in initialize.py for 2-spin system

Changed
^^^^^^^

* 2-spin simulation changed from non-quantum mechanical calculation to quantum mechanical. GUI toolbar for 2-spin now consistent with those for 3+ spins.

* App refactored along model-view-controller design pattern.

Deleted
^^^^^^^

* Code relating to the non-Quantum mechanical calculation of 2-spin system (AB quartet), including GUI widgets

0.1.0 - 2017-05-15 (pre-alpha release)
--------------------------------------

Initial Commit
