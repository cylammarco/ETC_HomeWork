#!/usr/bin/env python3
# # -*- coding: utf-8 -*-

"""An example script to use the ETC."""


import numpy as np

from src import etc


def main():
    # filter name
    FILTER_NAME = "Ks"
    # magnitudes of interest
    mag = np.linspace(10, 25, 1000)
    # number of frames
    NDIT = 60
    # exposure time per frame
    DIT = 60

    # Initialise
    hawki = etc.HawkIExposureTimeCalculator()
    hawki.set_observing_condition(seeing=1.3)
    hawki.get_snr(FILTER_NAME, brightness=mag, ndit=NDIT, dit=DIT)
    hawki.print_summary()
    hawki.plot(snr=[5, 10, 50], savefig=True)


if __name__ == "__main__":
    main()
