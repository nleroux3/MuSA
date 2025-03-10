#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ensemble class.

Author: Esteban Alonso González - alonsoe@ipe.csic.es
"""
import config as cfg
import numpy as np
import pandas as pd
import os, pdb
import shutil
import tempfile
import modules.met_tools as met
import modules.internal_fns as fns
from modules.dask_cluster import start_cluster, close_cluster
from dask import delayed, compute
from dask.distributed import Client
import multiprocessing

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

class SnowEnsemble():
    """
    Main class containing the ensemble of simulations
    (rows are timesteps)
    """

    def __init__(self, lat_idx, lon_idx, time_dict):

        self.members = cfg.ensemble_members
        self.temp_dest = None
        self.time_dict = time_dict
        self.lat_idx = lat_idx
        self.lon_idx = lon_idx
        self.forcing = []
        self.Neff = None

        # Initialize open loop storage lists
        self.origin_state = pd.DataFrame()
        self.origin_dump = []

        # Initialize lists of members
        self.state_membres = [0 for i in range(self.members)]
        self.out_members = [0 for i in range(self.members)]
        self.out_members_ensemble = [0 for i in range(self.members)]
        self.noise = [0 for i in range(self.members)]
        self.resampled_particles = [0 for i in range(self.members)]

        if cfg.da_algorithm in ['EnKF', 'IEnKF', 'ES',
                                'IES', 'IES-MCMC_AI',
                                'IES-MCMC', 'PIES',
                                'AdaPBS', 'AdaMuPBS']:
            self.noise_iter = [0 for i in range(self.members)]
            self.out_members_iter = [0 for i in range(self.members)]

        # Initialize prior weights = 1
        self.wgth = np.ones(self.members)/self.members

        # Initialize step value
        self.step = -1

        # Initialize shape of function
        if cfg.redraw_prior:
            self.func_shape_arr = []

        # Initialize obs and forz
        self.observations = []

        # MCMC storage
        if cfg.da_algorithm in ['IES-MCMC_AI', 'IES-MCMC']:
            self.state_members_mcmc = [0 for i in range(self.members)]
            self.noise_mcmc = [0 for i in range(self.members)]
            self.out_members_mcmc = [0 for i in range(self.members)]
            self.train_parameters = [0 for i in range(cfg.max_iterations+1)]
            self.train_pred = [0 for i in range(cfg.max_iterations+1)]

    def store_train_data(self, parameters, predictions, kalman_iter):

        self.train_parameters[kalman_iter] = parameters.copy()

        self.train_pred[kalman_iter] = predictions.copy()

    def process_run_mbr(self, mbr, step, readGSC, forcing_sbst):

        print('   mbr = ', mbr)

        # Create a temporary folder for the run of each mbr
        tmp_mbr_folder = tempfile.mkdtemp(dir = cfg.tmp_path)
        # Create the output folder
        if not os.path.exists(os.path.join(tmp_mbr_folder,'output')):
            os.makedirs(os.path.join(tmp_mbr_folder,'output'))

        if step == 0 or readGSC:
            if readGSC:

                GSC_path = os.path.join(
                    cfg.spatial_propagation_storage_path,
                    GSC_filename)

                member_forcing, noise_tmp = \
                    met.perturb_parameters(forcing_sbst,
                                            lat_idx=self.lat_idx,
                                            lon_idx=self.lon_idx,
                                            member=mbr, readGSC=True,
                                            GSC_filename=GSC_path)
            else:
                member_forcing, noise_tmp = \
                    met.perturb_parameters(forcing_sbst)


        else:
            # if PBS/PF is used, use the noise
            # of the previous assimilation step or redraw.
            if cfg.da_algorithm in ["PF", "PBS"]:
                if (cfg.redraw_prior):
                    # if redraw, generate new perturbations
                    noise_tmp = met.redraw(self.func_shape_arr)
                    member_forcing, noise_tmp = \
                        met.perturb_parameters(forcing_sbst,
                                                noise=noise_tmp,
                                                update=True)
                elif (cfg.redraw_scratch):
                    # New with SVS2, redraw the noise but different way from initial MuSA redraw code
                    # TODO: Can it be combined with initial MuSA redraw code
                    member_forcing, noise_tmp = \
                        met.perturb_parameters(forcing_sbst)

                else:
                    # Use the posterior parameters
                    noise_tmp = list(self.noise[mbr].values())
                    noise_tmp = np.vstack(noise_tmp)
                    # Take last perturbation values
                    noise_tmp = noise_tmp[:, np.shape(noise_tmp)[1] - 1]
                    member_forcing, noise_tmp = \
                        met.perturb_parameters(forcing_sbst,
                                                noise=noise_tmp,
                                                update=True)
            else:
                if (cfg.redraw_scratch):
                    member_forcing, noise_tmp = \
                        met.perturb_parameters(forcing_sbst)
                else:
                    # if kalman is used, use the posterior noise of the
                    # previous run
                    noise_tmp = list(self.noise_iter[mbr].values())
                    noise_tmp = np.vstack(noise_tmp)
                    # Take last perturbation values
                    noise_tmp = noise_tmp[:, np.shape(noise_tmp)[1] - 1]
                    member_forcing, noise_tmp = \
                        met.perturb_parameters(forcing_sbst,
                                                noise=noise_tmp, update=True)

        # write perturbed forcing
        if cfg.numerical_model in ['FSM2']:
            model.model_forcing_wrt(member_forcing, self.temp_dest, self.step)
        elif cfg.numerical_model in ['svs2']:
            model.model_forcing_wrt(member_forcing, tmp_mbr_folder, self.step)

        if cfg.numerical_model in ['FSM2']:
            if step != 0:
                if cfg.da_algorithm in ['PBS', 'PF']:
                    model.write_dump(self.out_members[mbr], self.temp_dest)
                else:  # if kalman, write updated dump
                    model.write_dump(self.out_members_iter[mbr],
                                        self.temp_dest)

            model.model_run(self.temp_dest)

            state_tmp, dump_tmp = model.model_read_output(self.temp_dest)

        elif cfg.numerical_model in ['dIm', 'snow17']:
            if step != 0:
                if cfg.da_algorithm in ['PBS', 'PF']:
                    state_tmp, dump_tmp =\
                        model.model_run(member_forcing,
                                        self.out_members[mbr])
                else:  # if kalman, write updated dump
                    state_tmp, dump_tmp =\
                        model.model_run(member_forcing,
                                        self.out_members_iter[mbr])
            else:
                state_tmp, dump_tmp =\
                    model.model_run(member_forcing)
        elif cfg.numerical_model in ['svs2']:

            # Reconfigure the MESH parameter with initial snow condictions from previous time step
            if step != 0:
                if cfg.da_algorithm in ['PBS', 'PF']:
                    model.configure_MESH_parameter(self.step, self.out_members[mbr], tmp_mbr_folder)

                else:  # if kalman, write updated dump
                    model.configure_MESH_parameter(self.step, self.out_members_iter[mbr], tmp_mbr_folder)

            else:
                model.configure_MESH_parameter(self.step, np.empty(0), tmp_mbr_folder)

            model.model_run(tmp_mbr_folder, mbr)
            # read model outputs, dump is a df containing the initial conditions/prognostic variables for next step
            state_tmp, dump_tmp = model.model_read_output(tmp_mbr_folder)

        else:
            raise Exception("Numerical model not implemented")

        # Remove temporary folder
        shutil.rmtree(tmp_mbr_folder)

        return mbr, state_tmp, dump_tmp, noise_tmp

    def create(self, forcing_sbst, observations_sbst, error_sbst, step,
               readGSC=False, GSC_filename=None):

        self.step = step
        self.observations = observations_sbst.copy()
        self.errors = error_sbst.copy()
        self.forcing = forcing_sbst.copy()

        # Write init or dump file from previous run if step != 0
        if cfg.numerical_model in ['FSM2']:

            # create temporal FSM2
            self.temp_dest = model.model_copy(self.lat_idx, self.lon_idx)

            model.model_forcing_wrt(forcing_sbst, self.temp_dest, self.step)
            if step != 0:
                model.write_dump(self.origin_dump[step - 1], self.temp_dest)

            # create open loop simulation
            model.model_run(self.temp_dest)

            # read model outputs
            origin_state_tmp, origin_dump_tmp =\
                model.model_read_output(self.temp_dest)

        elif cfg.numerical_model in ['dIm', 'snow17']:
            if step != 0:
                origin_state_tmp, origin_dump_tmp =\
                    model.model_run(forcing_sbst, self.origin_dump[step - 1])
            else:
                origin_state_tmp, origin_dump_tmp =\
                    model.model_run(forcing_sbst)

        elif cfg.numerical_model in ['svs2']:

            # Reconfigure the MESH parameter with initial snow conditions from previous time step
            if step != 0:
                model.configure_MESH_parameter(self.step, self.origin_dump[step - 1], cfg.tmp_path)
            else:
                model.configure_MESH_parameter(self.step, np.empty(0), cfg.tmp_path)

            # Modify and write forcing with perturbation
            model.model_forcing_wrt(forcing_sbst, cfg.tmp_path, self.step)

            # Create output folder in tmp folder if it does not exist
            if not os.path.exists(os.path.join(cfg.tmp_path,'output')):
                os.makedirs(os.path.join(cfg.tmp_path,'output'))
                
            model.model_run(cfg.tmp_path)
            # read model outputs, dump is a df containing the initial conditions for next step
            origin_state_tmp, origin_dump_tmp = model.model_read_output(cfg.tmp_path)

        else:
            raise Exception("Numerical model not implemented")

        # Store model outputs
        self.origin_state = pd.concat([self.origin_state,
                                       origin_state_tmp.copy()])
        self.origin_dump.append(origin_dump_tmp.copy())

        # Avoid ensemble generation if direct insertion
        if cfg.da_algorithm == "direct_insertion":
            return None

        # Ensemble generator
        # TODO: Parallelize this loop
        if cfg.parallelization_mbrs: # parallelization of all the mbrs
            client = start_cluster()
            forcing_sbst_future = client.scatter(forcing_sbst, broadcast=True)  # Broadcast DataFrame

            futures = [delayed(self.process_run_mbr)(m, step, readGSC, forcing_sbst) for m in range(self.members)]
            results = compute(*futures)

        else:

            results = []
            for mbr in range(self.members):
                results.append(self.process_run_mbr(mbr, step, readGSC, forcing_sbst))

        for r in results:
            mbr = r[0]
            state_tmp = r[1]
            dump_tmp = r[2]
            noise_tmp = r[3]

            # store model outputs and perturbation parameters
            self.state_membres[mbr] = state_tmp.copy()

            self.out_members[mbr] = dump_tmp.copy()
            self.out_members_ensemble[mbr] = dump_tmp.copy()

            self.noise[mbr] = noise_tmp.copy()

        close_cluster()  # Ensure any existing cluster is closed

        # Clean tmp directory
        try:
            shutil.rmtree(os.path.split(self.temp_dest)[0], ignore_errors=True)
        except TypeError:
            pass

    def posterior_shape(self):
        func_shape = met.get_shape_from_noise(self.noise,
                                              self.wgth,
                                              self.lowNeff)
        self.func_shape_arr = func_shape
        # Create new perturbation parameters

    def iter_update(self, step=None, updated_pars=None,
                    create=None, iteration=None):

        if create:  # If there is observational data update the ensemble


            # Ensemble generator
            for mbr in range(self.members):

                noise_tmp = updated_pars[:, mbr]
                member_forcing, noise_k_tmp = \
                    met.perturb_parameters(self.forcing, noise=noise_tmp,
                                           update=True)


                if cfg.numerical_model in ['FSM2']:
                    model.model_forcing_wrt(member_forcing, self.temp_dest,
                        self.step)
                    if step != 0:
                        model.write_dump(self.out_members_iter[mbr],
                                         self.temp_dest)

                    model.model_run(self.temp_dest)

                    state_tmp, dump_tmp = model.model_read_output(
                        self.temp_dest)

                elif cfg.numerical_model in ['dIm', 'snow17']:
                    model.model_forcing_wrt(member_forcing, self.temp_dest,
                        self.step)
                    if step != 0:
                        state_tmp, dump_tmp =\
                            model.model_run(member_forcing,
                                            self.out_members_iter[mbr])
                    else:
                        state_tmp, dump_tmp =\
                            model.model_run(member_forcing)



                self.state_membres[mbr] = state_tmp.copy()

                self.noise_iter[mbr] = noise_k_tmp.copy()

                if (iteration == cfg.max_iterations - 1 or
                        cfg.da_algorithm in ['EnKF', 'ES', 'AdaPBS',
                                             'AdaMuPBS']):

                    self.out_members_iter[mbr] = dump_tmp.copy()

            # Clean tmp directory
            try:
                shutil.rmtree(os.path.split(self.temp_dest)
                              [0], ignore_errors=True)
            except TypeError:
                pass

        else:  # if there is not obs data just write the kalman noise
            self.noise_iter = self.noise.copy()
            self.out_members_iter = self.out_members.copy()

    def resample(self, resampled_particles, do_res=True):

        # Particles
        self.out_members = [self.out_members[x].copy() for x in resampled_particles]

        # Noise
        self.noise = [self.noise[x].copy() for x in resampled_particles]

        if cfg.da_algorithm in ['PIES', 'AdaPBS'] and do_res:
            self.noise_iter = [self.noise_iter[x].copy()
                       for x in resampled_particles]

            self.out_members_iter = [self.out_members_iter[x].copy()
                       for x in resampled_particles]

    def season_rejuvenation(self):
        for mbr in range(self.members):
            _, noise_tmp = \
                met.perturb_parameters(self.forcing)
            for cont, condition in enumerate(cfg.season_rejuvenation):
                if condition:

                    self.noise[mbr][cfg.vars_to_perturbate[cont]] =\
                        noise_tmp[cfg.vars_to_perturbate[cont]].copy()

                    try:
                        self.noise_iter[mbr][cfg.vars_to_perturbate[cont]] =\
                            noise_tmp[cfg.vars_to_perturbate[cont]].copy()
                    except AttributeError:
                        pass

    def create_MCMC(self, mcmc_storage, step):

        # create temporal model dir
        self.temp_dest = model.model_copy(self.lat_idx, self.lon_idx)

        # Ensemble generator
        for mbr in range(self.members):

            noise_tmp = mcmc_storage[:, mbr]
            member_forcing, noise_k_tmp = \
                met.perturb_parameters(self.forcing, noise=noise_tmp,
                                       update=True)

            model.model_forcing_wrt(member_forcing, self.temp_dest, self.step)

            if cfg.numerical_model in ['FSM2']:
                if step != 0:

                    model.write_dump(self.out_members_mcmc[mbr],
                                     self.temp_dest)

                model.model_run(self.temp_dest)

                state_tmp, dump_tmp = model.model_read_output(self.temp_dest)

            elif cfg.numerical_model in ['dIm', 'snow17']:
                if step != 0:
                    state_tmp, dump_tmp =\
                        model.model_run(member_forcing,
                                        self.out_members_mcmc[mbr])
                else:
                    state_tmp, dump_tmp =\
                        model.model_run(member_forcing)

            else:
                raise Exception("Numerical model not implemented")

            self.state_members_mcmc[mbr] = state_tmp.copy()
            self.out_members_mcmc[mbr] = dump_tmp.copy()
            self.noise_mcmc[mbr] = noise_k_tmp.copy()

        # Clean tmp directory
        try:
            shutil.rmtree(os.path.split(self.temp_dest)[0], ignore_errors=True)
        except TypeError:
            pass

    def save_space(self):

        self.state_membres = [fns.reduce_size_state(x, self.observations)
                              for x in self.state_membres]
