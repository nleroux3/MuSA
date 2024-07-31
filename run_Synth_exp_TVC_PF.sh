#/bin/bash


# Activate conda environment
. ssmuse-sh -x /fs/ssm/eccc/cmd/cmds/apps/mamba/master/mamba_2024.01.18_all
conda activate MuSAenv


# Run synthetic experiment for TVC
ln -sf constants_svs2_TVC_synth_exp.py constants.py
ln -sf /home/nil005/store6/Driving_Data/MuSA_PF/exp_cfg/param_file/MESH_parameters_TVC_restart.txt /home/nil005/store6/Driving_Data/MuSA_PF/exp_cfg/param_file/MESH_parameters_restart.txt
ln -sf /home/nil005/store6/Driving_Data/MuSA_PF/exp_cfg/param_file/MESH_parameters_TVC_stop.txt /home/nil005/store6/Driving_Data/MuSA_PF/exp_cfg/param_file/MESH_parameters_stop.txt

OUTPUT_FOLDER='/home/nil005/store6/Driving_Data/MuSA_PF/Simulation_TestBed/output_PF'

##########################################################
## OL
##########################################################

DA_ALGORITHM='ensemble_OL'
NB_MEMBERS='100'
VAR_ASSIM="'"sigma_13GHz"'"
R_COV='1'
ERROR_VAR_NAMES="'"sdError"'"

OBS_FILE='/home/nil005/store6/Driving_Data/MuSA_PF/Prep_data/obs/obs_TVC_synth_weekly.nc'
NAME_OUTPUT='cell_TVC_OL_weekly'
NAME_ENSEMBLE_OUTPUT='ensbl_TVC_OL_weekly' 
NAME_VERT_PROFILES_OUTPUT='out_snow_vert_TVC_OL_weekly'
TMP_PATH='/home/nil005/store6/Driving_Data/MuSA_PF/Simulation_TestBed/sim_exp_'$(date +%Y%m%d%H%M%S)

mkdir -p ${TMP_PATH}
mkdir -p ${TMP_PATH}'/output'


sed "s|OBS_FILE|${OBS_FILE}|g; s|NAME_OUTPUT|${NAME_OUTPUT}|g; s|NAME_ENSEMBLE_OUTPUT|${NAME_ENSEMBLE_OUTPUT}|g; s|NAME_VERT_PROFILES_OUTPUT|${NAME_VERT_PROFILES_OUTPUT}|g; s|DA_ALGORITHM|${DA_ALGORITHM}|g; s|NB_MEMBERS|${NB_MEMBERS}|g ; s|VAR_ASSIM|${VAR_ASSIM}|g; s|ERROR_VAR_NAMES|${ERROR_VAR_NAMES}|g ; s|R_COV|${R_COV}|g; s|TMP_PATH|${TMP_PATH}|g" config_svs2_TVC_synth_exp.py >  config.py

### Run the data assimilation if output file does not exist - might need to be commented
if [ ! -f $OUTPUT_FOLDER/$NAME_ENSEMBLE_OUTPUT.pkl.blp ]; then
    echo "$NAME_ENSEMBLE_OUTPUT does not exists"
    python main_svs2.py &
    sleep 60
fi


##########################################################
## Assimilating sigma_13GHz
##########################################################

DA_ALGORITHM='PF'
NB_MEMBERS='100'
VAR_ASSIM="'"sigma_13GHz"'"
R_COV='1'
ERROR_VAR_NAMES="'"sdError"'"

OBS_FILE='/home/nil005/store6/Driving_Data/MuSA_PF/Prep_data/obs/obs_TVC_synth_weekly.nc'
NAME_OUTPUT='cell_TVC_PF_13GHz_weekly'
NAME_ENSEMBLE_OUTPUT='ensbl_TVC_PF_13GHz_weekly' 
NAME_VERT_PROFILES_OUTPUT='out_snow_vert_TVC_PF_13GHz_weekly'
TMP_PATH='/home/nil005/store6/Driving_Data/MuSA_PF/Simulation_TestBed/sim_exp_'$(date +%Y%m%d%H%M%S)

mkdir -p ${TMP_PATH}
mkdir -p ${TMP_PATH}'/output'


sed "s|OBS_FILE|${OBS_FILE}|g; s|NAME_OUTPUT|${NAME_OUTPUT}|g; s|NAME_ENSEMBLE_OUTPUT|${NAME_ENSEMBLE_OUTPUT}|g; s|NAME_VERT_PROFILES_OUTPUT|${NAME_VERT_PROFILES_OUTPUT}|g; s|DA_ALGORITHM|${DA_ALGORITHM}|g; s|NB_MEMBERS|${NB_MEMBERS}|g ; s|VAR_ASSIM|${VAR_ASSIM}|g; s|ERROR_VAR_NAMES|${ERROR_VAR_NAMES}|g ; s|R_COV|${R_COV}|g; s|TMP_PATH|${TMP_PATH}|g" config_svs2_TVC_synth_exp.py >  config.py

### Run the data assimilation if output file does not exist - might need to be commented
if [ ! -f $OUTPUT_FOLDER/$NAME_ENSEMBLE_OUTPUT.pkl.blp ]; then
    echo "$NAME_ENSEMBLE_OUTPUT does not exists"
    python main_svs2.py &
    sleep 60
fi


##########################################################
## Assimilating sigma_17GHz
##########################################################

DA_ALGORITHM='PF'
NB_MEMBERS='100'
VAR_ASSIM="'"sigma_17GHz"'"
R_COV='1'
ERROR_VAR_NAMES="'"sdError"'"

OBS_FILE='/home/nil005/store6/Driving_Data/MuSA_PF/Prep_data/obs/obs_TVC_synth_weekly.nc'
NAME_OUTPUT='cell_TVC_PF_17GHz_weekly'
NAME_ENSEMBLE_OUTPUT='ensbl_TVC_PF_17GHz_weekly' 
NAME_VERT_PROFILES_OUTPUT='out_snow_vert_TVC_PF_17GHz_weekly'
TMP_PATH='/home/nil005/store6/Driving_Data/MuSA_PF/Simulation_TestBed/sim_exp_'$(date +%Y%m%d%H%M%S)

mkdir -p ${TMP_PATH}
mkdir -p ${TMP_PATH}'/output'


sed "s|OBS_FILE|${OBS_FILE}|g; s|NAME_OUTPUT|${NAME_OUTPUT}|g; s|NAME_ENSEMBLE_OUTPUT|${NAME_ENSEMBLE_OUTPUT}|g; s|NAME_VERT_PROFILES_OUTPUT|${NAME_VERT_PROFILES_OUTPUT}|g; s|DA_ALGORITHM|${DA_ALGORITHM}|g; s|NB_MEMBERS|${NB_MEMBERS}|g ; s|VAR_ASSIM|${VAR_ASSIM}|g; s|ERROR_VAR_NAMES|${ERROR_VAR_NAMES}|g ; s|R_COV|${R_COV}|g; s|TMP_PATH|${TMP_PATH}|g" config_svs2_TVC_synth_exp.py >  config.py


### Run the data assimilation if output file does not exist - might need to be commented
if [ ! -f $OUTPUT_FOLDER/$NAME_ENSEMBLE_OUTPUT.pkl.blp ]; then
    echo "$NAME_ENSEMBLE_OUTPUT does not exists"
    python main_svs2.py &
    sleep 60
fi


##########################################################
## Assimilating difference sigma_13GHz and sigma_17GHz
##########################################################
DA_ALGORITHM='PF'
NB_MEMBERS='100'
VAR_ASSIM="'"sigma_diff_13_17"'"
R_COV='1'
ERROR_VAR_NAMES="'"sdError"'"

OBS_FILE='/home/nil005/store6/Driving_Data/MuSA_PF/Prep_data/obs/obs_TVC_synth_weekly.nc'
NAME_OUTPUT='cell_TVC_PF_diff_13_17_weekly'
NAME_ENSEMBLE_OUTPUT='ensbl_TVC_PF_diff_13_17_weekly' 
NAME_VERT_PROFILES_OUTPUT='out_snow_vert_TVC_PF_diff_13_17_weekly'
TMP_PATH='/home/nil005/store6/Driving_Data/MuSA_PF/Simulation_TestBed/sim_exp_'$(date +%Y%m%d%H%M%S)

mkdir -p ${TMP_PATH}
mkdir -p ${TMP_PATH}'/output'


sed "s|OBS_FILE|${OBS_FILE}|g; s|NAME_OUTPUT|${NAME_OUTPUT}|g; s|NAME_ENSEMBLE_OUTPUT|${NAME_ENSEMBLE_OUTPUT}|g; s|NAME_VERT_PROFILES_OUTPUT|${NAME_VERT_PROFILES_OUTPUT}|g; s|DA_ALGORITHM|${DA_ALGORITHM}|g; s|NB_MEMBERS|${NB_MEMBERS}|g ; s|VAR_ASSIM|${VAR_ASSIM}|g; s|ERROR_VAR_NAMES|${ERROR_VAR_NAMES}|g ; s|R_COV|${R_COV}|g; s|TMP_PATH|${TMP_PATH}|g" config_svs2_TVC_synth_exp.py >  config.py

### Run the data assimilation if output file does not exist - might need to be commented
if [ ! -f $OUTPUT_FOLDER/$NAME_ENSEMBLE_OUTPUT.pkl.blp ]; then
    echo "$NAME_ENSEMBLE_OUTPUT does not exists"
    python main_svs2.py &
    sleep 60
fi


##########################################################
## Assimilating difference sigma_13GHz and sigma_5.4GHz
##########################################################
DA_ALGORITHM='PF'
NB_MEMBERS='100'
VAR_ASSIM="'"sigma_diff_13_5p4"'"
R_COV='1'
ERROR_VAR_NAMES="'"sdError"'"

OBS_FILE='/home/nil005/store6/Driving_Data/MuSA_PF/Prep_data/obs/obs_TVC_synth_weekly.nc'
NAME_OUTPUT='cell_TVC_PF_diff_13_5p4_weekly'
NAME_ENSEMBLE_OUTPUT='ensbl_TVC_PF_diff_13_5p4_weekly' 
NAME_VERT_PROFILES_OUTPUT='out_snow_vert_TVC_PF_diff_13_5p4_weekly'
TMP_PATH='/home/nil005/store6/Driving_Data/MuSA_PF/Simulation_TestBed/sim_exp_'$(date +%Y%m%d%H%M%S)

mkdir -p ${TMP_PATH}
mkdir -p ${TMP_PATH}'/output'


sed "s|OBS_FILE|${OBS_FILE}|g; s|NAME_OUTPUT|${NAME_OUTPUT}|g; s|NAME_ENSEMBLE_OUTPUT|${NAME_ENSEMBLE_OUTPUT}|g; s|NAME_VERT_PROFILES_OUTPUT|${NAME_VERT_PROFILES_OUTPUT}|g; s|DA_ALGORITHM|${DA_ALGORITHM}|g; s|NB_MEMBERS|${NB_MEMBERS}|g ; s|VAR_ASSIM|${VAR_ASSIM}|g; s|ERROR_VAR_NAMES|${ERROR_VAR_NAMES}|g ; s|R_COV|${R_COV}|g; s|TMP_PATH|${TMP_PATH}|g" config_svs2_TVC_synth_exp.py >  config.py

### Run the data assimilation if output file does not exist - might need to be commented
if [ ! -f $OUTPUT_FOLDER/$NAME_ENSEMBLE_OUTPUT.pkl.blp ]; then
    echo "$NAME_ENSEMBLE_OUTPUT does not exists"
    python main_svs2.py &
    sleep 60
fi


##########################################################
## Assimilating difference sigma_17GHz and sigma_5p4GHz
##########################################################
DA_ALGORITHM='PF'
NB_MEMBERS='100'
VAR_ASSIM="'"sigma_diff_17_5p4"'"
R_COV='1'
ERROR_VAR_NAMES="'"sdError"'"

OBS_FILE='/home/nil005/store6/Driving_Data/MuSA_PF/Prep_data/obs/obs_TVC_synth_weekly.nc'
NAME_OUTPUT='cell_TVC_PF_diff_17_5p4_weekly'
NAME_ENSEMBLE_OUTPUT='ensbl_TVC_PF_diff_17_5p4_weekly' 
NAME_VERT_PROFILES_OUTPUT='out_snow_vert_TVC_PF_diff_17_5p4_weekly'
TMP_PATH='/home/nil005/store6/Driving_Data/MuSA_PF/Simulation_TestBed/sim_exp_'$(date +%Y%m%d%H%M%S)

mkdir -p ${TMP_PATH}
mkdir -p ${TMP_PATH}'/output'


sed "s|OBS_FILE|${OBS_FILE}|g; s|NAME_OUTPUT|${NAME_OUTPUT}|g; s|NAME_ENSEMBLE_OUTPUT|${NAME_ENSEMBLE_OUTPUT}|g; s|NAME_VERT_PROFILES_OUTPUT|${NAME_VERT_PROFILES_OUTPUT}|g; s|DA_ALGORITHM|${DA_ALGORITHM}|g; s|NB_MEMBERS|${NB_MEMBERS}|g ; s|VAR_ASSIM|${VAR_ASSIM}|g; s|ERROR_VAR_NAMES|${ERROR_VAR_NAMES}|g ; s|R_COV|${R_COV}|g; s|TMP_PATH|${TMP_PATH}|g" config_svs2_TVC_synth_exp.py >  config.py

### Run the data assimilation if output file does not exist - might need to be commented
if [ ! -f $OUTPUT_FOLDER/$NAME_ENSEMBLE_OUTPUT.pkl.blp ]; then
    echo "$NAME_ENSEMBLE_OUTPUT does not exists"
    python main_svs2.py &
    sleep 60
fi


##########################################################
## Assimilating sigma_13GHz and sigma_17GHz
##########################################################

DA_ALGORITHM='PF'
NB_MEMBERS='100'
VAR_ASSIM="'"sigma_13GHz"'","'"sigma_17GHz"'"
R_COV='1,1'
ERROR_VAR_NAMES="'"sdError_13GHz"'","'"sdError_17GHz"'"


OBS_FILE='/home/nil005/store6/Driving_Data/MuSA_PF/Prep_data/obs/obs_TVC_synth_weekly.nc'
NAME_OUTPUT='cell_TVC_PF_13GHz_17GHz_weekly'
NAME_ENSEMBLE_OUTPUT='ensbl_TVC_PF_13GHz_17GHz_weekly' 
NAME_VERT_PROFILES_OUTPUT='out_snow_vert_TVC_PF_13GHz_17GHz_weekly'
TMP_PATH='/home/nil005/store6/Driving_Data/MuSA_PF/Simulation_TestBed/sim_exp_'$(date +%Y%m%d%H%M%S)

mkdir -p ${TMP_PATH}
mkdir -p ${TMP_PATH}'/output'


sed "s|OBS_FILE|${OBS_FILE}|g; s|NAME_OUTPUT|${NAME_OUTPUT}|g; s|NAME_ENSEMBLE_OUTPUT|${NAME_ENSEMBLE_OUTPUT}|g; s|NAME_VERT_PROFILES_OUTPUT|${NAME_VERT_PROFILES_OUTPUT}|g; s|DA_ALGORITHM|${DA_ALGORITHM}|g; s|NB_MEMBERS|${NB_MEMBERS}|g ; s|VAR_ASSIM|${VAR_ASSIM}|g; s|ERROR_VAR_NAMES|${ERROR_VAR_NAMES}|g ; s|R_COV|${R_COV}|g; s|TMP_PATH|${TMP_PATH}|g" config_svs2_TVC_synth_exp.py >  config.py

### Run the data assimilation if output file does not exist - might need to be commented
if [ ! -f $OUTPUT_FOLDER/$NAME_ENSEMBLE_OUTPUT.pkl.blp ]; then
    echo "$NAME_ENSEMBLE_OUTPUT does not exists"
    python main_svs2.py &
    sleep 60
fi


##########################################################
## Assimilating sigma_13GHz, sigma_17GHz, sigma_5p4GHz
##########################################################

DA_ALGORITHM='PF'
NB_MEMBERS='100'
VAR_ASSIM="'"sigma_13GHz"'","'"sigma_17GHz"'","'"sigma_5p4GHz"'"
R_COV='1,1,1'
ERROR_VAR_NAMES="'"sdError_13GHz"'","'"sdError_17GHz"'","'"sigma_5p4GHz"'"


OBS_FILE='/home/nil005/store6/Driving_Data/MuSA_PF/Prep_data/obs/obs_TVC_synth_weekly.nc'
NAME_OUTPUT='cell_TVC_PF_13GHz_17GHz_5p4GHz_weekly'
NAME_ENSEMBLE_OUTPUT='ensbl_TVC_PF_13GHz_17GHz_5p4GHz_weekly' 
NAME_VERT_PROFILES_OUTPUT='out_snow_vert_TVC_PF_13GHz_17GHz_5p4GHz_weekly'
TMP_PATH='/home/nil005/store6/Driving_Data/MuSA_PF/Simulation_TestBed/sim_exp_'$(date +%Y%m%d%H%M%S)

mkdir -p ${TMP_PATH}
mkdir -p ${TMP_PATH}'/output'


sed "s|OBS_FILE|${OBS_FILE}|g; s|NAME_OUTPUT|${NAME_OUTPUT}|g; s|NAME_ENSEMBLE_OUTPUT|${NAME_ENSEMBLE_OUTPUT}|g; s|NAME_VERT_PROFILES_OUTPUT|${NAME_VERT_PROFILES_OUTPUT}|g; s|DA_ALGORITHM|${DA_ALGORITHM}|g; s|NB_MEMBERS|${NB_MEMBERS}|g ; s|VAR_ASSIM|${VAR_ASSIM}|g; s|ERROR_VAR_NAMES|${ERROR_VAR_NAMES}|g ; s|R_COV|${R_COV}|g; s|TMP_PATH|${TMP_PATH}|g" config_svs2_TVC_synth_exp.py >  config.py

### Run the data assimilation if output file does not exist - might need to be commented
if [ ! -f $OUTPUT_FOLDER/$NAME_ENSEMBLE_OUTPUT.pkl.blp ]; then
    echo "$NAME_ENSEMBLE_OUTPUT does not exists"
    python main_svs2.py &
    sleep 60
fi


##########################################################
## Assimilating sigma_13GHz and difference sigma_13GHz and sigma_17GHz
##########################################################
DA_ALGORITHM='PF'
NB_MEMBERS='100'
VAR_ASSIM="'"sigma_13GHz"'","'"sigma_diff_13_17"'"
R_COV='1,1'
ERROR_VAR_NAMES="'"sdError_13GHz"'","'"sdError_diff_13_17"'"

OBS_FILE='/home/nil005/store6/Driving_Data/MuSA_PF/Prep_data/obs/obs_TVC_synth_weekly.nc'
NAME_OUTPUT='cell_TVC_PF_13_diff_13_17_weekly'
NAME_ENSEMBLE_OUTPUT='ensbl_TVC_PF_13_diff_13_17_weekly' 
NAME_VERT_PROFILES_OUTPUT='out_snow_vert_TVC_PF_13_diff_13_17_weekly'
TMP_PATH='/home/nil005/store6/Driving_Data/MuSA_PF/Simulation_TestBed/sim_exp_'$(date +%Y%m%d%H%M%S)

mkdir -p ${TMP_PATH}
mkdir -p ${TMP_PATH}'/output'


sed "s|OBS_FILE|${OBS_FILE}|g; s|NAME_OUTPUT|${NAME_OUTPUT}|g; s|NAME_ENSEMBLE_OUTPUT|${NAME_ENSEMBLE_OUTPUT}|g; s|NAME_VERT_PROFILES_OUTPUT|${NAME_VERT_PROFILES_OUTPUT}|g; s|DA_ALGORITHM|${DA_ALGORITHM}|g; s|NB_MEMBERS|${NB_MEMBERS}|g ; s|VAR_ASSIM|${VAR_ASSIM}|g; s|ERROR_VAR_NAMES|${ERROR_VAR_NAMES}|g ; s|R_COV|${R_COV}|g; s|TMP_PATH|${TMP_PATH}|g" config_svs2_TVC_synth_exp.py >  config.py

### Run the data assimilation if output file does not exist - might need to be commented
if [ ! -f $OUTPUT_FOLDER/$NAME_ENSEMBLE_OUTPUT.pkl.blp ]; then
    echo "$NAME_ENSEMBLE_OUTPUT does not exists"
    python main_svs2.py &
    sleep 60
fi


##########################################################
## Assimilating sigma_17GHz and difference sigma_13GHz and sigma_17GHz
##########################################################
DA_ALGORITHM='PF'
NB_MEMBERS='100'
VAR_ASSIM="'"sigma_17GHz"'","'"sigma_diff_13_17"'"
R_COV='1,1'
ERROR_VAR_NAMES="'"sdError_17GHz"'","'"sdError_diff_13_17"'"

OBS_FILE='/home/nil005/store6/Driving_Data/MuSA_PF/Prep_data/obs/obs_TVC_synth_weekly.nc'
NAME_OUTPUT='cell_TVC_PF_17_diff_13_17_weekly'
NAME_ENSEMBLE_OUTPUT='ensbl_TVC_PF_17_diff_13_17_weekly' 
NAME_VERT_PROFILES_OUTPUT='out_snow_vert_TVC_PF_17_diff_13_17_weekly'
TMP_PATH='/home/nil005/store6/Driving_Data/MuSA_PF/Simulation_TestBed/sim_exp_'$(date +%Y%m%d%H%M%S)

mkdir -p ${TMP_PATH}
mkdir -p ${TMP_PATH}'/output'


sed "s|OBS_FILE|${OBS_FILE}|g; s|NAME_OUTPUT|${NAME_OUTPUT}|g; s|NAME_ENSEMBLE_OUTPUT|${NAME_ENSEMBLE_OUTPUT}|g; s|NAME_VERT_PROFILES_OUTPUT|${NAME_VERT_PROFILES_OUTPUT}|g; s|DA_ALGORITHM|${DA_ALGORITHM}|g; s|NB_MEMBERS|${NB_MEMBERS}|g ; s|VAR_ASSIM|${VAR_ASSIM}|g; s|ERROR_VAR_NAMES|${ERROR_VAR_NAMES}|g ; s|R_COV|${R_COV}|g; s|TMP_PATH|${TMP_PATH}|g" config_svs2_TVC_synth_exp.py >  config.py

### Run the data assimilation if output file does not exist - might need to be commented
if [ ! -f $OUTPUT_FOLDER/$NAME_ENSEMBLE_OUTPUT.pkl.blp ]; then
    echo "$NAME_ENSEMBLE_OUTPUT does not exists"
    python main_svs2.py &
    sleep 60
fi


##########################################################
## Assimilating SWE
##########################################################

DA_ALGORITHM='PF'
NB_MEMBERS='100'
VAR_ASSIM="'"swe"'"
R_COV='100'
ERROR_VAR_NAMES="'"sdError"'"


OBS_FILE='/home/nil005/store6/Driving_Data/MuSA_PF/Prep_data/obs/obs_TVC_synth_weekly.nc'
NAME_OUTPUT='cell_TVC_PF_swe_weekly'
NAME_ENSEMBLE_OUTPUT='ensbl_TVC_PF_swe_weekly' 
NAME_VERT_PROFILES_OUTPUT='out_snow_vert_TVC_PF_swe_weekly'
TMP_PATH='/home/nil005/store6/Driving_Data/MuSA_PF/Simulation_TestBed/sim_exp_'$(date +%Y%m%d%H%M%S)

mkdir -p ${TMP_PATH}
mkdir -p ${TMP_PATH}'/output'


sed "s|OBS_FILE|${OBS_FILE}|g; s|NAME_OUTPUT|${NAME_OUTPUT}|g; s|NAME_ENSEMBLE_OUTPUT|${NAME_ENSEMBLE_OUTPUT}|g; s|NAME_VERT_PROFILES_OUTPUT|${NAME_VERT_PROFILES_OUTPUT}|g; s|DA_ALGORITHM|${DA_ALGORITHM}|g; s|NB_MEMBERS|${NB_MEMBERS}|g ; s|VAR_ASSIM|${VAR_ASSIM}|g; s|ERROR_VAR_NAMES|${ERROR_VAR_NAMES}|g ; s|R_COV|${R_COV}|g; s|TMP_PATH|${TMP_PATH}|g" config_svs2_TVC_synth_exp.py >  config.py

### Run the data assimilation if output file does not exist - might need to be commented
if [ ! -f $OUTPUT_FOLDER/$NAME_ENSEMBLE_OUTPUT.pkl.blp ]; then
    echo "$NAME_ENSEMBLE_OUTPUT does not exists"
    python main_svs2.py &
    sleep 60
fi


##########################################################
## Assimilating SD
##########################################################

DA_ALGORITHM='PF'
NB_MEMBERS='100'
VAR_ASSIM="'"sd"'"
R_COV='0.003'
ERROR_VAR_NAMES="'"sdError"'"


OBS_FILE='/home/nil005/store6/Driving_Data/MuSA_PF/Prep_data/obs/obs_TVC_synth_weekly.nc'
NAME_OUTPUT='cell_TVC_PF_sd_weekly'
NAME_ENSEMBLE_OUTPUT='ensbl_TVC_PF_sd_weekly' 
NAME_VERT_PROFILES_OUTPUT='out_snow_vert_TVC_PF_sd_weekly'
TMP_PATH='/home/nil005/store6/Driving_Data/MuSA_PF/Simulation_TestBed/sim_exp_'$(date +%Y%m%d%H%M%S)

mkdir -p ${TMP_PATH}
mkdir -p ${TMP_PATH}'/output'


sed "s|OBS_FILE|${OBS_FILE}|g; s|NAME_OUTPUT|${NAME_OUTPUT}|g; s|NAME_ENSEMBLE_OUTPUT|${NAME_ENSEMBLE_OUTPUT}|g; s|NAME_VERT_PROFILES_OUTPUT|${NAME_VERT_PROFILES_OUTPUT}|g; s|DA_ALGORITHM|${DA_ALGORITHM}|g; s|NB_MEMBERS|${NB_MEMBERS}|g ; s|VAR_ASSIM|${VAR_ASSIM}|g; s|ERROR_VAR_NAMES|${ERROR_VAR_NAMES}|g ; s|R_COV|${R_COV}|g; s|TMP_PATH|${TMP_PATH}|g" config_svs2_TVC_synth_exp.py >  config.py

### Run the data assimilation if output file does not exist - might need to be commented
if [ ! -f $OUTPUT_FOLDER/$NAME_ENSEMBLE_OUTPUT.pkl.blp ]; then
    echo "$NAME_ENSEMBLE_OUTPUT does not exists"
    python main_svs2.py &
    sleep 60
fi



wait
rm -r /home/nil005/store6/Driving_Data/MuSA_PF/Simulation_TestBed/sim_exp_*

