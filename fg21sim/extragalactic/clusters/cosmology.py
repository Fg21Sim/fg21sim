# Copyright (c) 2016-2017 Weitian LI <liweitianux@live.com>
# MIT license

"""
Flat ΛCDM cosmological model.
"""

import logging

import numpy as np
from scipy import integrate
import astropy.units as au
from astropy.cosmology import LambdaCDM, z_at_value


logger = logging.getLogger(__name__)


class Cosmology:
    """
    Flat ΛCDM cosmological model.

    Attributes
    ----------
    H0 : float
        Hubble parameter at present day (z=0)
    Om0 : float
        Density parameter of (dark and baryon) matter at present day
    Ob0 : float
        Density parameter of baryon at present day
    Ode0 : float
        Density parameter of dark energy at present day
    sigma8 : float
        Present-day rms density fluctuation on a scale of 8 h^-1 Mpc.

    References
    ----------
    [1] https://astro.uni-bonn.de/~pavel/WIKIPEDIA/Lambda-CDM_model.html
    [2] https://en.wikipedia.org/wiki/Lambda-CDM_model
    [3] Randall, Sarazin & Ricker 2002, ApJ, 577, 579
        http://adsabs.harvard.edu/abs/2002ApJ...577..579R
        Sec.(2)
    """
    def __init__(self, H0=71.0, Om0=0.27, Ob0=0.046, Ode0=None, sigma8=0.834):
        Ode0 = 1.0 - Om0 if Ode0 is None else Ode0
        if (Ode0 > 0) and abs(Om0 + Ode0 - 1) > 1e-5:
            raise ValueError("non-flat LambdaCDM model not supported!")
        self.H0 = H0  # [km/s/Mpc]
        self.Om0 = Om0
        self.Ob0 = Ob0
        self.Ode0 = Ode0
        self.sigma8 = sigma8
        self.cosmo = LambdaCDM(H0=H0, Om0=Om0, Ob0=Ob0, Ode0=Ode0)

    @property
    def h(self):
        """
        Dimensionless/reduced Hubble parameter
        """
        return self.H0 / 100.0

    @property
    def M8(self):
        """
        Mass contained in a sphere of radius of 8 h^-1 Mpc.
        Unit: [Msun]
        """
        r = 8 * au.Mpc.to(au.cm) / self.h  # [cm]
        M8 = (4*np.pi/3) * r**3 * self.rho_crit(0)
        return (M8 * au.g.to(au.solMass))

    def age(self, z):
        """
        Cosmic time at redshift z.

        Parameters
        ----------
        z : float
            Redshift

        Returns
        -------
        age : float
            Age of the universe (cosmic time) at the given redshift.
            Unit: [Gyr]
        """
        return self.cosmo.age(z).value

    @property
    def age0(self):
        """
        Present age of the universe.
        """
        if not hasattr(self, "_age0"):
            self._age0 = self.age(0)
        return self._age0

    def redshift(self, age):
        """
        Invert the above age calculation, to return the redshift
        corresponding to the given cosmic time.

        Parameters
        ----------
        age : float
            Age of the universe (cosmic time), unit [Gyr]

        Returns
        -------
        z : float
            Redshift corresponding to the input age.
        """
        return z_at_value(self.age, age)

    def rho_crit(self, z):
        """
        Critical density at redshift z.
        Unit: [g/cm^3]
        """
        return self.cosmo.critical_density(0).value

    def OmegaM(self, z):
        """
        Density parameter of matter at redshift z.
        """
        return self.Om0 * (1+z)**3 / self.cosmo.efunc(z)**2

    def overdensity_virial(self, z):
        """
        Calculate the virial overdensity, which generally used to
        determine the virial radius of a cluster.

        References
        ----------
        [1] Cassano & Brunetti 2005, MNRAS, 357, 1313
            http://adsabs.harvard.edu/abs/2005MNRAS.357.1313C
            Eqs.(10,A4)
        """
        omega_z = (1 / self.OmegaM(z)) - 1
        Delta_c = 18*np.pi**2 * (1 + 0.4093 * omega_z**0.9052)
        return Delta_c

    def overdensity_crit(self, z):
        """
        Critical (linear) overdensity for a region to collapse
        at a redshift z.

        References
        ----------
        [1] Randall, Sarazin & Ricker 2002, ApJ, 577, 579
            http://adsabs.harvard.edu/abs/2002ApJ...577..579R
            Appendix.A, Eq.(A1)
        """
        coef = 3 * (12*np.pi) ** (2/3) / 20
        D0 = self.growth_factor(0)
        D_z = self.growth_factor(z)
        Om_z = self.OmegaM(z)
        delta_c = coef * (D0 / D_z) * (1 + 0.0123*np.log10(Om_z))
        return delta_c

    def growth_factor(self, z):
        """
        Growth factor at redshift z.

        References
        ----------
        [1] Randall, Sarazin & Ricker 2002, ApJ, 577, 579
            http://adsabs.harvard.edu/abs/2002ApJ...577..579R
            Appendix.A, Eq.(A7)
        """
        x0 = (2 * self.Ode0 / self.Om0) ** (1/3)
        x = x0 / (1 + z)
        coef = np.sqrt(x**3 + 2) / (x**1.5)
        integral = integrate.quad(lambda y: y**1.5 * (y**3+2)**(-1.5),
                                  a=0, b=x)[0]
        D = coef * integral
        return D
