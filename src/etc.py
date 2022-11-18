#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Body of the exposure time calculation"""

from functools import partial

from astropy import units
import hmbp
from matplotlib import pyplot as plt
import numpy as np
from scopesim.effects import ter_curves_utils as tcu


class HawkIExposureTimeCalculator:
    """
    This is a class for creating an exposure time calculator for Hawk-I. It is
    currently applicable to point source and aperture photometry only."""

    def __init__(self):

        self.observatory = "Paranal"
        self.instrument = "HAWKI"

        # assuming 20% obstructed -> factor of 0.8
        # assuming 85% reflectance -> factor of 0.85
        # see https://eso.org/sci/libraries/SPIE2018/10704-3.pdf
        self.collection_area = (4.0 * units.m) ** 2.0 * np.pi * 0.8 * 0.85

        # self.saturation_limit = 120000
        # self.lineraity_limit = 100000
        # self.peak_count = None

        # Taken from https://www.eso.org/sci/facilities/paranal/instruments/
        # hawki/inst.html
        #
        # Here we treat pixel as a length unit and pixel^2 as a square
        # pixel for appropriate unit conversion.
        #
        # In each pixel
        self.pixel_scale = 0.1063 * units.arcsec / units.pixel
        self.dark_current = (
            0.01 * units.electron / units.second / units.pixel**2
        )
        self.read_noise = 5.0 * units.electron / units.pixel**2
        # self.gain = 1.80 * units.electron

        self.filter_name = None
        self.brightness_list = None
        self.dit = None
        self.ndit = None
        self.exposure_time = None
        self.seeing = None
        self.airmass = None
        self.observating_condition_kwargs = None

        self.n_pix = None
        self.aper = None
        self.signal_aper = None
        self.sky_aper = None
        self.dark_aper = None
        self.read_noise_aper = None
        self.total_noise_aper = None
        self.snr_aper = None

        # https://www.eso.org/sci/facilities/paranal/instruments/hawki/doc/
        # VLT-MAN-ESO-14800-3486_v104.pdf
        # also assuming hmbp accounts for all the filter loss since it is
        self.quantum_efficiency = 0.9 * units.electron / units.ph

        self.supported_filters = [
            "Y",
            "NB1060",
            "NB1190",
            "J",
            "CH4",
            "H",
            "NB2090",
            "H2",
            "Ks",
            "BrGamma",
        ]

        self.signal = None
        self.sky = None
        self.snr = None

        self.for_flux_in_filter = partial(
            hmbp.for_flux_in_filter,
            instrument=self.instrument,
            observatory=self.observatory,
        )

        self.in_skycalc_background = partial(
            hmbp.in_skycalc_background,
            instrument=self.instrument,
            observatory=self.observatory,
        )

    def _get_filter_wavelength_limits(self):
        """Get the filter wavelength limits"""

        svo_str = f"{self.observatory}/{self.instrument}.{self.filter_name}"
        filt = tcu.download_svo_filter(svo_str)
        _wave = filt._model.points[0]
        _throughput = filt.model.lookup_table

        # Only get the range of filter where the throughput is >20%
        mask = _throughput > 0.2
        filter_min = min(_wave[mask]) * units.AA
        filter_max = max(_wave[mask]) * units.AA

        return filter_min, filter_max

    def _get_target_flux_in_filter(self, brightness_list):
        """Get the target flux in the filter provided"""

        n_photon_list = []
        for brightness in brightness_list:
            # brightness unit handled by hmbp
            n_photon = self.for_flux_in_filter(self.filter_name, brightness)
            n_photon_list.append(n_photon)

        return n_photon_list

    def _get_sky_flux_in_filter(self, **kwargs):
        """Get the sky background flux in the filter provided"""

        # Get an approximation of the wavelength limits of the given filter
        wave_min, wave_max = self._get_filter_wavelength_limits()

        # convert from Angstrom to nm
        skycal_kwargs = {
            "wmin": wave_min.to(units.nm).value,
            "wmax": wave_max.to(units.nm).value,
        }
        skycal_kwargs.update(kwargs)

        # brightness unit handled by hmbp
        n_photon = self.in_skycalc_background(
            self.filter_name, **skycal_kwargs
        )

        return n_photon

    def set_observing_condition(self, seeing, **kwargs):
        """
        See

        https://www.eso.org/observing/etc/doc/skycalc/helpskycalccli.html

        for the additional sky condition parameters (e.g. moon, zodiacal
        light, airglow...)

        Parameters
        ----------
        seeing: numeric or Quantity
            The seeing during the observation
        **kwargs:
            Other keyword arguments for skycalc (see link in description)

        """

        if isinstance(seeing, (int, float)):

            self.seeing = seeing * units.arcsec

        elif isinstance(seeing, units.Quantity):

            self.seeing = seeing

        # diameter twice the Image Quality FWHM
        # approximate seeing to FWHM -> radius = seeing
        # See https://www.eso.org/observing/etc/doc/helphawki.html#seeing
        # for more accurate estimation
        # apaerture area [arcsec2]
        self.aper = np.pi * (self.seeing) ** 2.0

        if "airmass" in kwargs:

            self.airmass = kwargs["airmass"]

        self.observating_condition_kwargs = kwargs

    def get_snr(self, filter_name, brightness, ndit, dit):
        """Get the flux from mag

        Parameters
        ----------
        filter_name: str
            One of
               1. Y
               2. NB1060
               3. NB1190
               4. J
               5. CH4
               6. H
               7. NB2090
               8. H2
               9. Ks
               10. BrGamma
        brightness: float, astropy.Quantity (or list of them)
            One of vega mag (astropy.units.mag), AB mag (astropy.units.ABmag)
            or Jansky (astropy.units.Jy). If float, Vega mag is assumed.
        ndit: integer
            Number of frames
        dit: float or astropy.Quantity
            Exposure time per frame

        Returns
        -------
        snr: float
            The signal-to-noise ratio

        """

        if filter_name not in self.supported_filters:

            raise ValueError(
                f"{filter_name} is not available with HAWK-I, please choose "
                f"from {self.supported_filters}."
            )

        else:

            self.filter_name = filter_name

        # Brightness unit will be handled by hmbp
        self.brightness_list = np.asarray(brightness).reshape(-1)

        if isinstance(dit, (float, int)):

            self.dit = dit * units.second

        elif isinstance(dit, units.Quantity):

            if dit.unit.physical_type == "time":

                self.dit = dit.to(units.second)

            else:

                raise TypeError(
                    f"dit unit has to be of type time, {dit.unit} of type "
                    f"{dit.unit.physical_type} is given."
                )

        else:

            raise ValueError(
                f"dit has to be numeric or a Qunatity. {dit} is given."
            )

        self.ndit = ndit
        self.exposure_time = self.dit * self.ndit

        # ASSUMING signal is returned in the unit of [ph s-1 m-2]
        # and sky is returned in the unit of [ph s-1 m-2 arcsec-2]
        # as the signal is purely local calculation but the sky is a remote
        # computation coming with a warning of the unit of extra
        # arcsec-2 needed.

        # ph -> e : quantum efficiency
        # e -> data number : gain

        # returning in the unit of [e]
        self.signal = [
            i
            * self.collection_area
            * self.quantum_efficiency
            * self.exposure_time
            for i in self._get_target_flux_in_filter(self.brightness_list)
        ]

        # returning in the unit of [e]
        # Using .value on aper because the returned quantity is
        # missing the unit of arcsec-2
        self.sky = self._get_sky_flux_in_filter(
            **self.observating_condition_kwargs
        )
        self.sky_aper = (
            self.sky
            * self.quantum_efficiency
            * self.exposure_time
            * self.collection_area
            * self.aper.value
        )

        # number of pixels within aperture
        self.n_pix = self.aper / self.pixel_scale**2.0

        # dark current within the aperture
        self.dark_aper = self.dark_current * self.n_pix * self.exposure_time

        # read noise within the aperture
        self.read_noise_aper = self.read_noise**2 * self.n_pix * self.ndit

        # signal within the aperture
        self.signal_aper = np.array([i.value for i in self.signal])

        # total noise
        self.total_noise_aper = np.sqrt(
            (
                self.signal_aper
                + self.sky_aper.value
                + self.dark_aper.value
                + self.read_noise_aper.value
            )
        )

        # signal-to-noise
        self.snr_aper = self.signal_aper / self.total_noise_aper

        # Create a simple 2D gaussian profile to approximate the
        # peak brightness to check for linearity and saturation
        # It is meaningless to compare against an averaged count.

        return self.snr_aper

    def print_summary(self):
        """Print the execute summary"""

        print("Statistics (all values are the sum inside the aperture)")
        print("")
        print(f"Number of pixels : {self.n_pix}")
        print(f"Source signal: {self.signal_aper}")
        print(f"Sky background: {self.sky_aper}")
        print(f"Dark Current: {self.dark_aper}")
        print(f"Readnoise: {self.read_noise_aper}")
        print("")
        print(f"Signal-to-Noise: {self.snr_aper}")

    def plot(self, snr=None, savefig=False, filename="etc.png"):
        """Create a basic plot of SNR as a function of birghtness"""
        fig = plt.figure()
        plt.scatter(self.brightness_list, self.snr_aper, s=5, color="black")
        if isinstance(snr, (float, int, list, np.ndarray)):
            plt.hlines(
                snr, min(self.brightness_list), max(self.brightness_list)
            )
        plt.xlim(min(self.brightness_list), max(self.brightness_list))
        plt.xlabel("Brightness")
        plt.ylabel("SNR")
        plt.yscale("log")
        plt.tight_layout()
        plt.grid()
        if savefig:
            if isinstance(filename, str):
                plt.savefig(filename)
            else:
                raise TypeError(
                    f"filename has to be a string, {type(filename)} is given."
                )
        plt.show()
        return fig
