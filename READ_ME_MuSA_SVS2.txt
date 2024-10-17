1. Create the ‘MuSAenv’ environment
* On Science, load Mamba: https://wiki.cmc.ec.gc.ca/wiki/CMDS/Presentation_Conda_Mamba#References/R%C3%A9f%C3%A9rences
* Create an environment using the available file MuSAenv.yml
* You can also create a kernel that can be used with Jupyter Notebook (c.f. Section Jupyter/Vscode/Ipykernel)

2. First run with MuSA-MESH/SVS2
* Load the MuSA conda environment.
* MuSA requires two files: constant.py and config.py (they currently are symbolic links towards the SVS2 corresponding files)
* For your first rumn, modify the following paths to your own account storage: tmp_path, save_ensemble_path, output_path
* The following output files with be created:
o name_output  contains the default outputs from MuSA (see section Outputs in https://github.com/ealonsogzl/MuSA)
o name_ensemble_output contains the SVS2/SMRT outputs and noises applied to the met forcing for all the members
o name_vert_profiles_output is only created when the option “ensemble_OL” is used to only generate an open loop ensemble. This files contains the all the SVS2-SMRT outputs of all the members.
* Observation files in netcdf containing the variables to assimilate are required. 
o See path obs_file
o New observation files should contain the same observation variables as this file /home/nil005/store6/Driving_Data/MuSA_PF/Prep_data/obs/obs_Powassan_synth_weekly_noLiq.nc. If no value is available for an observation or that observation is not used for the assimilation experiment, put a NaN value. If backscatter is being assimilated (see sigma_... values in the obs file), make sure that the times of the observed backscatters corresponds to times when the vertical profile of snow properties is being outputted (see variable nprofile_day in MESH_parameters) 
* To run MuSA once the files are modified: ‘python main.py’
 
3. Run your own MuSA-SVS2 experiment
* Create an experiment folder with the same folder names and files as /home/nil005/store6/Driving_Data/MuSA_PF_clean
* Modify the appropriate links in the config file.
