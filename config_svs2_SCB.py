#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This is the MuSA configuration file.
Note that not all the options will be used in all the experimental setups.

"""
# Note: not all options have been tested with dIm and snow17
numerical_model = 'svs2'  # model to use from FSM2, dIm or snow17
# -----------------------------------
# Directories
# -----------------------------------

obs_file = "/home/nil005/store6/Driving_Data/Snow_Crested_Butte/MuSA/DATA/obs/obs.nc"
intermediate_path = "./DATA/INTERMEDIATE/"
file_forcing = '/home/nil005/ords/Codes/MuSA/MESH_SVS2_SCB/basin_forcing_org.met'
dir_exp = '/home/nil005/ords/Codes/MuSA/MESH_SVS2_SCB/'
save_ensemble_path = "./DATA/ENSEMBLES/"
output_path = "./DATA/RESULTS/"
tmp_path = None


# If restart_run is enabled, the outputs will not be overwritten
restart_run = False
# If restart_forcing, the forcing will be read from intermediate files
restart_forcing = False

# -----------------------------------
# Data Assim
# -----------------------------------

# da_algorithm from PF, EnKF, IEnKF, PBS, ES, IES, deterministic_OL,
# IES-MCMC_AI, IES-MCMC, AdaMuPBS, AdaPBS or PIES
da_algorithm = 'IEnKF'
redraw_prior = False  # PF and PBS only
max_iterations = 4  # IEnKF, IES, IES-MCMC and AdaPBS
# resampling_algorithm from "bootstrapping", residual_resample,
# stratified_resample,  systematic_resample, no_resampling
resampling_algorithm = "no_resampling"
ensemble_members = 100
Neffthrs = 0.1           # Low Neff threshold


# MCMC parameters
chain_len = 20000   # Length of the mcmcm
adaptive = True    # Update proposal covariance for next step.
histcov = True     # Use posterior IES covariance as proposal covariance
burn_in = 0.1      # discard the first x proportion of samples

# r_cov can be a list of scalars of length equal to var_to_assim or the string
# 'dynamic_error'. If 'dynamic_error' is selected, errors may change in space
# and time. If this option is selected, the errors will be stored in a new
# variable in the observation files, and will have the same dimensions as
# the observations.
r_cov = [0.04]
add_dynamic_noise = False

# var_to_assim from "snd", "SWE", "Tsrf","fSCA", "SCA", "alb", "LE", "H"
var_to_assim = ["snd"]
obs_error_var_names = ['sdError']  # In case of r_cov = 'dynamic_error'

# DA second order variables and/or statistics (experimental)
DAsord = False
DAord_names = ["Ampli"]

# vars_to_perturbate from "SW", "LW", "Prec", "Ta", "RH", "Ua", "PS
vars_to_perturbate = ["TA", "PRE"]

# Name of the variable to assimilate in the observation file
obs_var_names = 'sd_mean'

# In smoothers, re-draw new parameters for each season
season_rejuvenation = [True, True]
# seed to initialise the random number generator
seed = None

# perturbation_strategy from "normal", "lognormal",
# "logitnormal_adi" or "logitnormal_mult"
perturbation_strategy = ["logitnormal_adi", "logitnormal_mult"]

# precipitation_phase from "Harder" or "temp_thld"
#precipitation_phase = "Harder"

# Save ensembles as a pkl object
save_ensemble = False

# -----------------------------------
# Domain
# -----------------------------------

# implementation from "point_scale", "distributed" or "Spatial_propagation"
implementation = "point_scale"

# if implementation = "Spatial_propagation" : specify which observation
# variables are spatially propagated in a list
# if var_to_prop = var_to_assim -> All the variables are spatially propagated
# if var_to_prop = [] -> Any variable is spatially propagated
var_to_prop = var_to_assim

# parallelization from "sequential", "multiprocessing" or "HPC.array"
parallelization = "sequential"
MPI = False  # Note: not tested
nprocess = 8  # Note: if None, the number of processors will be estimated

#aws_lat = 4735225.54  # Latitude in case of point_scale
#aws_lon = 710701.28   # Longitude in case of point_scale

date_ini = "2018-10-01 06:00" # 1h after first time in the basin_forcing
date_end = "2019-06-30 12:00"

season_ini_month = 9  # In smoothers, beginning of DA window (month)
season_ini_day = 1    # In smoothers, beginning of DA window (day)








