#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os,shutil,pdb,glob, re
import pandas as pd
import xarray as xr
import numpy as np
import config as cfg


import sys
sys.path.append('/fs/homeu2/eccc/mrd/ords/rpnenv/nil005/Codes/smrt')
#from smrt.core.globalconstants import DENSITY_OF_ICE
from smrt import sensor_list, make_model, make_snowpack, make_soil
from smrt.emmodel.iba import derived_IBA
from smrt.permittivity.snow_mixing_formula import wetsnow_permittivity_memls as memls

sys.path.append('/home/nil005/ords/Codes/mironov_soil')
from mironov import mironov_model


DENSITY_OF_ICE = 917.


# Functions
def debye_eqn(ssa, density):
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
                      
def generate_smrt_output():               
    '''
    Roughness model: Geometrical Optics Backscatter model
    Permittivity model: static complexe permittivity values to optimize from C-band
    '''

    # Determine soil permittivity using Mironov (https://github.com/JulienMeloche/mironov_soil)

    # open the parameter fil and get the soil parameters needed to calculate the soil permittivity
    file = open(cfg.tmp_path+'/MESH_parameters.txt') 
      
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

    deltaz = pd.read_csv(cfg.tmp_path+'/MESH_input_soil_levels.txt', delim_whitespace=' ', header=None)
    deltaz = deltaz[0].values

    # Compute dry soil density (from inisoil_svs2.f90)
    wsat  =  -0.00126   * np.array(sand_perc) + 0.489
    rhosoil = (1.0-wsat)*2700. # kg m-3
    rhosoil = rhosoil / 1000. # kg m-3 to g cm-3


    #Mean square slope of the target footprint calculated from soil RSM height and soil correlation length
    #use dummy values for now
    sig_soil = 0.01
    lc_soil = 0.1
    mss=2.*(sig_soil/lc_soil)**2

             
    # Read simulation results
    mod = xr.open_dataset(os.path.join(cfg.tmp_path,'output','out_svs2.nc'))

    df_soil = mod[['WSOIL','TPSOIL']].to_dataframe() 
    df_snow = mod[['SNODEN_ML','SNOMA_ML','TSNOW_ML','SNODOPT_ML','SNODP']].to_dataframe() 

    # SNODEN_ML: densite des couches
    # SNOMA_ML: SWE des couches
    # TSNOW_ML: T des couches
    # SNODOPT_ML: diametre optique des couches
    # SNODP: hauteur totale du snowpack

    if cfg.da_algorithm == "ensemble_OL": # Run SMRT only when we have obs'
        # Get the obs
        obs = xr.open_dataset(cfg.obs_file).to_dataframe()
        times = obs.index
    else:
        # Snow profile outputs are every 6 h     
        time_bgn = pd.to_datetime(str(mod.time.values[0]))
        time_end = pd.to_datetime(str(mod.time.values[-1]))                                        
        times = pd.date_range(start = time_bgn , end = time_end , freq = '1H')   
        times = times[-1:] # just the last time of each assimilation step for now, saves time
                          

    # Get backscatter from SMRT from the times when we have snow profile outputs
    sigma_13GHz = []
    sigma_17GHz = []
    sigma_5p4GHz = []
    time_sigma = []
    sigma_diff_13_17 = []
    sigma_diff_13_5p4 = []
    sigma_diff_17_5p4 = []

    for tt in times: # just the last time
        snow_t = df_snow.loc[tt].copy()
        snow_t = snow_t[snow_t['SNOMA_ML'] > 0]  # Select only layers with a mass  

        soil_t = df_soil.loc[tt]

        # Calculate soil permittivity
        e_r, e_i = mironov_model(soil_t['TPSOIL'].iloc[0]-273.15, clay_perc[0], soil_t['WSOIL'].iloc[0], rhosoil[0])
        eps = complex(e_r, e_i)


        if len(snow_t) > 0.: # If there is at least one layer

            sub = make_soil('geometrical_optics_backscatter', 
                            permittivity_model = eps, 
                            mean_square_slope=mss, 
                            temperature = soil_t['TPSOIL'].iloc[0])

            snow_t['thickness'] = snow_t[['SNODEN_ML','SNOMA_ML']].apply(lambda x : x[1] / x[0], axis = 1) 
            snow_t['SNOSSA_ML'] = snow_t['SNODOPT_ML'].apply(lambda x: 6./(x * DENSITY_OF_ICE) if x>0 else 0) 
            snow_t['corr length'] = snow_t[['SNODEN_ML','SNOSSA_ML']].apply(lambda x: debye_eqn(x[1], x[0]), axis = 1)

            snowpack = make_snowpack(thickness = snow_t['thickness'].values,
                                     microstructure_model = "exponential",
                                     density = snow_t['SNODEN_ML'].values,
                                     temperature = snow_t['TSNOW_ML'].values,
                                     corr_length = snow_t['corr length'],
                                     substrate = sub)

            #Modeling theories to use in SMRT
            model = make_model(derived_IBA(memls), "dort", rtsolver_options=dict(diagonalization_method="shur_forcedtriu",
                                                                    error_handling='nan'),
                                              emmodel_options=dict(dense_snow_correction='auto'))


            sensor_13GHz  = sensor_list.active(13e9, 35)
            sensor_17GHz  = sensor_list.active(17e9, 35)
            sensor_5p4GHz  = sensor_list.active(5.4e9, 35)

            #run the model
            result_13GHz = model.run(sensor_13GHz, snowpack, parallel_computation=False)
            result_17GHz = model.run(sensor_17GHz, snowpack, parallel_computation=False)
            result_5p4GHz = model.run(sensor_5p4GHz, snowpack, parallel_computation=False)

            sigma_13GHz.append(to_dB(result_13GHz.sigmaVV()))
            sigma_17GHz.append(to_dB(result_17GHz.sigmaVV()))
            sigma_5p4GHz.append(to_dB(result_5p4GHz.sigmaVV()))
            sigma_diff_13_17.append(result_13GHz.sigmaVV()-result_17GHz.sigmaVV())
            sigma_diff_13_5p4.append(result_13GHz.sigmaVV()-result_5p4GHz.sigmaVV())
            sigma_diff_17_5p4.append(result_17GHz.sigmaVV()-result_5p4GHz.sigmaVV())
            time_sigma.append(tt)
        else:

            sigma_13GHz.append(-999.)
            sigma_17GHz.append(-999.)
            sigma_5p4GHz.append(-999.)
            sigma_diff_13_17.append(-999.)
            sigma_diff_13_5p4.append(-999.)
            sigma_diff_17_5p4.append(-999.)
            time_sigma.append(tt)


                             
    smrt = pd.DataFrame()
    smrt['time'] = time_sigma
    smrt['sigma_13GHz'] = sigma_13GHz
    smrt['sigma_17GHz'] = sigma_17GHz
    smrt['sigma_5p4GHz'] = sigma_5p4GHz
    smrt['sigma_diff_13_17'] = sigma_diff_13_17
    smrt['sigma_diff_13_5p4'] = sigma_diff_13_5p4
    smrt['sigma_diff_17_5p4'] = sigma_diff_17_5p4
    smrt = smrt.set_index('time')
    smrt_xr = smrt.to_xarray()
                             
    # Write netcdf   
    encoding = generate_encodings(smrt_xr) 
    netcdf_file_out = 'out_smrt.nc'
    smrt_xr.to_netcdf(os.path.join(cfg.tmp_path,'output',netcdf_file_out))

