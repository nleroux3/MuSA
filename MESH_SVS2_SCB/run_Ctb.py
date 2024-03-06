import os

mesh_exe = '/home/nil005/ords/Codes/MESH_SVS/MESH_SVS_master/sa_mesh'

svs_version = 'svs2'

list_site = ['Ctb']

list_type= ['opn'] 

for site in list_site:
    list_exp = []
    for tt in list_type:
            

        # Run simulation 
        exp_name =  "exp_"+tt
        os.system(mesh_exe)
        os.system("python /home/nil005/ords/Codes/MuSA/MESH_SVS2_SCB/generate_nc_output.py -site "+site+" -exp "+exp_name+" -version "+svs_version)
            

                


