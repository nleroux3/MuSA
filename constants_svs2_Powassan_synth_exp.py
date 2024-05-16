# -----------------------------------
# Physical constants
# -----------------------------------

sdfrac = 0.7                    # fraction of the sd_errors to use if collapse


# -----------------------------------
# Mean errors
# -----------------------------------

mean_errors = {"PRE": 0,
            "TA": 0}
sd_errors = { "PRE": 0.4,
            "TA":0.9}

# -----------------------------------
# Upper bounds errors
# -----------------------------------

# If strategy is normal or lognormal, bounds apply to the perturbed variables
# If strategy is  "logitnormal_mult","logitnormal_adi", bounds applied to the noie

upper_bounds = {"PRE": 3,
                "TA": 3}

# -----------------------------------
# Lower bounds errors
# -----------------------------------

lower_bounds = {"PRE": 0,
                "TA": -3}


# -----------------------------------
# Dynamic noise
# -----------------------------------
dyn_noise = {"PRE": 0.01,
             "TA": 0.01}


# -----------------------------------
# Unit conversions
# -----------------------------------
forcing_offset = {"PRE": 0,
                  "TA": 0}

forcing_multiplier = {"PRE": 1,
                      "TA": 1}
