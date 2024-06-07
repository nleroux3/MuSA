#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Some functions to interact with SVS2.

Author: Nicolas R. Leroux - nicolas.leroux@ec.g.ca
"""
import os, pdb
import shutil, glob
import subprocess
import tempfile
import datetime as dt
import pandas as pd
import config as cfg
import constants as cnt
import modules.met_tools as met
import secrets
import time
import copy
import pdcast as pdc
import warnings
import pyarrow as pa
import pyarrow.csv as csv
import numpy as np
import xarray as xr
import modules.internal_fns as ifn
from statsmodels.stats.weightstats import DescrStatsW
from metpy.calc import dewpoint_from_specific_humidity,wet_bulb_temperature
from metpy.units import units
from modules.generate_smrt_output import *
from modules.generate_nc_output import *

if cfg.DAsord:
    from modules.user_optional_fns import snd_ord
# TODO: homogenize documentation format

forcing_columns = ['HOUR', 'MINS', 'JDAY', 'YEAR', 'FSIN', 'FLIN', 'PRE', 'TA', 'QA', 'UV', 'PRES', 'PRERN', 'PRESNO']
model_columns = ["year", "month", "day", "hour", "sd", "swe", "Ts", "alb","sigma_13GHz","sigma_17GHz",'sigma_5p4GHz','sigma_diff_13_17','sigma_diff_13_5p4','sigma_diff_17_5p4']


def W19(Ta, QA, Pres):
    a = 6.99e-5
    b = 2
    c = 3.97

    Td = dewpoint_from_specific_humidity(Pres * units.Pa, Ta * units.degC, QA * units('kg/kg')).magnitude
    Tw = wet_bulb_temperature(Pres * units.Pa, Ta * units.degC, Td * units.degC).magnitude
    fr = 1.-1./(1. + a*np.exp(b*(Tw+c)))  # Liquid precipitation fraction

    return fr

def model_run(mbr=-1):

    current_dir = os.getcwd()
    os.chdir(os.path.join(cfg.dir_exp,'Simulation_TestBed','sim_exp'))
    os.system(cfg.mesh_exe)
    os.chdir(current_dir)
    generate_nc_output()
    generate_smrt_output()
    if ((cfg.da_algorithm == "ensemble_OL") & (mbr >= 0)):
        shutil.copyfile(os.path.join(cfg.dir_exp,'Simulation_TestBed','sim_exp','output','out_svs2.nc'), os.path.join(cfg.dir_exp,'Simulation_TestBed','sim_exp','output','out_svs2_'+str(mbr)+'.nc'))


def concat_netcdf_ensemble_outputs(lat_idx, lon_idx):
    # Concat all the vertical profiles at observation times
    var_drop = ['SNOMA','SNODP','SNODEN','SNOALB','WSNO','TSNO_SURF','RSNOW_AC','RAINRATE','SNOWRATE','ISOIL','TPSOIL','WSOIL','TPSOILV']

    ens_list = []
    for num in range(cfg.ensemble_members):
        mbr = xr.open_dataset(os.path.join(cfg.dir_exp,'Simulation_TestBed','sim_exp','output','out_svs2_{}.nc'.format(num)),drop_variables = var_drop)
        ens_list.append(mbr)

    # Remove all the files for clean up
    files_vert = glob.glob(os.path.join(cfg.dir_exp,'Simulation_TestBed','sim_exp','output','out_snow_vert_*.nc'))
    for file in files_vert:
        os.remove(file)

    # Concat all the vertical
    ds = xr.concat(ens_list, dim='mbr', coords = 'all').drop_dims('soil_layer').assign_coords({"mbr": range(cfg.ensemble_members)})

    # Import obs times and filter the output profiles on those datess
    obs = xr.open_dataset(cfg.obs_file).to_dataframe()
    times_obs = obs.index
    ds = ds.sel(time=times_obs)

    # Output combined netcdf
    fileout = os.path.join(cfg.save_ensemble_path,cfg.name_vert_profiles_output+'.nc')
    try:
        os.remove(fileout)
    except OSError:
        pass
    ds.to_netcdf(fileout)



def model_read_output(read_dump=True):
    mod = xr.open_dataset(os.path.join(cfg.dir_exp,'Simulation_TestBed','sim_exp','output','out_svs2.nc'))

    swe = mod['SNOMA'].to_dataframe('swe')
    sd = mod['SNODP'].to_dataframe('snd')
    Ts = mod['TSNO_SURF'].to_dataframe('Ts')
    alb = mod['SNOALB'].to_dataframe('Ts')

    state = pd.concat([sd, swe, Ts, alb], axis=1)
    state.columns = ['sd','swe', 'Ts','alb']

    state['year'] = state.index.year
    state['month'] = state.index.month
    state['day'] = state.index.day
    state['hour'] = state.index.hour

    smrt_out = xr.open_dataset(os.path.join(cfg.dir_exp,'Simulation_TestBed','sim_exp','output','out_smrt.nc')).to_dataframe()
    state = pd.concat([state, smrt_out], axis = 1)

    state = state[model_columns]

    if read_dump:
        dump = pd.read_csv(os.path.join(cfg.dir_exp,'Simulation_TestBed','sim_exp', 'output/restart_svs2.csv'), header = None,delimiter=r"\s+", names = range(50))
        return state, dump
    else:
       return state


def get_var_state_position(var):

    state_columns = model_columns

    return state_columns.index(var)


def model_forcing_wrt(forcing_df, step=0):

    met_forcing_temp = forcing_df.copy()


    frac_liq = W19(met_forcing_temp['TA'].values, met_forcing_temp['QA'].values, met_forcing_temp['PRES'].values)
    PRE = met_forcing_temp['PRE'].values
    PRESNO = PRE * (1.-frac_liq)
    PRERN = PRE * frac_liq
    met_forcing_temp['PRESNO'] = PRESNO
    met_forcing_temp['PRERN'] = PRERN
    met_forcing_temp.to_csv(os.path.join(cfg.dir_exp,'Simulation_TestBed','sim_exp','basin_forcing.met'), sep = ' ', index = False, header = False)

def configure_MESH_parameter(step, dump):

    if step == 0: # Initial run
        os.system('cp '+cfg.dir_exp+'/exp_cfg/param_file/MESH_parameters_stop.txt '+cfg.dir_exp+'/Simulation_TestBed/sim_exp/MESH_parameters.txt')
    else:

        os.system('cp '+cfg.dir_exp+'exp_cfg/param_file/MESH_parameters_restart.txt '+cfg.dir_exp+'/Simulation_TestBed/sim_exp/MESH_parameters.txt')
        dump.to_csv(os.path.join(cfg.dir_exp, 'Simulation_TestBed/sim_exp','MESH_parameters.txt'), mode = 'a', index = False, header=False, sep = '\t')

def configure_options_ini_parameter(step, time_dict):

    os.system('cp '+cfg.dir_exp+'/exp_cfg/MESH_input_soil_levels.txt '+cfg.dir_exp+'/Simulation_TestBed/sim_exp/MESH_input_soil_levels.txt')
    if step == 0:
        time = time_dict['del_t'][time_dict["Assimilaiton_steps"][step]:
                                    time_dict["Assimilaiton_steps"][step + 1]+1]

        time_end = time[-1]

        DATEINI = dt.datetime.strptime(cfg.date_ini, "%Y-%m-%d %H:%M").strftime('%Y%m%d%H')

        os.system('sed "s/year_start/0/g  ; s/day_start/0/g  ; s/hour_start/0/g ; \
            s/year_end/'+str(time_end.year)+'/g  ; s/day_end/'+str(time_end.timetuple().tm_yday)+'/g  ; s/hour_end/'+str(time_end.hour)+'/g \
            ; s/DATEINI/'+str(DATEINI)+'/g" '+cfg.dir_exp+'/exp_cfg/MESH_input_run_options_gen.ini>  '+cfg.dir_exp+'/Simulation_TestBed/sim_exp/MESH_input_run_options.ini')


    else:

        time = time_dict['del_t'][time_dict["Assimilaiton_steps"][step]:
                                    time_dict["Assimilaiton_steps"][step + 1]+1]

        time_start = time[0]
        time_end = time[-1]

        DATEINI = dt.datetime.strptime(cfg.date_ini, "%Y-%m-%d %H:%M").strftime('%Y%m%d%H')

        os.system('sed "s/year_start/'+str(time_start.year)+'/g  ; s/day_start/'+str(time_start.timetuple().tm_yday)+'/g  ; s/hour_start/'+str(time_start.hour)+'/g ; \
            s/year_end/'+str(time_end.year)+'/g  ; s/day_end/'+str(time_end.timetuple().tm_yday)+'/g  ; s/hour_end/'+str(time_end.hour)+'/g\
            ; s/DATEINI/'+str(DATEINI)+'/g" '+ cfg.dir_exp+'/exp_cfg/MESH_input_run_options_gen.ini>  '+cfg.dir_exp+'/Simulation_TestBed/sim_exp/MESH_input_run_options.ini')



def write_dump(dump):
    """
    Parameters
    ----------
    dump : TYPE
        DESCRIPTION.
    fsm_path : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    dump_copy = dump.copy()
    file_name = os.path.join(cfg.dir_exp,'Simulation_TestBed','sim_exp','output', "out_dump")
    dump_copy.iloc[2, 0] = str(int(dump_copy.iloc[2, 0]))
    dump_copy.to_csv(file_name, header=None, index=None, sep=' ', mode='w',
                     na_rep='NaN')


def storeOL(OL_SVS, Ensemble, observations_sbst, time_dict, step):

    ol_data = Ensemble.origin_state.copy()

    # remove time ids from output
    ol_data.drop(ol_data.columns[[0, 1, 2, 3]], axis=1, inplace=True)

    # Store colums
    for n, name_col in enumerate(ol_data.columns):
        OL_SVS[name_col] = ol_data.iloc[:, [n]].to_numpy()


def storeDA(Result_df, step_results, observations_sbst, error_sbst,
            time_dict, step):

    vars_to_perturbate = cfg.vars_to_perturbate
    var_to_assim = cfg.var_to_assim
    error_names = cfg.obs_error_var_names

    rowIndex = Result_df.index[time_dict["Assimilaiton_steps"][step]:
                               time_dict["Assimilaiton_steps"][step + 1]]

    if len(var_to_assim) > 1:
        for i, var in enumerate(var_to_assim):
            Result_df.loc[rowIndex, var] = observations_sbst[:, i]
            Result_df.loc[rowIndex, error_names[i]] = error_sbst[:, i]
    else:
        var = var_to_assim[0]
        Result_df.loc[rowIndex, var] = observations_sbst
        Result_df.loc[rowIndex, error_names[0]] = error_sbst

    # Add perturbation parameters to Results
    for var_p in vars_to_perturbate:
        Result_df.loc[rowIndex, var_p +
                      "_noise_mean"] = step_results[var_p + "_noise_mean"]
        Result_df.loc[rowIndex, var_p +
                      "_noise_sd"] = step_results[var_p + "_noise_sd"]





def store_sim(updated_Sim, sd_Sim, Ensemble,
              time_dict, step, MCMC=False, save_prior=False):

    if MCMC:
        list_state = copy.deepcopy(Ensemble.state_members_mcmc)
    else:
        list_state = copy.deepcopy(Ensemble.state_membres)


    rowIndex = updated_Sim.index[time_dict["Assimilaiton_steps"][step]:
                                 time_dict["Assimilaiton_steps"][step + 1]]

    # Get updated columns
    if save_prior:
        pesos = np.ones_like(Ensemble.wgth)
    else:
        pesos = Ensemble.wgth

    for n, name_col in enumerate(list(list_state[0].columns)):
        # create matrix of colums
        col_arr = [list_state[x].iloc[:, n].to_numpy()
                   for x in range(len(list_state))]
        col_arr = np.vstack(col_arr)

        d1 = DescrStatsW(col_arr, weights=pesos)
        average_sim = d1.mean
        sd_sim = d1.std

        # pdb.set_trace()
        updated_Sim.loc[rowIndex, name_col] = average_sim
        sd_Sim.loc[rowIndex, name_col] = sd_sim


def init_result(del_t, DA=False):

    if DA:
        # Concatenate
        col_names = ["Date"]

        # Create results dataframe
        Results = pd.DataFrame(np.nan, index=range(len(del_t)),
                               columns=col_names)

        Results["Date"] = [x.strftime('%d/%m/%Y-%H:%S') for x in del_t]
        return Results

    else:

        # Create results dataframe
        Results = pd.DataFrame(np.nan, index=range(len(del_t)-1),
                               columns=model_columns)



        Results["year"] = [np.nan for x in del_t[:-1]]
        Results["month"] = [np.nan for x in del_t[:-1]]
        Results["day"] = [np.nan for x in del_t[:-1]]
        Results["hour"] = [np.nan for x in del_t[:-1]]
        Results["sd"] = [np.nan for x in del_t[:-1]]
        Results["swe"] = [np.nan for x in del_t[:-1]]
        Results["Ts"] = [np.nan for x in del_t[:-1]]
        Results["alb"] = [np.nan for x in del_t[:-1]]

        Results = Results.astype({'sd': 'float32',
                                   'swe': 'float32',
                                   'Ts': 'float32',
                                   'alb': 'float32'})

        return Results


