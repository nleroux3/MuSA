#/bin/bash


# Activate conda environment
. ssmuse-sh -x /fs/ssm/eccc/cmd/cmds/apps/mamba/master/mamba_2024.01.18_all
conda activate MuSAenv

# Run synthetic experiment for Powassan
ln -sf constants_svs2_Powassan_synth_exp.py constants.py

## Assimilating simga_13GHz
DA_ALGORITHM='PF'
NB_MEMBERS='100'
VAR_ASSIM='sigma_13GHz'

OBS_FILE='/home/nil005/store6/Driving_Data/MuSA_PF/Prep_data/obs/obs_Powassan_synth_2times.nc'
NAME_OUTPUT='cell_Powassan_PF_13GHz_2times'
NAME_ENSEMBLE_OUTPUT='ensbl_Powassan_PF_13GHz_2times' 
NAME_VERT_PROFILES_OUTPUT='out_snow_vert_Powassan_PF_13GHz_2times'


sed "s|OBS_FILE|$OBS_FILE|g; s|NAME_OUTPUT|$NAME_OUTPUT|g; s|NAME_ENSEMBLE_OUTPUT|$NAME_ENSEMBLE_OUTPUT|g; s|NAME_VERT_PROFILES_OUTPUT|$NAME_VERT_PROFILES_OUTPUT|g; s|DA_ALGORITHM|$DA_ALGORITHM|g; s|NB_MEMBERS|$NB_MEMBERS|g ; s|VAR_ASSIM|$VAR_ASSIM|g" config_svs2_Powassan_synth_exp.py >  config.py

### Run the data assimilation
python main_svs2.py

## Assimilating simga_17GHz
DA_ALGORITHM='PF'
NB_MEMBERS='100'
VAR_ASSIM='sigma_17GHz'

OBS_FILE='/home/nil005/store6/Driving_Data/MuSA_PF/Prep_data/obs/obs_Powassan_synth_2times.nc'
NAME_OUTPUT='cell_Powassan_PF_17GHz_2times'
NAME_ENSEMBLE_OUTPUT='ensbl_Powassan_PF_17GHz_2times' 
NAME_VERT_PROFILES_OUTPUT='out_snow_vert_Powassan_PF_17GHz_2times'


sed "s|OBS_FILE|$OBS_FILE|g; s|NAME_OUTPUT|$NAME_OUTPUT|g; s|NAME_ENSEMBLE_OUTPUT|$NAME_ENSEMBLE_OUTPUT|g; s|NAME_VERT_PROFILES_OUTPUT|$NAME_VERT_PROFILES_OUTPUT|g; s|DA_ALGORITHM|$DA_ALGORITHM|g; s|NB_MEMBERS|$NB_MEMBERS|g ; s|VAR_ASSIM|$VAR_ASSIM|g" config_svs2_Powassan_synth_exp.py >  config.py



### Run the data assimilation
python main_svs2.py

## Assimilating simga_17GHz
DA_ALGORITHM='PF'
NB_MEMBERS='100'
VAR_ASSIM='sigma_diff_13_17'

OBS_FILE='/home/nil005/store6/Driving_Data/MuSA_PF/Prep_data/obs/obs_Powassan_synth_2times.nc'
NAME_OUTPUT='cell_Powassan_PF_diff_13_17_2times'
NAME_ENSEMBLE_OUTPUT='ensbl_Powassan_PF_diff_13_17_2times' 
NAME_VERT_PROFILES_OUTPUT='out_snow_vert_Powassan_PF_diff_13_17_2times'


sed "s|OBS_FILE|$OBS_FILE|g; s|NAME_OUTPUT|$NAME_OUTPUT|g; s|NAME_ENSEMBLE_OUTPUT|$NAME_ENSEMBLE_OUTPUT|g; s|NAME_VERT_PROFILES_OUTPUT|$NAME_VERT_PROFILES_OUTPUT|g; s|DA_ALGORITHM|$DA_ALGORITHM|g; s|NB_MEMBERS|$NB_MEMBERS|g ; s|VAR_ASSIM|$VAR_ASSIM|g" config_svs2_Powassan_synth_exp.py >  config.py

### Run the data assimilation
python main_svs2.py


## Assimilating simga_17GHz
DA_ALGORITHM='PF'
NB_MEMBERS='100'
VAR_ASSIM='sigma_diff_17_13'

OBS_FILE='/home/nil005/store6/Driving_Data/MuSA_PF/Prep_data/obs/obs_Powassan_synth_2times.nc'
NAME_OUTPUT='cell_Powassan_PF_diff_17_13_2times'
NAME_ENSEMBLE_OUTPUT='ensbl_Powassan_PF_diff_17_13_2times' 
NAME_VERT_PROFILES_OUTPUT='out_snow_vert_Powassan_PF_diff_17_13_2times'


sed "s|OBS_FILE|$OBS_FILE|g; s|NAME_OUTPUT|$NAME_OUTPUT|g; s|NAME_ENSEMBLE_OUTPUT|$NAME_ENSEMBLE_OUTPUT|g; s|NAME_VERT_PROFILES_OUTPUT|$NAME_VERT_PROFILES_OUTPUT|g; s|DA_ALGORITHM|$DA_ALGORITHM|g; s|NB_MEMBERS|$NB_MEMBERS|g ; s|VAR_ASSIM|$VAR_ASSIM|g" config_svs2_Powassan_synth_exp.py >  config.py

### Run the data assimilation
python main_svs2.py




