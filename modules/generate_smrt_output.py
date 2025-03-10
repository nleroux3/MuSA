#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os,shutil,pdb,glob, re
import pandas as pd
import xarray as xr
import numpy as np
import config as cfg
from joblib import Parallel, delayed, parallel_backend
from dask.distributed import LocalCluster, Client

from modules.radar_equivalent_snow import *

from smrt import sensor_list, make_model, make_snowpack, make_soil
from smrt.emmodel.iba import derived_IBA
from smrt.permittivity.snow_mixing_formula import wetsnow_permittivity_memls as memls
from concurrent.futures import ProcessPoolExecutor, as_completed
from modules.mironov import mironov_model


DENSITY_OF_ICE = 917.


# Functions
def debye_eqn(ssa, density):
    if ssa == 0 :
        return np.nan
    else:
        return 4. * (1. - density / DENSITY_OF_ICE) / (ssa * DENSITY_OF_ICE)


def to_dB(data):
    return 10. * np.log10(data)

def to_lin(data):
    return 10.**(data/10.)

def generate_encodings(data):
    DEFAULT_ENCODING = {
        'zlib': True,
        'shuffle': True,
        'complevel': 4,
        'fletcher32': False,
        'contiguous': False,
    }

    encoding = {}
    for var in data.data_vars:
        encoding[var] = DEFAULT_ENCODING.copy()
    return encoding

def get_snowpack(snow_df, soil_df, clay_perc, rhosoil, mss):

    if len(snow_df) == 0: # no snow layer
        return np.nan
    else:
        # Calculate soil permittivity
        e_r, e_i = mironov_model(soil_df['TPSOIL'].iloc[0]-273.15, clay_perc, soil_df['WSOIL'].iloc[0], rhosoil)
        eps = complex(e_r, e_i)

        sub = make_soil('geometrical_optics_backscatter',
                        permittivity_model = eps,
                        mean_square_slope=mss,
                        temperature = soil_df['TPSOIL'].iloc[0])


        snowpack = make_snowpack(thickness = snow_df['thickness'].values,
                                 microstructure_model = "exponential",
                                 density = snow_df['SNODEN_ML'].values,
                                 temperature = snow_df['TSNOW_ML'].values,
                                 corr_length = snow_df['corr length'],
                                 substrate = sub)

    return snowpack


def generate_smrt_output(tmp_mbr_folder):
    '''
    Roughness model: Geometrical Optics Backscatter model
    Permittivity model: static complexe permittivity values to optimize from C-band
    '''

    # Determine soil permittivity using Mironov (https://github.com/JulienMeloche/mironov_soil)

    # open the parameter fil and get the soil parameters needed to calculate the soil permittivity
    file = open(tmp_mbr_folder+'/MESH_parameters.txt')

    content = file.readlines()

    NotFound_sand = True
    line = 0
    while NotFound_sand:
        if content[line][:4] == 'sand':
            NotFound_sand = False
        else:
            line += 1
    sand_perc = re.findall(r"[-+]?(?:\d*\.*\d+)", content[line])
    sand_perc = [float(i) for i in sand_perc]


    NotFound_clay = True
    line = 0
    while NotFound_clay:
        if content[line][:4] == 'clay':
            NotFound_clay = False
        else:
            line += 1
    clay_perc = re.findall(r"[-+]?(?:\d*\.*\d+)", content[line])
    clay_perc = [float(i) for i in clay_perc]

    deltaz = pd.read_csv(tmp_mbr_folder+'/MESH_input_soil_levels.txt', delim_whitespace=' ', header=None)
    deltaz = deltaz[0].values

    # Compute dry soil density (from inisoil_svs2.f90)
    wsat  =  -0.00126   * np.array(sand_perc) + 0.489
    rhosoil = (1.0-wsat)*2700. # kg m-3
    rhosoil = rhosoil / 1000. # kg m-3 to g cm-3



    '''
    Roughness model: Geometrical Optics Backscatter model
    Permittivity model: static complex permittivity values to optimize from C-band
    '''
    #Mean square slope of the target footprint calculated from soil RSM height and soil correlation length
    #use dummy values for now
    sig_soil = 0.01
    lc_soil = 0.1
    mss=2.*(sig_soil/lc_soil)**2


    # Read simulation results
    mod = xr.open_dataset(os.path.join(tmp_mbr_folder,'output','out_svs2.nc'))

    df_soil = mod[['WSOIL','TPSOIL']].to_dataframe()
    df_snow = mod[['SNODEN_ML','SNOMA_ML','TSNOW_ML','SNODOPT_ML','SNODP']].to_dataframe()

    # SNODEN_ML: densite des couches
    # SNOMA_ML: SWE des couches
    # TSNOW_ML: T des couches
    # SNODOPT_ML: diametre optique des couches
    # SNODP: hauteur totale du snowpack

    df_snow['thickness'] = df_snow[['SNODEN_ML','SNOMA_ML']].apply(lambda x : x[1] / x[0], axis = 1)
    df_snow['SNOSSA_ML'] = df_snow['SNODOPT_ML'].apply(lambda x: 6./(x * DENSITY_OF_ICE) if x>0 else 0)
    df_snow['corr length'] = df_snow[['SNODEN_ML','SNOSSA_ML']].apply(lambda x: debye_eqn(x[1], x[0]), axis = 1)

    if cfg.da_algorithm == "ensemble_OL": # Run SMRT only when we have obs'
        # Get the obs times
        # obs = xr.open_dataset(cfg.obs_file).to_dataframe()
        # times = obs.index

        # The full snowpack vertical properties is outputted every 6 h
        time_bgn = pd.to_datetime(str(mod.time.values[0]))
        time_bgn_D = time_bgn.floor('D')
        time_end = pd.to_datetime(str(mod.time.values[-1]))
        times = pd.date_range(start = time_bgn_D , end = time_end , freq = '12H')
        times = times[times > time_bgn]

    else:
        # Snow profile outputs are every 6 h
        time_bgn = pd.to_datetime(str(mod.time.values[0]))
        time_end = pd.to_datetime(str(mod.time.values[-1]))
        times = pd.date_range(start = time_bgn , end = time_end , freq = '1H')
        times = times[-1:] # just the last time of each assimilation step for now, saves time

        # Every 12 h
        #time_bgn_D = time_bgn.floor('D')
        #times = pd.date_range(start = time_bgn_D , end = time_end , freq = '12H')
        #times = times[times > time_bgn]



    df_snow.loc[:, 'height'] = np.nan
    for date in times:
        df_temp = df_snow.loc[date].copy()
        df_snow.loc[date,'height'] = np.cumsum(df_temp.thickness.values[::-1])[::-1]

    # Get the snowpacks for SMRT
    if cfg.radar_equivalent_snow:
        snow_t_13GHz = [three_layer_k(df_snow.loc[date], method = 'thick-ke-density', freq = 13e9) for date in times]
        snow_t_17GHz = [three_layer_k(df_snow.loc[date], method = 'thick-ke-density', freq = 17e9) for date in times]


    # Get backscatter from SMRT from the times when we have snow profile outputs
    sigma_13GHz = []
    sigma_17GHz = []
    sigma_diff_13_17 = []


    time_list = []
    snowpacks = []
    SWE = []
    depth = []
    for tt in times:
        snow_t = df_snow.loc[tt]
        soil_t = df_soil.loc[tt]
        snow_t = snow_t[snow_t['SNOMA_ML'] > 0]  # Select only layers with a mass

        if len(snow_t) > 0: # We get the backscatter when the snowpack depth is > 0 m
            time_list.append(tt)
            snowpacks.append(get_snowpack(snow_t, soil_t,clay_perc[0], rhosoil[0], mss))
            SWE.append(snow_t['SNOMA_ML'].sum())
            depth.append(snow_t['SNODP'].mean())


    snowpacks = pd.Series(snowpacks, index = time_list)
    #create a dataframe
    meta_df = pd.DataFrame({'depth' :depth, 'SWE': SWE, 'smrt_snow' : snowpacks}, index = time_list).dropna()



    #Modeling theories to use in SMRT
    model = make_model(derived_IBA(memls), "dort", rtsolver_options=dict(diagonalization_method="shur_forcedtriu",
                                                                error_handling='nan'),
                                            emmodel_options=dict(dense_snow_correction='auto'))

    if len(time_list)  > 0:
        sensor  = sensor_list.active(13.5e9, 35)
        result_13GHz = model.run(sensor,  meta_df, snowpack_column='smrt_snow', parallel_computation=False)

        sensor  = sensor_list.active(17.25e9, 35)
        result_17GHz = model.run(sensor,  meta_df, snowpack_column='smrt_snow', parallel_computation=False)

        sigma_13GHz = to_dB(result_13GHz.sigmaVV())
        sigma_17GHz = to_dB(result_17GHz.sigmaVV())
        sigma_diff_13_17 = to_dB(abs(result_13GHz.sigmaVV() - result_17GHz.sigmaVV()))

    else:
        time_list = times
        sigma_13GHz = -9999.
        sigma_17GHz = -9999.
        sigma_diff_13_17 = -9999.

    smrt = pd.DataFrame()
    smrt['time'] = time_list
    smrt['sigma_13GHz'] = sigma_13GHz
    smrt['sigma_17GHz'] = sigma_17GHz
    smrt['sigma_diff_13_17'] = sigma_diff_13_17
    smrt = smrt.replace(np.nan, -9999.)
    smrt = smrt.set_index('time')

    smrt_xr = smrt.to_xarray()

    # Write netcdf
    encoding = generate_encodings(smrt_xr)
    netcdf_file_out = 'out_smrt.nc'
    smrt_xr.to_netcdf(os.path.join(tmp_mbr_folder,'output',netcdf_file_out))

