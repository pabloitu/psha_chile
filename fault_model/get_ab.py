import numpy as np
import geopandas as gpd
from shapely.geometry import LineString

from openquake.hazardlib import nrml
from openquake.hazardlib.sourceconverter import SourceConverter
# from openquake.hazardlib.mfd import EvenlyDiscretizedMFD  # optional if you want isinstance checks


def read_simple_fault_sources(nrml_path):
    """
    Read an NRML source model and return a list of SimpleFaultSource objects.

    Parameters
    ----------
    nrml_path : str or Path

    Returns
    -------
    list
        List of openquake.hazardlib.source.simple_fault.SimpleFaultSource
        instances.
    """
    model = nrml.read(nrml_path)
    ns = '{' + model.attrib['xmlns'] + '}'
    sm = model[0]

    # pick only <simpleFaultSource> nodes
    sf_nodes = []
    for src in sm[0]:
        if src.tag.split(ns)[1] == 'simpleFaultSource':
            sf_nodes.append(src)


    conv = SourceConverter()
    simple_fault_sources = [conv.convert_node(node) for node in sf_nodes if node]
    return simple_fault_sources

import numpy as np
import math


def fit_gr_from_incremental_mfd(mfd, n_years=1.0):
    """
    Fit Gutenberg–Richter a, b from an OpenQuake incremental MFD.

    We assume the MFD comes from an <incrementalMFD>:
      - mfd.min_mag   : center of first bin (Mw)
      - mfd.bin_width : bin width dM (Mw)
      - mfd.occurrence_rates : incremental rates per bin (typically per year)

    Steps:
      1) Fit log10(lambda_i) = a_incr - b * M_i  (incremental form)
      2) Convert to cumulative GR:
         log10 N(M >= m) = a_cum(1yr) - b * m
      3) Optionally scale a_cum to an N_years window:
         a_cum(N_years) = a_cum(1yr) + log10(N_years)

    Parameters
    ----------
    mfd : hazardlib MFD object
        Evenly-discretized incremental MFD.
    n_years : float, optional
        Time window for which you want the GR 'a' value.
        If n_years = 1.0 (default), 'a_cum_scaled' = 'a_cum_1yr'.
        If n_years = 50, you get a for a 50-year window.

    Returns
    -------
    dict
        {
          'a_incr'       : intercept in log10(lambda) = a_incr - b*M
          'a_cum_1yr'    : a for N(M>=m) per year
          'a_cum_scaled' : a for N(M>=m) over n_years
          'b'            : b-value
          'mmin'         : min magnitude used in fit
          'mmax'         : max magnitude used in fit
          'r2_log10'     : R^2 in log10 space for cumulative GR
          'rms_log10'    : RMS misfit (log10) for cumulative GR
        """
    # --- Extract bin centres and incremental rates ---
    min_mag = float(mfd.min_mag)
    dM = float(mfd.bin_width)
    rates = np.asarray(mfd.occurrence_rates, dtype=float)

    nbins = rates.size
    mags = min_mag + np.arange(nbins) * dM   # bin centres

    # Only fit bins with positive rates
    mask = rates > 0
    mags_fit = mags[mask]
    inc_fit = rates[mask]

    # --- 1) Fit incremental GR: log10(lambda) = a_incr - b*M ---
    x = mags_fit
    y = np.log10(inc_fit)

    # y = c0 + c1*x   =>  a_incr = c0,  b = -c1
    c1, c0 = np.polyfit(x, y, 1)
    b = -float(c1)
    a_incr = float(c0)

    # --- 2) Convert to cumulative GR (per YEAR) ---
    # For an underlying GR, incremental rate in bin of width dM is:
    #   lambda_i = 10^(a_cum - b*M_i) * (1 - 10^(-b*dM))
    # So:
    #   a_incr = a_cum + log10(1 - 10^(-b*dM))
    # => a_cum = a_incr - log10(1 - 10^(-b*dM))
    factor = 1.0 - 10.0 ** (-b * dM)
    if factor <= 0:
        raise RuntimeError("Invalid factor in GR conversion (check b, dM).")

    a_cum_1yr = a_incr - math.log10(factor)

    # --- 3) Scale 'a' to an N_years window (if desired) ---
    # N_T(M>=m) = T * N_1yr(M>=m) => a_T = a_1yr + log10(T)
    if n_years <= 0:
        raise ValueError("n_years must be positive.")
    a_cum_scaled = a_cum_1yr + math.log10(n_years)

    # --- Goodness-of-fit in cumulative space (optional diagnostics) ---
    # Cumulative rates (using the original incremental data)
    cum_rates = np.cumsum(inc_fit[::-1])[::-1]
    y_cum = np.log10(cum_rates)

    # Predicted cumulative GR (per YEAR) at the same mags
    N_pred = 10.0 ** (a_cum_1yr - b * mags_fit)
    y_pred = np.log10(N_pred)

    resid = y_cum - y_pred
    rms_log10 = float(np.sqrt(np.mean(resid ** 2)))

    ss_res = float(np.sum(resid ** 2))
    ss_tot = float(np.sum((y_cum - np.mean(y_cum)) ** 2))
    r2 = float(1.0 - ss_res / ss_tot) if ss_tot > 0 else np.nan

    return {
        "a_fit": a_incr,
        "a_cum_fit": a_cum_1yr,
        "b_fit": b,
        "mmin": float(mags_fit.min()),
        "mmax": float(mags_fit.max()),
        "r2_log10": r2,
        "rms_log10": rms_log10,
    }

import math  # you already import it above; if so, you can skip this line


# ---- NEW: geometry helpers + GR moment integration ----
import math  # you already import this above; ok if duplicated


# ---- Geometry + seismic moment from GR ----

def haversine_length_km(coords_lonlat):
    """
    Approximate fault trace length in km from lon/lat coordinates
    using a simple haversine formula.

    Parameters
    ----------
    coords_lonlat : sequence of (lon, lat) pairs in degrees.

    Returns
    -------
    float
        Total length in km.
    """
    R_km = 6371.0

    def seg_length(p1, p2):
        lon1, lat1 = map(math.radians, p1)
        lon2, lat2 = map(math.radians, p2)
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        h = (math.sin(dlat / 2.0) ** 2 +
             math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2.0) ** 2)
        return 2.0 * R_km * math.asin(math.sqrt(h))

    return sum(
        seg_length(coords_lonlat[i], coords_lonlat[i + 1])
        for i in range(len(coords_lonlat) - 1)
    )


def gr_seismic_moment_rate(
    a_cum_1yr,
    b,
    mmin,
    mmax,
    mw_c1=1.5,
    mw_c2=9.1,
):
    """
    Seismic moment rate (per YEAR) implied by a truncated GR MFD.

    We assume:
      log10 N(M >= m) = a_cum_1yr - b * m            (per year)
      log10 M0 = mw_c1 * M + mw_c2                  (N·m)

    And integrate M0(M) dN/dM from mmin to mmax.

    Returns
    -------
    float
        Seismic moment rate in N·m / yr.
    """
    if mmax <= mmin:
        raise ValueError("mmax must be > mmin.")

    k = mw_c1 - b  # exponent for 10^(kM)
    if abs(k) < 1e-8:
        raise ValueError("b is too close to mw_c1; use numerical integration in this edge case.")

    term = 10.0 ** (k * mmax) - 10.0 ** (k * mmin)

    # Closed-form integral:
    # Mdot = (b / (mw_c1 - b)) * 10^(a_cum_1yr + mw_c2) * (10^(k mmax) - 10^(k mmin))
    mdot = (b / (mw_c1 - b)) * (10.0 ** (a_cum_1yr + mw_c2)) * term
    return mdot


# ---- Tectonic moment + moment-balance a-value ----

def tectonic_moment_rate(
    length_km,
    upper_sd_km,
    lower_sd_km,
    dip_deg,
    slip_rate,
    slip_unit="mm/yr",
    shear_modulus=30e9,
    coupling=1.0,
):
    """
    Compute tectonic moment rate for a planar fault.

    Parameters
    ----------
    length_km : float
        Fault trace length (km).
    upper_sd_km, lower_sd_km : float
        Upper and lower seismogenic depths (km).
    dip_deg : float
        Dip angle (degrees).
    slip_rate : float
        Slip rate value.
    slip_unit : {'mm/yr', 'm/yr'}, optional
        Unit of slip_rate.
    shear_modulus : float, optional
        Shear modulus (Pa). Default 30e9.
    coupling : float, optional
        Seismic coupling coefficient χ. Default 1.

    Returns
    -------
    float
        Tectonic moment rate (N·m / yr).
    """
    if slip_unit == "mm/yr":
        slip_m_per_yr = slip_rate * 1e-3
    elif slip_unit == "m/yr":
        slip_m_per_yr = slip_rate
    else:
        raise ValueError("slip_unit must be 'mm/yr' or 'm/yr'.")

    thickness_km = lower_sd_km - upper_sd_km
    if thickness_km <= 0:
        raise ValueError("Non-positive seismogenic thickness.")
    width_km = thickness_km / math.sin(math.radians(dip_deg))

    L_m = length_km * 1e3
    W_m = width_km * 1e3

    mdot = shear_modulus * L_m * W_m * slip_m_per_yr * coupling
    return mdot


def a_from_moment_rate_truncated_gr(
    mdot,
    b,
    m_min,
    m_max,
    mw_c1=1.5,
    mw_c2=9.1,
):
    """
    Compute cumulative GR 'a' from a given moment rate for a truncated GR.

    Parameters
    ----------
    mdot : float
        Target (tectonic) moment rate in N·m / yr.
    b : float
        GR b-value.
    m_min, m_max : float
        Min and max magnitudes for the truncated GR.
    mw_c1, mw_c2 : float, optional
        Coeffs in log10(M0) = mw_c1*M + mw_c2.

    Returns
    -------
    float
        a_cum_1yr_mbal, such that the GR MFD conserves the given moment rate.
    """
    if mdot <= 0:
        raise ValueError("mdot must be positive.")
    if m_max <= m_min:
        raise ValueError("m_max must be > m_min.")

    k = mw_c1 - b
    if abs(k) < 1e-8:
        raise ValueError("b is too close to mw_c1; use numerical integration.")

    term = 10.0 ** (k * m_max) - 10.0 ** (k * m_min)
    if term <= 0:
        raise RuntimeError("Non-positive term in GR integral; check m_min/m_max/b.")

    # Invert the moment-rate formula:
    # mdot = (b / (mw_c1 - b)) * 10^(a + mw_c2) * term
    # => 10^(a + mw_c2) = mdot * (mw_c1 - b)/(b * term)
    # => a = log10(mdot) + log10(mw_c1 - b) - log10(b) - log10(term) - mw_c2
    a_cum = (
        math.log10(mdot)
        + math.log10(mw_c1 - b)
        - math.log10(b)
        - math.log10(term)
        - mw_c2
    )
    return a_cum


def fault_gr_summary(
    coords_lonlat,
    dip_deg,
    upper_sd_km,
    lower_sd_km,
    a_cum_1yr,
    b,
    mmin,
    mmax,
    n_years=1.0,
):
    """
    Summarize what the *existing GR MFD* implies for a fault.

    Parameters
    ----------
    coords_lonlat : sequence of (lon, lat) pairs (degrees).
        Fault trace coordinates from the simpleFaultGeometry.
    dip_deg : float
        Fault dip in degrees.
    upper_sd_km, lower_sd_km : float
        Upper and lower seismogenic depths (km).
    a_cum_1yr : float
        GR 'a' for the cumulative relation (per YEAR):
        log10 N(M >= m) = a_cum_1yr - b * m
        This should be the a_cum_1yr you just fit from the incremental MFD.
    b : float
        GR b-value, same one you got from the fit.
    mmin, mmax : float
        Minimum and maximum magnitudes for the truncated GR.
        Typically mmin = MFD minMag, mmax = max bin centre.
    n_years : float, optional
        Time span for which to compute total expected moment and events.
        Default is 1 year.

    Returns
    -------
    dict
        {
          'L_km'          : fault trace length (km),
          'W_km'          : down-dip width (km),
          'area_km2'      : L * W (km^2),
          'N_Mge_mmin_1yr': rate N(M >= mmin) per year,
          'N_Mge_mmin_T'  : expected N(M >= mmin) over n_years,
          'Mdot_e18_1yr'  : seismic moment rate in 1e18 N·m/yr,
          'M_e18_T'       : total moment over n_years in 1e18 N·m,
        }
    """
    if n_years <= 0:
        raise ValueError("n_years must be positive.")

    # Geometry
    L_km = haversine_length_km(coords_lonlat)
    thickness_km = lower_sd_km - upper_sd_km
    if thickness_km <= 0:
        raise ValueError("lower_sd_km must be greater than upper_sd_km.")
    W_km = thickness_km / math.sin(math.radians(dip_deg))
    area_km2 = L_km * W_km

    # GR rates
    N_Mge_mmin_1yr = 10.0 ** (a_cum_1yr - b * mmin)
    N_Mge_mmin_T = N_Mge_mmin_1yr * n_years

    # GR seismic moment rate (per year)
    mdot = gr_seismic_moment_rate(a_cum_1yr, b, mmin, mmax)
    mdot_e18 = mdot / 1e18
    M_e18_T = mdot_e18 * n_years

    return {
        "L_km": L_km,
        "W_km": W_km,
        "area_km2": area_km2,
        "N_Mge_mmin_1yr": N_Mge_mmin_1yr,
        "N_Mge_mmin_T": N_Mge_mmin_T,
        "Mdot_e18_1yr": mdot_e18,
        "M_e18_T": M_e18_T,
    }
def build_slip_rate_map(
    shp_path,
    id_field="id_seg",
    slip_field="slip_rate",
    range_field=None,
):
    """
    Build a mapping {source_id: slip_rate} from a fault shapefile.

    Parameters
    ----------
    shp_path : str or Path
        Path to the shapefile containing fault attributes.
    id_field : str, optional
        Name of the field that matches the OpenQuake source_id
        (e.g. 'id_seg', 'id_flt', or similar).
    slip_field : str, optional
        Name of the numeric slip-rate field (e.g. 'slip_rate', in mm/yr).
    range_field : str or None, optional
        If provided and `slip_field` is missing or NaN, this field will
        be used as a backup, assuming a string like '0.1-1' and using
        the midpoint of the range.

    Returns
    -------
    dict
        Mapping {src_id (str): slip_rate (float)}.
    """
    gdf = gpd.read_file(shp_path)

    slip_map = {}
    for _, row in gdf.iterrows():
        src_id = str(row[id_field]).strip()

        slip_val = None
        # 1) Try numeric field first
        if slip_field in row and row[slip_field] is not None:
            try:
                slip_val = float(row[slip_field])
            except (TypeError, ValueError):
                slip_val = None

        # 2) If that fails and range_field is given, try to parse 'a-b'
        if slip_val is None and range_field is not None and range_field in row:
            rng = row[range_field]
            if isinstance(rng, str) and "-" in rng:
                try:
                    a_str, b_str = rng.split("-", 1)
                    a_val = float(a_str)
                    b_val = float(b_str)
                    slip_val = 0.5 * (a_val + b_val)  # simple midpoint
                except (TypeError, ValueError):
                    slip_val = None

        if slip_val is None:
            # no usable slip for this row; skip
            continue

        # If there are duplicates, last one wins; you can change this if needed
        slip_map[src_id] = slip_val

    return slip_map

def simple_faults_to_shapefile(
    nrml_path,
    out_shapefile,
    slip_rate_map=None,        # NEW: dict {src_id: slip_rate}
    slip_unit="mm/yr",
    shear_modulus=30e9,
    coupling=1.0,
):
    """
    Parse an OpenQuake source model (NRML), extract simpleFaultSources,
    fit a/b to their incremental MFDs, and write a shapefile.

    Parameters
    ----------
    nrml_path : str or Path
        Path to the NRML source model.
    out_shapefile : str or Path
        Output shapefile path.
    filter_polygon_shp : str or Path, optional
        If given, only faults that intersect this polygon shapefile
        will be exported (similar to your Chile filter).

    Returns
    -------
    geopandas.GeoDataFrame
        The GeoDataFrame that was written to disk.
    """
    sf_sources = read_simple_fault_sources(nrml_path)

    region_gdf = None

    records = []
    for src in sf_sources:
        # Build fault trace geometry (lon, lat)
        print(src)
        coords = [(pt.longitude, pt.latitude) for pt in src.fault_trace.points]
        line = LineString(coords)

        # MFD and GR fit (from NRML incrementalMFD)
        mfd = src.mfd
        gr_fit = fit_gr_from_incremental_mfd(mfd)

        a_cum_data = gr_fit["a_cum_fit"]  # GR a_cum_1yr from the XML MFD
        b_val = gr_fit["b_fit"]
        mmin = gr_fit["mmin"]
        mmax = gr_fit["mmax"]

        # Geometry-based seismic summary (from GR, i.e. "seismic moment")
        L_km = haversine_length_km(coords)
        thickness_km = float(src.lower_seismogenic_depth) - float(src.upper_seismogenic_depth)
        W_km = thickness_km / math.sin(math.radians(float(src.dip)))
        area_km2 = L_km * W_km

        # Seismic moment rate implied by the GR MFD (per year)
        mdot_seis = gr_seismic_moment_rate(
            a_cum_1yr=a_cum_data,
            b=b_val,
            mmin=mmin,
            mmax=mmax,
        )
        mdot_seis_e18 = mdot_seis / 1e18

        # --- NEW: tectonic moment & moment-balance a, if slip_rate is provided ---
        a_cum_mbal = np.nan
        mdot_tect_e18 = np.nan

        if slip_rate_map is not None:
            slip = slip_rate_map.get(src.source_id, None)
            if slip is not None:
                mdot_tect = tectonic_moment_rate(
                    length_km=L_km,
                    upper_sd_km=float(src.upper_seismogenic_depth),
                    lower_sd_km=float(src.lower_seismogenic_depth),
                    dip_deg=float(src.dip),
                    slip_rate=slip,
                    slip_unit=slip_unit,
                    shear_modulus=shear_modulus,
                    coupling=coupling,
                )
                mdot_tect_e18 = mdot_tect / 1e18

                # moment-balance a (what a would be if we forced GR to match tectonic moment)
                a_cum_mbal = a_from_moment_rate_truncated_gr(
                    mdot=mdot_tect,
                    b=b_val,
                    m_min=mmin,
                    m_max=mmax,
                )

        # Collect attributes
        rec = {
            "src_id": src.source_id,
            "name": src.name,
            "trt": str(src.tectonic_region_type),
            "dip": float(src.dip),
            "usd": float(src.upper_seismogenic_depth),
            "lsd": float(src.lower_seismogenic_depth),
            "rake": float(src.rake),
            'slip': slip,
            "rar": float(src.rupture_aspect_ratio),
            "msr": src.magnitude_scaling_relationship.__class__.__name__,
            "mfd_type": mfd.__class__.__name__,
            "mfd_min_mag": float(mfd.min_mag),
            "mfd_bin_w": float(mfd.bin_width),
            "n_bins": len(mfd.occurrence_rates),

            # GR fit (from XML)
            "a_incr_fit": gr_fit["a_fit"],  # incremental intercept (internal)
            "a_cum_data": a_cum_data,  # GR a_cum_1yr from the NRML MFD
            "b_fit": b_val,
            "gr_mmin": mmin,
            "gr_mmax": mmax,
            "gr_r2log": gr_fit["r2_log10"],
            "gr_rmslog": gr_fit["rms_log10"],

            # Geometry
            "L_km": L_km,
            "W_km": W_km,
            "area_km2": area_km2,

            # Seismic moment & rate (from existing GR MFD)
            "Mdot_seis_e18": mdot_seis_e18,  # N·m/yr in units of 1e18
            "Nge_mmin_1yr": 10.0 ** (a_cum_data - b_val * mmin),

            # Tectonic moment & moment-balance a (if slip provided)
            "Mdot_tect_e18": mdot_tect_e18,
            "a_cum_mbal": a_cum_mbal,

            "geometry": line,
        }
        records.append(rec)

    gdf = gpd.GeoDataFrame( data=records, crs=4326)
    gdf.to_file(out_shapefile)
    return gdf

slip_rate_map = build_slip_rate_map(
    "../data/sara_active_faults/crustal_faults_chile.shp",
    id_field="id_seg",        # or "id_flt" depending on your file
    slip_field="slip_rate",   # numeric field
    range_field="slip_rates", # optional backup like '0.1-1'
)

# Then pass it into simple_faults_to_shapefile
gdf_faults = simple_faults_to_shapefile(
    "crustalfaults.xml",
    "crustalfaults_with_mbal.shp",
    slip_rate_map=slip_rate_map,
    slip_unit="mm/yr",        # adjust if they're in m/yr
    shear_modulus=30e9,
    coupling=1.0,
)