import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
import xarray as xr
from datetime import datetime

import sys
sys.path.append('/fs/homeu2/eccc/mrd/ords/rpnenv/nil005/Codes/smrt')
#from smrt.core.globalconstants import DENSITY_OF_ICE
from smrt import sensor_list, make_model, make_snowpack
from smrt.emmodel import iba
from smrt.substrate.reflector_backscatter import make_reflector

# The functions in this script were taken from the radar_equivalent_snow model from J.Meloche
# https://gitlab.science.gc.ca/tsmm/radar_equivalent_snow

DENSITY_OF_ICE = 917.

# Functions
def debye_eqn(ssa, density):
    return 4. * (1. - density / DENSITY_OF_ICE) / (ssa * DENSITY_OF_ICE)  


def avg_snow_sum_thick(snow_df, method = 'thick', freq = 17.5e9):
    thick = snow_df.thickness.sum()
    if method == 'thick':
        snow_mean = snow_df.apply(lambda x: np.average(x, weights = snow_df.thickness.values), axis =0)
        snow_mean['thickness'] = thick
        return snow_mean
    elif method == 'thick-ke':
        snow_df['ke'] = compute_ke(snow_df, freq = freq)
        snow_mean = snow_df.apply(lambda x: np.average(x, weights = snow_df.thickness.values * snow_df.ke.values), axis =0)
        snow_mean['thickness'] = thick
        return snow_mean
    elif method == 'thick-ke-density':
        snow_df['ke'] = compute_ke(snow_df, freq = freq)
        df_copy = snow_df.copy()
        density_temp = np.average(df_copy.SNODEN_ML, weights = snow_df.thickness.values )
        snow_mean = snow_df.apply(lambda x: np.average(x, weights =  snow_df.thickness.values*snow_df.ke.values, axis =0))
        snow_mean['thickness'] = thick
        snow_mean['SNODEN_ML'] = density_temp
        return snow_mean
    else:
        print('provide a valid method')
        return np.nan



def compute_ke(snow_df, freq = 17.5e9):
    #Creating the snowpack to simulate with the substrate
    if isinstance(snow_df.thickness, np.floating):
        thickness = [snow_df.thickness]
    else:
        thickness = snow_df.thickness

    sp = make_snowpack(thickness=thickness, 
                        microstructure_model='exponential',
                        density= snow_df.SNODEN_ML,
                        temperature= snow_df.TSNOW_ML,
                        corr_length = debye_eqn(np.array(snow_df.SNOSSA_ML), np.array(snow_df.SNODEN_ML)))
    #create sensor
    sensor  = sensor_list.active(freq, 35)
    
    #get ks from IBA class
    ks = np.array([iba.IBA(sensor, layer, dense_snow_correction='auto').ks for layer in sp.layers])
    ka = np.array([iba.IBA(sensor, layer, dense_snow_correction='auto').ka for layer in sp.layers])
    ke = ks + ka
    return ke


def three_layer_k(snow_df, method = 'thick', freq = 17.5e9):

    snow_df = snow_df[snow_df['SNOMA_ML'] > 0].copy()

    if len(snow_df) > 0 :

        #kmean cluster classification of layer
        X = pd.DataFrame({ 'ke' : compute_ke(snow_df, freq =freq),  'height' : snow_df.height})
        kmeans = KMeans(n_clusters=3, random_state=0, n_init="auto").fit(X)
        snow_df['label'] = kmeans.labels_
        
        df = snow_df.groupby('label', sort = False).apply(lambda x: avg_snow_sum_thick(x, method = method, freq =freq))

        df['height'] = np.cumsum(df.thickness[::-1])[::-1]

        return df
    else:
        return snow_df


