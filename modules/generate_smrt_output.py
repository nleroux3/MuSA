#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os,shutil,pdb,glob
import pandas as pd
import xarray as xr
import numpy as np
import config as cfg


import sys
sys.path.append('/fs/homeu2/eccc/mrd/ords/rpnenv/nil005/Codes/smrt')
#from smrt.core.globalconstants import DENSITY_OF_ICE
from smrt import sensor_list, make_model, make_snowpack, make_soil

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
                      
def generate_smrt_output(freq):               
    '''
    Roughness model: Geometrical Optics Backscatter model
    Permittivity model: static complexe permittivity values to optimize from C-band
    '''
    #Mean square slope of the target footprint calculated from soil RSM height and soil correlation length
    #use dummy values for now
    sig_soil = 0.01
    lc_soil = 0.1
    eps = complex(3.5, 0.1)
    mss=2*(sig_soil/lc_soil)**2

             
    # Read simulation results
    mod = xr.open_dataset(os.path.join(cfg.dir_exp,'output','out_svs2.nc'))

    df_soil = mod['TPSOIL'].to_dataframe() 
    df = mod[['SNODEN_ML','SNOMA_ML','TSNOW_ML','SNODOPT_ML','SNODP']].to_dataframe() 
    # SNODEN_ML: densite des couches
    # SNOMA_ML: SWE des couches
    # TSNOW_ML: T des couches
    # SNODOPT_ML: diametre optique des couches
    # SNODP: hauteur totale du snowpack

    print(cfg.da_algorithm)
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
    sigma = []
    time_sigma = []

    for tt in times: # just the last time
        d = df.loc[tt].copy()

        d_soil = df_soil.loc[tt]
        d = d[d['SNOMA_ML'] > 0]  # Select only layers with a mass  

        if len(d) > 0: # If there is at least obe layer

            sub = smrt.make_soil('geometrical_optics', 
                            permittivity_model = eps, 
                            mean_square_slope=mss, 
                            temperature = d_soil.iloc[0].values[0])

            d['thickness'] = d[['SNODEN_ML','SNOMA_ML']].apply(lambda x : x[1] / x[0], axis = 1) 
            d['SNOSSA_ML'] = d['SNODOPT_ML'].apply(lambda x: 6./(x * DENSITY_OF_ICE) if x>0 else 0) 
            d['corr length'] = d[['SNODEN_ML','SNOSSA_ML']].apply(lambda x: debye_eqn(x[1], x[0]), axis = 1)

            snowpack = make_snowpack(thickness = d['thickness'].values,
                                     microstructure_model = "exponential",
                                     density = d['SNODEN_ML'].values,
                                     temperature = d['TSNOW_ML'].values,
                                     corr_length = d['corr length'],
                                    substrate = sub)

            #Modeling theories to use in SMRT
            model = make_model("iba", "dort", rtsolver_options = {'error_handling':'nan', 'phase_normalization' : True})


            sensor  = sensor_list.active(freq, 35)

            #run the model
            result = model.run(sensor, snowpack, parallel_computation=False)

            sigma.append(to_dB(result.sigmaVV()))
            time_sigma.append(tt)
        else:
            sigma.append(-999.)
            time_sigma.append(tt)


                             
    smrt = pd.DataFrame()
    smrt['time'] = time_sigma
    smrt['sigma'] = sigma
    smrt = smrt.set_index('time')
    smrt_xr = smrt.to_xarray()
                             
    # Write netcdf   
    encoding = generate_encodings(smrt_xr) 
    netcdf_file_out = 'out_smrt.nc'
    smrt_xr.to_netcdf(os.path.join(cfg.dir_exp,'output',netcdf_file_out))

