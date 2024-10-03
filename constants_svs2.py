# -----------------------------------
# Physical constants
# -----------------------------------

sdfrac = 0.7                    # fraction of the sd_errors to use if collapse


# -----------------------------------
# Mean errors
# -----------------------------------


mean_errors = {"PRE": -0.22324549502942945,
            "TA": 0.0, 
            "UV":-0.04804,
            "FSIN":-0.0050}

sd_errors = { "PRE": 0.6681998129742771,
            "TA":1.46297, 
            "UV":0.309967,
            "FSIN": 0.1}

# -----------------------------------
# Decorrelation time [h]
# -----------------------------------

tau = {"PRE": 24.,
       "TA": 10.25,
       "UV": 2.6,
       "FSIN": 3.}
# -----------------------------------
# Upper bounds errors
# -----------------------------------

# If strategy is normal or lognormal, bounds apply to the perturbed variables
# If strategy is  "logitnormal_mult","logitnormal_adi", bounds applied to the noise

upper_bounds = {"PRE": 3,
                "TA": 3,
                "UV": 3,
                "FSIN": 3}


# -----------------------------------
# Lower bounds errors
# -----------------------------------

lower_bounds = {"PRE": 0.5,
                "TA": -3,
                "UV": 0.5,
                "FSIN":0.5}

# -----------------------------------
# Dynamic noise
# -----------------------------------

dyn_noise = {"PRE": 0.01,
                "TA": 0.01,
                "UV": 0.01,
                "FSIN":0.01}


# -----------------------------------
# Unit conversions
# -----------------------------------
forcing_offset = {"PRE": 0,
                  "TA": 0,
                  "UV":0,
                  "FSIN":0}

forcing_multiplier = {"PRE": 1,
                      "TA": 1,
                      "UV":1,
                      "FSIN":1}
