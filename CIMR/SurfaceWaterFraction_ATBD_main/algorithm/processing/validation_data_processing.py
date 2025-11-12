"""
This will house the code to load, transform and collocate Windsat
Tbs, LPDR product, GLWD classification and IGBP maps.
"""

import xarray as xr
import pandas as pd
import numpy as np
import os
import re
import rioxarray
from datetime import date
from functools import partial
from dataclasses import dataclass
import xml.etree.ElementTree as ET


# Load LPDR data (NOTE: only descending swath)
def load_lpdr(lpdr_folder: str) -> xr.Dataset:
    """
    Load and collocate data according to metadata from website.
    This version only selects Descending swath data from the provided
    folder.

    """

    # Static metadata: LPDR v3
    ordered_band_names = [
        'fw', 'fwns', 'Tmn or Tmx', 'PWV', 'VOD', 'vsm', 'VPD'
    ]
    band_id2name = {i+1: name for i, name in enumerate(ordered_band_names)}

    lpdr_descriptions = [
        '30-day smoothed open water fraction ',
        'Non-smoothed open water fraction ',
        """Daily surface air temperature minima or maxima,
        corresponding to descending or ascending pass retrievals """,
        'Vertically integrated atmospheric water vapor ',
        'Vegetation optical depth at 10.7 GHz ',
        'Volumetric soil moisture at 10.7 GHz ',
        'Near-surface atmospheric Vapor Pressure Deficit ',
    ]

    lpdr_units = [
        'dimensionless ',
        'dimensionless',
        'Kelvin ',
        'mm ',
        'Neper ',
        'cm3/cm3 ',
        'KPa ',
    ]
    lpdr_valid_range = [
        '0-1',
        '0-1',
        '240-340',
        '0-80',
        '0-3',
        '0-1',
        '≥0'
    ]

    lpdr_dss = []
    doys = []
    for filename in os.listdir(lpdr_folder):
        if filename.endswith("D.tif"):
            continue

        # extract date from filename.
        date_regex = r"AMSRU_Mland_(\d{4})(\d{3})[AD].tif"
        _year, doy = re.findall(pattern=date_regex, string=filename)[0]
        doys.append(int(doy))

        file_path = os.path.join(lpdr_folder, filename)
        darr = rioxarray.open_rasterio(file_path)
        ds = darr.to_dataset(dim="band")
        ds = ds.rename(band_id2name)

        lpdr_dss.append(ds)

    lpdr_ds = xr.concat(lpdr_dss, dim="day_number")
    lpdr_ds["day_number"] = doys

    # Add metadata
    for i, dv in enumerate(lpdr_ds.data_vars.keys()):
        lpdr_ds[dv].attrs = {
            "Description": lpdr_descriptions[i],
            "Units": lpdr_units[i],
            "Valid_range": lpdr_valid_range[i]
        }

    lpdr_ds.day_number.attrs = {
        "Long name": "day of the year"
    }
    lpdr_ds

    return lpdr_ds


def load_GLWD(glwd_folder: str):
    """
        Load reprojected GLWD data from folder.
    """
    glwd_name_pattern = r"GLWD_(.*)_025deg.tif"
    glwd_file_names = os.listdir(glwd_folder)
    glwd_products = [
        re.findall(glwd_name_pattern, filename)[0]
        for filename in glwd_file_names
    ]

    all_darr = []
    for i, filename in enumerate(os.listdir(glwd_folder)):
        file_path = os.path.join(glwd_folder, filename)
        darr = rioxarray.open_rasterio(file_path)
        darr = darr.assign_coords({"band": [i+1]})
        all_darr.append(darr)

    glwd_da = xr.concat(all_darr, dim="band")

    # Individual band values are 1, diferenciate them with enumerate index
    glwd_ds = glwd_da.to_dataset(dim="band")
    glwd_ds = glwd_ds.rename(
        {i+1: name for i, name in enumerate(glwd_products)}
    )

    return glwd_ds


# IMPORTED FROM LST ATBD

def recover_dates(
    folder_path: str, ymd_regex: str = r"_(\d{4})_(\d{2})_(\d{2})"
) -> list[date]:
    """
    Returns a list of dates parsing the file names within the folder path
    using the given year-month-day regex pattern.

    param folder_path:
    param ymd_regex: must return year, month and day using capturing groups.
    Default works for Windsat datafiles
    "RSS_WINDSAT_DAILY_TBTOA_MAPS_2017_01_01.nc"
    """

    dates = []
    for file in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, file)):

            year, month, day = [
                int(number) for number in re.findall(ymd_regex, file)[0]
            ]
            dates.append(date(year, month, day))

    return dates


def get_doy_sinceJ1st2017(dates: list[date]) -> list[int]:
    """
    Return the day of the year since January 1st 2017 (fisrt date)
    from a list of datetime objects. This will be used as an index
    for loading more than one year of data. DoY = MOD(366, DsJ1st2017)
    """

    def calculate_day_index(d: date) -> int:
        year_diff = d.year - 2017
        day_of_year = (d - date(d.year, 1, 1)).days + 1
        # day_of_year = d.timetuple().tm_yday
        # TODO: Leep years are a problem, tm_yday returns different doy for
        # the same month-day depending on year.
        return year_diff * 366 + day_of_year  # Cumulative index

    return [calculate_day_index(d) for d in dates]


def select_dims(dataset: xr.Dataset) -> xr.Dataset:
    """
    Remove unused frequencies and polarizations

    Frequencies:
    0 -- 6.8 GHz
    1 -- 10.7 GHz
    2 -- 18.7 GHz (Ku)
    3 -- 23.8 GHz
    4 -- 37.0 GHz (Ka)

    Polarizations:
    0 -- V
    1 -- H
    (except for 6.8 and 23.8 GHz we also have):
    2 -- P (+45º)
    3 -- M (-45º)
    4 -- L (Circular Left)
    5 -- R (Circular Right)
    """

    # Select dimensions
    dataset = dataset.sel(
        indexers={
            "polarization": [0, 1],  # [ V, H ]
            "frequency_band": [2, 4],  # [ 18.7 GHz (Ku) , 37.0 GHz (Ka) ]
            # "look_direction": 1,  # Aft look
        }
    )
    return dataset


def transform_dataset(dataset: xr.Dataset) -> xr.Dataset:
    """
    Other transformations
    """
    # Roll lattitude grid so we have -180, 180 range
    # dataset = dataset.roll(shifts={"longitude_grid": 4 * 180})

    # Extract latitude and longitude grid dimensions
    dataset = dataset.assign_coords(
        lat=dataset.latitude,
        lon=dataset.longitude
    )

    # Join Polarization dimentions into one:
    if "polarization_dual" in dataset.sizes.keys():
        dataset = dataset.rename({"polarization_dual": "polarization"})

    return dataset


def preporcess_dataset(dataset: xr.Dataset) -> xr.Dataset:
    """Wrapper"""
    dataset = select_dims(dataset)
    dataset = transform_dataset(dataset)
    return dataset


# Partial function definition
# TODO: Do I need to do this? this was chatGPT's idea
_preprocess_dataset = partial(preporcess_dataset)


def windsat_datacube(folder_path: str) -> xr.Dataset:
    """
    Wrapper for creating a dataset with the combined data inside a folder
    param folder_path: must contain the files in .nc format

    Limited to general transformations

    param folder_path: str, name of the folder
    return: dataset with the loaded data.
    """

    dates = recover_dates(folder_path)
    day_numbers = get_doy_sinceJ1st2017(dates)

    ds = xr.open_mfdataset(
        paths=os.path.join(folder_path + "/*.nc"),
        preprocess=_preprocess_dataset,
        decode_times=False,  # "time" is a datavar
        concat_dim="day_number",
        combine="nested",
    )

    # Add a day_number coordinate
    ds["day_number"] = day_numbers
    ds["day_number"].attrs = {
        "Description": "Int, day since Jan 1st 2017, definded as 1"
    }

    return ds


def load_swf_validation_ds(
    windsat_folder, lpdr_folder, glwd_folder, igbp_file
) -> xr.Dataset:
    """
        WRAPPER
        Read the data from the corrsponding folders and return the full
        collocated dataset
        as an xarray object.
    """
    # Load each individual dataset
    igbp_ds = xr.open_dataset(igbp_file, engine="h5netcdf")
    lpdr_ds = load_lpdr(lpdr_folder)
    glwd_ds = load_GLWD(glwd_folder)
    ws_ds = windsat_datacube(windsat_folder)

    # NOTE: Windsat ds will act as a template, we need to transform it:
    # We only need DESCENDING swath data
    # NOTE: we move this outside loading and into processing, more flexible
    # ws_ds = ws_ds.sel(swath_sector=1)

    # Windsat lon origin is displaced.
    ws_ds = ws_ds.roll({"longitude_grid": 180*4})

    # Swap grid ints for coordinates
    ws_ds = ws_ds.swap_dims({
        "latitude_grid": "lat",
        "longitude_grid": "lon"
    })

    # Sort by time-coordinate indeces
    ws_ds = ws_ds.sortby(["day_number", "lat", "lon"])

    # transform Windsat's lon from [0, 360] to standard [-180, 180]
    attrs = ws_ds.lon.attrs
    ws_ds["lon"] = ws_ds.lon - 180
    ws_ds["lon"].attrs = attrs
    ws_ds["lon"].attrs["valid_min"] = -179.875
    ws_ds["lon"].attrs["valid_max"] = 179.875

    # NOTE LPRD: manage fill values outside the valid range for each dvar.
    for dvar in lpdr_ds.data_vars.keys():
        range_strings = lpdr_ds[dvar].attrs["Valid_range"].split("-")
        if len(range_strings) == 2:
            min_val, max_val = [int(s) for s in range_strings]

            # Mask out the data outside the range ints
            lpdr_ds[dvar] = lpdr_ds[dvar].where(
                (lpdr_ds[dvar] > min_val) & (lpdr_ds[dvar] < max_val),
                drop=True,
            )
        else:
            # Special case for the >0 valid range
            min_val = int(range_strings[0][-1])
            lpdr_ds[dvar] = lpdr_ds[dvar].where(
                (lpdr_ds[dvar] > min_val), drop=True,
            )

    # Transform and collocate all ds's with Windsat:
    # Collocate IGBP landcover
    ws_ds["IGBP_landcover"] = (
        ("lat", "lon"), igbp_ds.Majority_Land_Cover_Type_1.values[:, :]
    )
    ws_ds["IGBP_landcover"].attrs = igbp_ds.Majority_Land_Cover_Type_1.attrs

    # Collocate LPDR
    # NOTE: I need to make sure that LPDR has the same day_number as Windsat
    lpdr_ds = lpdr_ds.reindex(day_number=ws_ds.day_number)

    for dvar in lpdr_ds.data_vars.keys():
        # NOTE Data is stored with ordered lat and lon, need to reverse lat
        ws_ds[dvar] = (
            ("day_number", "lat", "lon"), lpdr_ds[dvar].data[:, ::-1, :])
        ws_ds[dvar].attrs = lpdr_ds[dvar].attrs

    # Collocate GLWD
    for dvar in glwd_ds.data_vars.keys():
        # Data is stored with ordered lat and lon, we need to reverse latitude
        ws_ds[dvar] = (("lat", "lon"), glwd_ds[dvar].data[::-1, :])
        ws_ds[dvar].attrs = glwd_ds[dvar].attrs

    return ws_ds


def select_data_variables(
        ds: xr.Dataset, add_dvars: list = None
) -> xr.Dataset:
    """
        Explicit description of all data variables,
        default list to load. Return only the data variables needed.
        add_dvars: add this to deafult dvars if needed for an experiment.
    """
    dvar_filter = []
    default_ws_dvars = [
        # Datavars coding for Dimensions
        # "longitude",
        # "latitude",
        # "node",  # node of swath, [ascending, descending]
        # "look", # look direction. 0 = fore, 1 = aft.
        # Actual data
        # "frequency_vpol",  # center frequency of V-pol channel in each band
        # "frequency_hpol",  # center frequency of H-pol channel in each band
        # "eia_nominal",  # nominal Earth indidence angle of each band
        # "time",  # Time of observation (lat, lon) seconds since 01JAN200000Z
        # "eaa",  # boresight Earth azimuth angle. range: [0o, 360o].
        # "eia",  # boresight Earth incidence angle. range: [0o, 90o]
        "tbtoa",  # Brightness temperature
        # "quality_flag",  # 32-bit quality control flag
        # "sss_HYCOM", # HYCOM sea surface salinity
        # "surtep_REY", # NOAA (Reynolds) V2 OI sea surface temperature
        # # Land fractions
        # "fland_06", # for 6GHz
        # "fland_10", # For 10 GHz
        # # Windsat V8 products
        # "surtep_WSAT", # skin temperature
        # "colvap_WSAT", # atmosphere_mass_content_of_water_vapor
        # "colcld_WSAT", # atmosphere_mass_content_of_cloud_liquid_water
        # "winspd_WSAT", # sea surface wind speed
        # "rain_WSAT", # surface rain rate
        # # Cross-Calibrated Multi-Platform
        # "winspd_CCMP", # Wind speed
        # "windir_CCMP", # Cross-Calibrated Multi-Platform Wind direction
        # # ERA 5 products
        "surtep_ERA5",  # skin temperature
        # "airtep_ERA5",  # Air temperature at 2m above surface
        # "colvap_ERA5", # Columnar liquid cloud water
        # "colcld_ERA5", # atmosphere_mass_content_of_cloud_liquid_water
        # "winspd_ERA5", # 10-m NS wind speed
        # "windir_ERA5", # Wind direction
        # "surtep_CMC", # CMC Sea surface temperature
        # "rain_IMERG", # IMERG V6 surface rain rate
        # # RSS 2022 absorption model
        # NOTE! Theese 3 dvars have polarization_dual dimentions instead
        # of polarization (0,1)
        "tran",  # Total atmospheric transmittance computed from ERA
        # atmospheric profiles and WSAT columnar vapor and cloud water
        "tbdw",  # Atmospheric downwelling brightness temperature computed
        # from ERA atmospheric profiles and WSAT columnar vapor and cloud
        # water
        "tbup",  # Atmospheric upwelling brightness temperature
    ]

    default_lpdr_dvars = [
        # 'fw',  # Monthly averaged fw
        "fwns",  # Non-smoothed fractional water
        # 'Tmn or Tmx',
        # 'PWV',
        'VOD',  # X band Vegetation optical depth
        'vsm',  # X band Soil moisture
        # 'VPD',
    ]

    other_dvars = [
        "IGBP_landcover",
        "all_classes_area_pct",
        "main_class",
        "main_class_50pct"
    ]
    dvar_filter.extend(default_ws_dvars)
    dvar_filter.extend(default_lpdr_dvars)
    dvar_filter.extend(other_dvars)
    if add_dvars:
        dvar_filter.extend(add_dvars)

    return ds[dvar_filter]


def unravel_freqpol(ds: xr.Dataset, dvars: list[str]) -> xr.Dataset:
    """
        FROM LST ATBD
        Unravel the frequency and polarization dimensions into
        a set of new data variables, for each dvar in list.
        return the dataset with added fields
    """
    frequencies = {
        0: "19",
        1: "37",
    }
    polarizations = {
        0: "V",
        1: "H",
    }

    for dvar in dvars:
        if dvar not in ds.data_vars:
            print(f"Warning {dvar} not found in dataset.")
            continue

        for freqid, freqname in frequencies.items():
            for polid, polname in polarizations.items():
                new_name = f"{dvar}{freqname}{polname}"
                ds[new_name] = ds[dvar].isel(
                    polarization=polid, frequency_band=freqid
                )

    return ds

# Manage config file:


@dataclass
class SwfConfig():
    paths: dict[str:str]
    local: bool


def read_config(xml_path) -> SwfConfig:
    """
        Read the config file and recover folder paths
        hierarchy is remote, then local.
    """

    tree = ET.parse(xml_path)
    root = tree.getroot()

    local_text = tree.find("local").text.capitalize()
    parse_local = {"True": True, "False": False}
    local = parse_local[local_text]

    local_paths = {child.tag: child.text for child in root.find("local_paths")}
    remote_paths = {
        child.tag: child.text for child in root.find("remote_paths")
    }

    if local is True:
        paths = local_paths
    else:
        paths = remote_paths

    return {"paths": paths, "local": local}


def load_lut(
        ds: xr.Dataset,
        lut_filepath: str,
) -> xr.Dataset:
    """
        read the lookup table into the dataset and assign a reference value
        for each observation (day_number, lat, lon)
        filepaths must be .csv files

        return the updated dataset with reference value data
    """

    # NOTE: LUT table metadata (static for now)
    sm_bins = np.array([0, 0.1, 0.2, 0.3, 0.4, 0.5])
    vod_bins = np.array([0, 0.05, 0.1, 0.15, 0.2, 0.25,
                         0.3, 0.4, 0.5, 0.6, 0.7, 1])

    sm_slices = [(sm_bins[i], sm_bins[i+1]) for i in range(len(sm_bins)-1)]
    vod_slices = [(vod_bins[i], vod_bins[i+1]) for i in range(len(vod_bins)-1)]

    # We want to re-create the index we used to groupby and generate the LUTs:
    sm_idx = np.full(ds.vsm.shape, np.nan)
    vod_idx = np.full(ds.VOD.shape, np.nan)

    for i, (sm_min, sm_max) in enumerate(sm_slices):
        sm_idx[(ds.vsm >= sm_min) & (ds.vsm < sm_max)] = i

    for j, (vod_min, vod_max) in enumerate(vod_slices):
        vod_idx[(ds.VOD >= vod_min) & (ds.VOD < vod_max)] = j

    sm_idx = xr.DataArray(sm_idx, dims=ds.vsm.dims)
    vod_idx = xr.DataArray(vod_idx, dims=ds.VOD.dims)

    # Assign to the dataset:
    ds = ds.assign_coords(sm_bin=sm_idx, vod_bin=vod_idx)

    # Open LUTs as dataframes from csv
    lut_df = pd.read_csv(lut_filepath, index_col=0)

    # Cast LUT into dataarrays
    lut_xr = xr.DataArray(lut_df)

    # fill them into the original dataset
    ds["sm_bin"] = ds["sm_bin"].fillna(-1).astype(int)
    ds["vod_bin"] = ds["vod_bin"].fillna(-1).astype(int)

    # Adapt the name according to the filename
    pol_name = os.path.basename(
        lut_filepath
    ).removeprefix("lut_").removesuffix(".csv")

    ds[pol_name] = (("sm_bin", "vod_bin"), lut_xr.values)

    # Create new dvars with day, lat, lon dimentions
    dvar_name_h = "ref_land_emis_" + pol_name

    ds[dvar_name_h] = ds[pol_name].sel(
        sm_bin=ds["sm_bin"], vod_bin=ds["vod_bin"]
    )

    # Drop unecessary dimentions
    ds = ds.drop_dims(["sm_bin", "vod_bin"])

    # Handle missing values
    # NOTE: to create the dataarrays, all values must have the same dtype,
    # so NaNs are mapped to -1
    missing_vodsm = (ds.sm_bin == -1) & (ds.vod_bin == -1)
    ds = ds.where(~missing_vodsm)

    return ds

def atmospheric_corrections(ds: xr.Dataset) -> xr.Dataset:
    """ 
    Apply atmospheric correction to the brightness temperatures.
    fields with:
    First Odert approximation:
    TBBoA = (TBToA - TBau)/ tran.

    De Lannoy 2016 formula:
    TBBoA = Ts · ((TBToA · tran^-1) - (1+tran^-1)·TBau) / (Ts - TBau)

    returns the same dataset with 2 new fields for _1st_order and _de_lannoy formula.

    This function is taiolred to this particular dataset and should not be used on others.

    """
    
    ds["tbboa_1st_order"] = (ds.tbtoa - ds.tbup)/ ds.tran
    ds["tbboa_de_lannoy"] = ds.surtep_ERA5 * ((ds.tbtoa * (1 / ds.tran)) - ds.tbup*(1 + (1 / ds.tran)))/(ds.surtep_ERA5 - ds.tbup)

    return ds
    
