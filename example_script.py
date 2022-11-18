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
    # 50-percentile obsering condition has a seeing of 0.8"
    hawki.set_observing_condition(seeing=0.8)
    hawki.get_snr(FILTER_NAME, brightness=mag, ndit=NDIT, dit=DIT)
    hawki.print_summary()
    hawki.plot(snr=[5], savefig=True)


if __name__ == "__main__":
    main()
