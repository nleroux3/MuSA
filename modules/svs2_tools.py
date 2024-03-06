#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Some functions to interact with FSM.

Author: Esteban Alonso González - alonsoe@ipe.csic.es
"""
import os
import shutil
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
if cfg.DAsord:
    from modules.user_optional_fns import snd_ord
# TODO: homogenize documentation format

forcing_columns = ['HOUR', 'MINS', 'JDAY', 'YEAR', 'FSIN', 'FLIN', 'PRE', 'TA', 'QA', 'UV', 'PRES', 'PRERN', 'PRESNO']

model_columns = ["year", "month", "day", "hour", "snd", "SWE", "Tsrf", "alb"]


def model_run():
    os.chdir('/home/nil005/ords/Codes/MuSA/MESH_SVS2_SCB/')
    os.system("python /home/nil005/ords/Codes/MuSA/MESH_SVS2_SCB/run_Ctb.py")
    os.chdir('/home/nil005/ords/Codes/MuSA/')


def model_read_output():


    mod = xr.open_dataset(os.path.join(cfg.dir_exp,'output','out_svs2.nc'))
    
    swe = mod['SNOMA'].to_dataframe('swe')
    sd = mod['SNODP'].to_dataframe('snd')
    Ts = mod['TSNO_SURF'].to_dataframe('Ts')
    alb = mod['SNOALB'].to_dataframe('Ts')

    df = pd.concat([swe, sd, Ts, alb], axis=1)
    df.columns = ['SWE', 'snd','Tsrf','alb']
    
    df['year'] = df.index.year
    df['month'] = df.index.month
    df['day'] = df.index.day
    df['hour'] = df.index.hour


    df = df[model_columns]

    return df
    
    #if read_dump:
    #    return state, dump
    #else:
    #    return state



def get_var_state_position(var):

    state_columns = model_columns

    return state_columns.index(var)


def model_forcing_wrt(forcing_df, step=0):

    met_forcing_temp = forcing_df.copy()


    met_forcing_temp['PRESNO'] = met_forcing_temp[['PRE','TA']].apply(lambda x: x[0] if x[1]<0 else 0, axis = 1)
    met_forcing_temp['PRERN'] = met_forcing_temp[['PRE','TA']].apply(lambda x: x[0] if x[1]>=0 else 0, axis = 1)

    met_forcing_temp.to_csv(os.path.join(cfg.dir_exp,'basin_forcing.met'), sep = ' ', index = False, header = False)



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
    file_name = os.path.join(cfg.dir_exp,'output', "out_dump")
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
        Result_df.loc[rowIndex, error_names] = error_sbst

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
    # remove time ids fomr FSM output
    # TODO: modify directly FSM code to not to output time id's
    for lst in range(len(list_state)):
        data = list_state[lst]
        data.drop(data.columns[[0, 1, 2, 3]], axis=1, inplace=True)

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
        Results = pd.DataFrame(np.nan, index=range(len(del_t)),
                               columns=model_columns)



        Results["year"] = [np.nan for x in del_t]
        Results["month"] = [np.nan for x in del_t]
        Results["day"] = [np.nan for x in del_t]
        Results["hour"] = [np.nan for x in del_t]
        Results["snd"] = [np.nan for x in del_t]
        Results["SWE"] = [np.nan for x in del_t]
        Results["Tsrf"] = [np.nan for x in del_t]
        Results["alb"] = [np.nan for x in del_t]

        Results = Results.astype({'snd': 'float32',
                                   'SWE': 'float32',
                                   'Tsrf': 'float32',
                                   'alb': 'float32'})

        return Results


