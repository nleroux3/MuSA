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
import modules.met_tools as met
import modules.internal_fns as fns


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
        self.noise = [0 for i in range(self.members)]

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

            # Reconfigure the MESH parameter with initial snow condictions from previous time step
            if step != 0:
                model.configure_MESH_parameter(self.step, self.origin_dump[step - 1])
            else:
                model.configure_MESH_parameter(self.step, np.empty(0))


            # Modify and write forcing with perturbation
            model.model_forcing_wrt(forcing_sbst, self.step)

            model.model_run()
            # read model outputs, dump is a df containing the initial conditions for next step
            origin_state_tmp, origin_dump_tmp = model.model_read_output()

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
        for mbr in range(self.members):

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
                model.model_forcing_wrt(member_forcing, self.step)

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
                # if step != 0:
                #     if cfg.da_algorithm in ['PBS', 'PF']:
                #         model.write_dump(self.out_members[mbr])
                #     else:  # if kalman, write updated dump
                #         model.write_dump(self.out_members_iter[mbr])

                # Reconfigure the MESH parameter with initial snow condictions from previous time step
                if step != 0:
                    model.configure_MESH_parameter(self.step, self.out_members[mbr])
                else:
                    model.configure_MESH_parameter(self.step, np.empty(0))


                # Modify and write forcing with perturbation
                model.model_forcing_wrt(member_forcing, self.step)

                model.model_run()
                # read model outputs, dump is a df containing the initial conditions for next step
                state_tmp, dump_tmp = model.model_read_output()

            else:
                raise Exception("Numerical model not implemented")

            # store model outputs and perturbation parameters
            self.state_membres[mbr] = state_tmp.copy()

            self.out_members[mbr] = dump_tmp.copy()

            self.noise[mbr] = noise_tmp.copy()

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

            # create temporal model dir
            self.temp_dest = model.model_copy(self.lat_idx, self.lon_idx)

            # Ensemble generator
            for mbr in range(self.members):

                noise_tmp = updated_pars[:, mbr]
                member_forcing, noise_k_tmp = \
                    met.perturb_parameters(self.forcing, noise=noise_tmp,
                                           update=True)

                model.model_forcing_wrt(member_forcing, self.temp_dest,
                                        self.step)

                if cfg.numerical_model in ['FSM2']:
                    if step != 0:
                        model.write_dump(self.out_members_iter[mbr],
                                         self.temp_dest)

                    model.model_run(self.temp_dest)

                    state_tmp, dump_tmp = model.model_read_output(
                        self.temp_dest)

                elif cfg.numerical_model in ['dIm', 'snow17']:

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
        new_out = [self.out_members[x].copy() for x in resampled_particles]
        self.out_members = new_out.copy()

        # Noise
        new_out = [self.noise[x].copy() for x in resampled_particles]
        self.noise = new_out.copy()

        if cfg.da_algorithm in ['PIES', 'AdaPBS'] and do_res:
            new_out = [self.noise_iter[x].copy()
                       for x in resampled_particles]
            self.noise_iter = new_out.copy()

            new_out = [self.out_members_iter[x].copy()
                       for x in resampled_particles]
            self.out_members_iter = new_out.copy()

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
