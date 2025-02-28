#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: Esteban Alonso González - alonsoe@ipe.csic.es
Updates: Nicolas R. Leroux  - nicolas.leroux@ec.gc.ca
"""

import modules.internal_fns as ifn
import modules.spatialMuSA as spM
import config as cfg
if cfg.numerical_model == 'FSM2':
    import modules.fsm_tools as model
elif cfg.numerical_model == 'dIm':
    import modules.dIm_tools as model
elif cfg.numerical_model == 'snow17':
    import modules.snow17_tools as model
elif cfg.numerical_model == 'svs2':
    import modules.svs2_tools as model
else:
    raise Exception('Model not implemented')
import numpy as np
import sys
from modules.cell_assim import cell_assimilation


def MuSA():


    """
    This is the main function. Here the parallelization scheme and the
    implementation is selected. This function is just a wrapper of the real
    assimilation process, which is encapsulated in the cell_assimilation
    function.

    Raises
    ------
    'Choose an available implementation'
        An available implementation should be choosen.

    'Choose an available parallelization scheme'
        An available parallelization scheme should be choosen.

    -------
    None.

    """
    if cfg.implementation == "point_scale":

        print("Running the assimilation in a single point")
        cell_assimilation(0,0)




if __name__ == "__main__":

    MuSA()


