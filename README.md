# Build a HAWKI ETC

[![Python package](https://github.com/cylammarco/ETC_HomeWork/actions/workflows/python-test.yml/badge.svg)](https://github.com/cylammarco/ETC_HomeWork/actions/workflows/python-test.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Current implementation is not installable, but the struture is as close to installable as possible. The test, shell and example script can only run at the top level directory (where you find this script). Run the example script with

```python
python example_script.py
```

It only works when there is internet connection because of the sky brightness calculation.

Explicit third-party dependencies: `astropy`,  `HowManyPhotons`, `matplotlib`, `numpy` and `scopesim`.

Example ETC output at 50-percentile obsering condition, which has a seeing of 0.8:

![alt text](https://github.com/cylammarco/ETC_HomeWork/blob/main/etc.png?raw=true)

### User Story

*Kieran wants to study the initial mass function of an open cluster in the Large Magellanic Cloud.
He plans to use the HAWK-I instrument on the VLT and would like to know what the faintest stars are that will be detectable (S/N > 5) with 1 hour of observing time in the K filter.
He assumes average (50th percentile) observing conditions will apply for the observation*

### Deliverable

The goal of this exercise is to build a -**very**- simple exposure time calculator (ETC) module in Python for the [HAWK-I imager instrument on the VLT](https://www.eso.org/sci/facilities/paranal/instruments/hawki.html).
The only conditions for how to implement the ETC are:

- written in Python >=3.7
- the ETC function or class must be importable by other scripts (i.e. a function or class)
- a test suite is included in a separate file (e.g. `test_etc.py`)

If you make any simplifying assumptions during the coding process, please document these in comments so that the reason for the assumption isn't lost to the sands of time.

### Hints

The aim of this exercise is to demonstrate coding style, not to showcase radiometric talents.
Therefore, it' is perfectly fine to make use of the radiometric-gymnastics package: [How Many Photons](https://pypi.org/project/HowManyPhotons/)

For comparing results, you may want to use the official [ESO HAWK-I ETC](https://www.eso.org/observing/etc/bin/gen/form?INS.NAME=HAWK-I+INS.MODE=imaging).
