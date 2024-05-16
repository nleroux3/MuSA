#/bin/bash


# Activate conda environment
. ssmuse-sh -x /fs/ssm/eccc/cmd/cmds/apps/mamba/master/mamba_2024.01.18_all
conda activate MuSAenv


# Run synthetic experiment for TVC
ln -sf constants_svs2_TVC_synth_exp.py constants.py
ln -sf /home/nil005/store6/Driving_Data/MuSA_PF/exp_cfg/param_file/MESH_parameters_TVC_restart.txt /home/nil005/store6/Driving_Data/MuSA_PF/exp_cfg/param_file/MESH_parameters_restart.txt
ln -sf /home/nil005/store6/Driving_Data/MuSA_PF/exp_cfg/param_file/MESH_parameters_TVC_stop.txt /home/nil005/store6/Driving_Data/MuSA_PF/exp_cfg/param_file/MESH_parameters_stop.txt

##########################################################
## OL
##########################################################

DA_ALGORITHM='ensemble_OL'
NB_MEMBERS='100'
VAR_ASSIM='sigma_13GHz'

OBS_FILE='/home/nil005/store6/Driving_Data/MuSA_PF/Prep_data/obs/obs_TVC_synth_2times.nc'
NAME_OUTPUT='cell_TVC_OL_2times'
NAME_ENSEMBLE_OUTPUT='ensbl_TVC_OL_2times' 
NAME_VERT_PROFILES_OUTPUT='out_snow_vert_TVC_OL_2times'


sed "s|OBS_FILE|$OBS_FILE|g; s|NAME_OUTPUT|$NAME_OUTPUT|g; s|NAME_ENSEMBLE_OUTPUT|$NAME_ENSEMBLE_OUTPUT|g; s|NAME_VERT_PROFILES_OUTPUT|$NAME_VERT_PROFILES_OUTPUT|g; s|DA_ALGORITHM|$DA_ALGORITHM|g; s|NB_MEMBERS|$NB_MEMBERS|g ; s|VAR_ASSIM|$VAR_ASSIM|g" config_svs2_TVC_synth_exp.py >  config.py

### Run the data assimilation
python main_svs2.py


##########################################################
## Assimilating sigma_13GHz
##########################################################

DA_ALGORITHM='PF'
NB_MEMBERS='100'
VAR_ASSIM='sigma_13GHz'

OBS_FILE='/home/nil005/store6/Driving_Data/MuSA_PF/Prep_data/obs/obs_TVC_synth_2times.nc'
NAME_OUTPUT='cell_TVC_PF_13GHz_2times'
NAME_ENSEMBLE_OUTPUT='ensbl_TVC_PF_13GHz_2times' 
NAME_VERT_PROFILES_OUTPUT='out_snow_vert_TVC_PF_13GHz_2times'


sed "s|OBS_FILE|$OBS_FILE|g; s|NAME_OUTPUT|$NAME_OUTPUT|g; s|NAME_ENSEMBLE_OUTPUT|$NAME_ENSEMBLE_OUTPUT|g; s|NAME_VERT_PROFILES_OUTPUT|$NAME_VERT_PROFILES_OUTPUT|g; s|DA_ALGORITHM|$DA_ALGORITHM|g; s|NB_MEMBERS|$NB_MEMBERS|g ; s|VAR_ASSIM|$VAR_ASSIM|g" config_svs2_TVC_synth_exp.py >  config.py

### Run the data assimilation
python main_svs2.py

##########################################################
## Assimilating sigma_17GHz
##########################################################

DA_ALGORITHM='PF'
NB_MEMBERS='100'
VAR_ASSIM='sigma_17GHz'

OBS_FILE='/home/nil005/store6/Driving_Data/MuSA_PF/Prep_data/obs/obs_TVC_synth_2times.nc'
NAME_OUTPUT='cell_TVC_PF_17GHz_2times'
NAME_ENSEMBLE_OUTPUT='ensbl_TVC_PF_17GHz_2times' 
NAME_VERT_PROFILES_OUTPUT='out_snow_vert_TVC_PF_17GHz_2times'


sed "s|OBS_FILE|$OBS_FILE|g; s|NAME_OUTPUT|$NAME_OUTPUT|g; s|NAME_ENSEMBLE_OUTPUT|$NAME_ENSEMBLE_OUTPUT|g; s|NAME_VERT_PROFILES_OUTPUT|$NAME_VERT_PROFILES_OUTPUT|g; s|DA_ALGORITHM|$DA_ALGORITHM|g; s|NB_MEMBERS|$NB_MEMBERS|g ; s|VAR_ASSIM|$VAR_ASSIM|g" config_svs2_TVC_synth_exp.py >  config.py



### Run the data assimilation
python main_svs2.py


##########################################################
## Assimilating difference sigma_13GHz and sigma_17GHz
##########################################################
DA_ALGORITHM='PF'
NB_MEMBERS='100'
VAR_ASSIM='sigma_diff_13_17'

OBS_FILE='/home/nil005/store6/Driving_Data/MuSA_PF/Prep_data/obs/obs_TVC_synth_2times.nc'
NAME_OUTPUT='cell_TVC_PF_diff_13_17_2times'
NAME_ENSEMBLE_OUTPUT='ensbl_TVC_PF_diff_13_17_2times' 
NAME_VERT_PROFILES_OUTPUT='out_snow_vert_TVC_PF_diff_13_17_2times'


sed "s|OBS_FILE|$OBS_FILE|g; s|NAME_OUTPUT|$NAME_OUTPUT|g; s|NAME_ENSEMBLE_OUTPUT|$NAME_ENSEMBLE_OUTPUT|g; s|NAME_VERT_PROFILES_OUTPUT|$NAME_VERT_PROFILES_OUTPUT|g; s|DA_ALGORITHM|$DA_ALGORITHM|g; s|NB_MEMBERS|$NB_MEMBERS|g ; s|VAR_ASSIM|$VAR_ASSIM|g" config_svs2_TVC_synth_exp.py >  config.py

### Run the data assimilation
python main_svs2.py


##########################################################
## Assimilating difference sigma_13GHz and sigma_5.4GHz
##########################################################
DA_ALGORITHM='PF'
NB_MEMBERS='100'
VAR_ASSIM='sigma_diff_13_5p4'

OBS_FILE='/home/nil005/store6/Driving_Data/MuSA_PF/Prep_data/obs/obs_TVC_synth_2times.nc'
NAME_OUTPUT='cell_TVC_PF_diff_13_5p4_2times'
NAME_ENSEMBLE_OUTPUT='ensbl_TVC_PF_diff_13_5p4_2times' 
NAME_VERT_PROFILES_OUTPUT='out_snow_vert_TVC_PF_diff_13_5p4_2times'


sed "s|OBS_FILE|$OBS_FILE|g; s|NAME_OUTPUT|$NAME_OUTPUT|g; s|NAME_ENSEMBLE_OUTPUT|$NAME_ENSEMBLE_OUTPUT|g; s|NAME_VERT_PROFILES_OUTPUT|$NAME_VERT_PROFILES_OUTPUT|g; s|DA_ALGORITHM|$DA_ALGORITHM|g; s|NB_MEMBERS|$NB_MEMBERS|g ; s|VAR_ASSIM|$VAR_ASSIM|g" config_svs2_TVC_synth_exp.py >  config.py

### Run the data assimilation
python main_svs2.py

##########################################################
## Assimilating difference sigma_17GHz and sigma_5p4GHz
##########################################################
DA_ALGORITHM='PF'
NB_MEMBERS='100'
VAR_ASSIM='sigma_diff_17_5p4'

OBS_FILE='/home/nil005/store6/Driving_Data/MuSA_PF/Prep_data/obs/obs_TVC_synth_2times.nc'
NAME_OUTPUT='cell_TVC_PF_diff_17_5p4_2times'
NAME_ENSEMBLE_OUTPUT='ensbl_TVC_PF_diff_17_5p4_2times' 
NAME_VERT_PROFILES_OUTPUT='out_snow_vert_TVC_PF_diff_17_5p4_2times'


sed "s|OBS_FILE|$OBS_FILE|g; s|NAME_OUTPUT|$NAME_OUTPUT|g; s|NAME_ENSEMBLE_OUTPUT|$NAME_ENSEMBLE_OUTPUT|g; s|NAME_VERT_PROFILES_OUTPUT|$NAME_VERT_PROFILES_OUTPUT|g; s|DA_ALGORITHM|$DA_ALGORITHM|g; s|NB_MEMBERS|$NB_MEMBERS|g ; s|VAR_ASSIM|$VAR_ASSIM|g" config_svs2_TVC_synth_exp.py >  config.py

### Run the data assimilation
python main_svs2.py




