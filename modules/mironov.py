import numpy as np



def mironov_model(T, C, m_v, p_d = 1.5):
    """
    Calculate the complex permittivity (at 1.4 Ghz) of frozen and thaw soil
    input param
        T : temperature in Celsius
        C : Clay content in %
        m_v : volumetric moisture content (cm^3/cm^3)
        p_d : bulk density (g/cm^3)

        thaw soil from mironov et al 2013 (DOI: 10.1109/LGRS.2012.2207878)
        frozen soil from mironov et al 2017 (DOI: 10.1016/j.rse.2017.08.007)
    """
    #check T is within -30 and 30
    if T < -30:
        T = -30
    if T > 30:
        T = 30

    #positive temperature
    if T >= 0 :
        m_v_t = 0.0286 +  0.00307 * C

        n_d = 1.634 - 0.00539 * C + 2.75e-5 * C**2
        k_d = 0.0395 - 4.038e-4 * C
        n_b = (8.86 + 0.00321 * T) + (-0.0644 + 7.96e-4 * T) * C + (2.97e-4 - 9.6e-6 * T) * C**2
        k_b = (0.738 - 0.00903 * T + 8.57e-5 * T**2) + (-0.00215 + 1.47e-4 * T) * C + (7.36e-5 - 1.03e-6 * T + 1.05e-8 * T**2) * C**2
        n_u = (10.3 - 0.0173 * T) + (6.5e-4 + 8.82e-5 * T)* C + (-6.34e-6 - 6.32e-7 * T) * C**2
        k_u = (0.7 - 0.017 * T + 1.78e-4 * T**2) + (0.0161 + 7.25e-4 * T) * C + (-1.46e-4 - 6.03e-6 * T - 7.87e-9 * T**2)* C**2


        if m_v_t >= m_v:
            #for m_v_t < m_v
            n_s = n_d + (n_b - 1) * m_v
            k_s = k_d + k_b * m_v
        else :
            #for m_v_t > m_v
            n_s = n_d + (n_b - 1) * m_v_t + (n_u - 1) * (m_v - m_v_t)
            k_s = k_d + k_b * m_v_t + k_u * (m_v - m_v_t)

    #negative temperature
    else:
        #Moisture (cm^3/cm^3)
        m_g = m_v/p_d

        m_gl = 0.0019 * C * (1 + 1.056 * np.exp(T/6.77))
        n_m_1p = 0.415 - 0.0256 * np.exp(T/3.57)
        n_b_1p = 8.042 + 0.0921 * T
        n_i_1p = 1.305 + 1.022 * np.exp(T/4.02)
        k_m_p = 0
        k_b_p = 1.654 - 0.258 * np.exp(T/4.07)
        k_i_p = 0.204 + 0.00354 * T

        # exemple for m of the notation of eqn from Mironov et al 2017
        #n_m_1p = (n_m - 1)/p_m
        #k_m_p = k_m/p_m

        if m_gl >= m_g:

            n_s = (n_m_1p + n_b_1p * m_g) * p_d + 1
            k_s = (k_m_p + k_b_p * m_g) * p_d
        else :

            n_s = (n_m_1p + n_b_1p * m_gl + n_i_1p * (m_g - m_gl)) * p_d + 1
            k_s = (k_m_p + k_b_p * m_gl + k_i_p * (m_g - m_gl)) * p_d    

    #real and imaginary permittivity (output)
    e_r = n_s**2 - k_s**2
    e_i = 2 * n_s * k_s

    return e_r, e_i