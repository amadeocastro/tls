import numpy
import batman
from transitleastsquares import transitleastsquares


# Test case for statistics when data contains gap during a transit

if __name__ == "__main__":
    print("Starting test: Gap in test statistic...", end='')
    numpy.random.seed(seed=0)  # reproducibility
    # Create test data
    start = 48
    days = 365.25 * 3
    samples_per_day = 12  # 48
    samples = int(days * samples_per_day)  # 48
    t = numpy.linspace(start, start + days, samples)

    # Use batman to create transits
    ma = batman.TransitParams()
    ma.t0 = (start + 20)
    ma.per = 365.25  # orbital period
    ma.rp = 6371 / 696342  # 6371 planet radius (in units of stellar radii)
    ma.a = 217  # semi-major axis (in units of stellar radii)
    ma.inc = 90  # orbital inclination (in degrees)
    ma.ecc = 0  # eccentricity
    ma.w = 90  # longitude of periastron (in degrees)
    ma.u = [0.5]  # limb darkening coefficients
    ma.limb_dark = "linear"  # limb darkening model
    m = batman.TransitModel(ma, t)  # initializes model
    original_flux = m.light_curve(ma)  # calculates light curve

    # Create noise and merge with flux
    ppm = 5
    stdev = 10 ** -6 * ppm
    noise = numpy.random.normal(0, stdev, int(samples))
    y = original_flux + noise
    y[1] = numpy.nan

    #print(len(y))
    y[200:500] = numpy.nan
    t[200:500] = numpy.nan
    #import matplotlib.pyplot as plt
    #plt.plot(t, y)
    #plt.show()

    model = transitleastsquares(t, y)
    results = model.power(
        period_min=360,
        period_max=370,
        transit_depth_min=10 * 10 ** -6,
        oversampling_factor=2,
        duration_grid_step=1.1,
        T0_fit_margin=1.2
    )

    numpy.testing.assert_almost_equal(results.period_uncertainty, 0.3153203546531813, decimal=5)
    numpy.testing.assert_equal(results.per_transit_count, [0, 5, 5])
    numpy.testing.assert_equal(len(results.transit_times), 3)
    numpy.testing.assert_almost_equal(results.period, 365.22218620040417, decimal=5)
    numpy.testing.assert_almost_equal(
        results.transit_times,
        [68.06015495259413, 433.2823411529983, 798.5045273534024],
        decimal=5
        )

    numpy.testing.assert_almost_equal(results.depth, 0.9998972750356973, decimal=5)
    numpy.testing.assert_almost_equal(results.duration, 0.41082005564431956, decimal=5)
    numpy.testing.assert_almost_equal(results.SDE, 4.471095518473202, decimal=5)
    numpy.testing.assert_almost_equal(
        results.odd_even_mismatch, 0.15219910861779098, decimal=5
    )
    numpy.testing.assert_almost_equal(results.rp_rs, 0.009114758081257387, decimal=5)

    # Full light curve model
    numpy.testing.assert_almost_equal(
        numpy.sum(results.model_lightcurve_time), 38276049.947393775, decimal=5)
    numpy.testing.assert_almost_equal(
        numpy.sum(results.model_lightcurve_model), 64234.99399704611, decimal=5)

    transit_times_expected = [68.06015495259413, 433.2823411529983, 798.5045273534024]
    numpy.testing.assert_almost_equal(
        results.transit_times, transit_times_expected, decimal=5)
    numpy.testing.assert_almost_equal(results.duration, 0.41082005564431956, decimal=5)

    numpy.testing.assert_almost_equal(
        max(results.model_folded_phase), 1.0000380285975052, decimal=5)
    numpy.testing.assert_almost_equal(
        min(results.model_folded_phase), 3.8028597505324e-05, decimal=5)
    numpy.testing.assert_almost_equal(
        numpy.mean(results.model_folded_phase), 0.5000380285975052, decimal=5)

    numpy.testing.assert_almost_equal(
        results.depth_mean_even, (0.999915, 6.785539e-06), decimal=5)
    numpy.testing.assert_almost_equal(
        results.depth_mean_odd, (0.999920, 1.209993e-05), decimal=5)
    numpy.testing.assert_almost_equal(
        results.depth_mean, (0.999917, 6.086923e-06), decimal=5)
    
    numpy.testing.assert_almost_equal(
        results.transit_depths, [numpy.nan, 0.99991, 0.9999], decimal=5)

    numpy.testing.assert_almost_equal(
        results.transit_depths_uncertainties, [numpy.nan, 2.92371e-06, 4.48803e-06], decimal=5)
    numpy.testing.assert_almost_equal(
        results.odd_even_mismatch, 0.15219910861779098, decimal=5)
    numpy.testing.assert_almost_equal(
        results.transit_count, 3, decimal=5)
    numpy.testing.assert_almost_equal(
        results.distinct_transit_count, 2, decimal=5)
    numpy.testing.assert_almost_equal(
        results.empty_transit_count, 1, decimal=5)
    numpy.testing.assert_almost_equal(
        results.snr_per_transit, [0 ,37.05205333, 37.49345826], decimal=5)
    numpy.testing.assert_almost_equal(
        results.snr, 52.71163674786351, decimal=5)
    numpy.testing.assert_almost_equal(
        results.snr_pink_per_transit, [0, 45.47710446, 46.0188779 ], decimal=5)
    print('passed')
    