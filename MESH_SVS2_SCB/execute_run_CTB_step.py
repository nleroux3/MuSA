from argparse import ArgumentParser
import os,shutil,pdb

dir_ref = '/home/nil005/store6/Driving_Data/Snow_Crested_Butte/MuSA/DATA/'
    
parser = ArgumentParser(description = """
                                            Script to launch a SVS simulation using for the SCB site
                                            """)

parser.add_argument('-site', help="Site: Ctb", dest='site')
parser.add_argument('-exp', help="Experiment name", dest='exp')
parser.add_argument('-exe', help="MESH executable", dest='exe')
parser.add_argument('-version', help="Version of SVS to consider", dest='version')
parser.add_argument('-type', help="Type of simulation (Open or forest)", dest='type')
parser.add_argument('-lcano', help="Activate SVS canopy module ", dest='lcano')


args = parser.parse_args()

# print(args.type)

# # Create link to parameter file
# if os.path.isfile('MESH_parameters.txt'):
#      os.remove('MESH_parameters.txt')

# if(int(args.lcano)==0):
#      str_cano='.false.'
# else:
#      str_cano='.true.'

# ## Replace LCANO in the file MESH_parameters by either '.false.' or '.true'.
# os.system('sed "s/LCANO/'+str_cano+'/g" '+dir_ref+'/Forcing/MESH_parameters_'+args.site+'_'+args.type+'_'+args.version+'.txt > MESH_parameters.txt')


# # Prepare option file
# if os.path.isfile('MESH_input_run_options.ini'):
#     os.remove('MESH_input_run_options.ini')


# shutil.copy(dir_ref+'/Forcing/MESH_input_run_options_gen.ini','MESH_input_run_options.ini')

# # Copy MESH input soil file
# shutil.copy(dir_ref+'/Forcing/MESH_input_soil_levels.txt','MESH_input_soil_levels.txt')


# # Create link to met forcing file
# os.system('ln -sf '+dir_ref+'/Forcing/basin_forcing_'+args.site+'_'+args.type+'.txt basin_forcing.met')


# # Create experience repository
# dir_exp = dir_ref+'/RESULTS'


# # Create link to experience repository
# if os.path.isdir('./'+'output'):
#     os.remove('./'+'output')
   

# os.symlink(dir_exp,'./'+'output')

# Run MESH
#os.system('./'+args.exe)
os.system(args.exe)

