
# -*- coding: utf-8 -*-

"""The tests here only check that they run without raising error, it is not
checked against any (un)known results."""

from astropy import units
from src import etc
import numpy as np
from unittest.mock import patch

hawki = etc.HawkIExposureTimeCalculator()
hawki.set_observing_condition(seeing=1.3)


def test_float_input():
    '''test float'''
    hawki.get_snr('Ks', 10.0, ndit=60, dit=60)

def test_int_input():
    '''test int'''
    hawki.get_snr('Ks', 10, ndit=60, dit=60)

def test_abmag_input():
    '''test AB mag'''
    hawki.get_snr('Ks', 10.0 * units.ABmag, ndit=60, dit=60)

def test_vega_mag_input():
    '''test Vega mag'''
    hawki.get_snr('Ks', 10.0 * units.mag, ndit=60, dit=60)

def test_jansky_input():
    '''test Jansky'''
    hawki.get_snr('Ks', 10.0 * units.Jy, ndit=60, dit=60)

def test_list_of_float_input():
    '''test list of float'''
    hawki.get_snr('Ks', [10.0, 20.0], ndit=60, dit=60)

def test_array_of_float_input():
    '''test array of float'''
    hawki.get_snr('Ks', np.array([10.0, 20.0]), ndit=60, dit=60)

def test_summary():
    '''test printing executive summary to screen'''
    hawki.print_summary()

@patch("matplotlib.pyplot.show")
def test_plot(mock_show):
    hawki.plot()
