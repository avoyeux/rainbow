pro const_init

defsysv, "!const_G", 6.67408d-11															;[m3.kg^-1.s^-2]
defsysv, "!const_kB", 1.3806503d-23                                                           ;[J.K^-1]
defsysv, "!const_h", 6.62606876d-34                                                           ;[J.s]
defsysv, "!const_amu", 1.66053873d-27                                                         ;[kg]
defsysv, "!const_c", 299792458.0d                                                             ;[m.s^-1]
defsysv, "!const_m_h", 1.0078250321*!const_amu                                                ;[kg]
defsysv, "!const_m_he", 4.0026032497*!const_amu                                               ;[kg]
defsysv, "!const_ua", 1.49597870691d11                                                        ;[m]
defsysv, "!const_lambda_h", 1215.67d-10                                                       ;[m]
defsysv, "!const_lambda_he", 303.78d-10                                                       ;[m]
defsysv, "!const_B1s2p_h", (6.0/3.0)*(6.26d8*(!const_lambda_h)^3.0d)/(8.0d*!dpi*!const_h)     ;[J^-1.m^3.s^-2]
defsysv, "!const_B1s2p_he", (6.0/3.0)*(1.00d10*(!const_lambda_he)^3.0d)/(8.0d*!dpi*!const_h)  ;[J^-1.m^3.s^-2]
defsysv, "!const_nu0_h", (!const_c)/(!const_lambda_h)                                         ;[s^-1]
defsysv, "!const_nu0_he", (!const_c)/(!const_lambda_he)                                       ;[s^-1]
defsysv, "!const_sigma1_h", [1.2123537, 0.39397851, 0.5069496]*1.0d-10/sqrt(exp(1))           ;[m]
defsysv, "!const_sigma1_he", 10*1.0d-12/sqrt(exp(1))                                          ;[m]
defsysv, "!const_amp_h", [0.89386553, -10.53734, 12.94331]*(!const_sigma1_h*sqrt(!dpi))
defsysv, "!const_amp_he", 1.0d
defsysv, "!const_dlb_h", [0.021592636, 0.020865398, 0.018594019]*1.0d-10                      ;[m]
defsysv, "!const_dlb_he", 0.0d                                                                ;[m]
defsysv, "!const_Grav", 6.67259d-11                                                           ;[m3.kg-1.s-2]
defsysv, "!const_MSol", 1.989d30                                                              ;[kg]
defsysv, "!const_mp", 1.67262158d-27                                                          ;[kg]
defsysv, "!const_me", 9.10938291d-31                                                          ;[kg]
defsysv, "!const_q", 1.60217657d-19                                                           ;[C]
defsysv, "!const_Ro", 6.9599d8                                                               ;[m]
defsysv, "!const_epsilon0", 8.854187817d-12                                                   ;[F/m]
defsysv, "!const_astronomical_unit", 149597870700.0d                                           ;[m]
defsysv, "!const_thomson_section", ((!const_q^2.0d)/(4.0*!dpi*!const_epsilon0*!const_me*!const_c^2.0d))^2.0d ;m^2

defsysv, "!const_mercury_radius", 2439.7d3 ;m
defsysv, "!const_venus_radius", 6051.8d3 ;m


DEFSYSV, "!DDTOR", !DPI/180.0d
DEFSYSV, "!DRADEG", 180.0d/!DPI

file = 'sun_coronal_1992_feldman.abund'
;abund_name = concat_dir(concat_dir(!xuvtop, 'abundance'), file)
;read_abund, abund_name, abund, abund_ref
defsysv, "!const_Ahe", 0.1

end

