# Author: haoge <haoge@usc.edu> at USC SPORT Lab

# when characterising, voltage is swept beyond vdd and gnd, to accommodate for overshoot during simulation
# value is difference of VH-vdd or gnd-VL. e.g. for overscan = 0.5, vdd = 1V, actual scan is from -0.5V to 1.5V
VOLTAGE_OVERSCAN = 0.14

# spice extended resolution factor.
# to solve the problem that spice tran simulation resolution decreases with VSTEP.
#we want VSTEP to decrease stored CSM LUT size, but not the accuracy of spice simulation.
# hence this parameter multiplies spice tran simulation resolution by this factor.
# be careful when read spice output, ditch un-needed lines so that LUT size does not change
SP_EXTEND_RES = 20
#################################   Spice template directory   #################################################
# user need to tell the tool know where are the templates
spice_template_dir = "./spice_templates/"

#################################   Output save option and directory  ##########################################
LUT_bin_dir = "/home/home2/visiting/mitsushij/data/CSM_data/LUT_bin/"
# these files below can be used for debug. otherwise saving them cost in storage.
# if set to yes(1), then os will copy spice temp out to its specific dir + name each specific analysis.
save_spice_raw_char_output   = 0
spice_raw_char_out_dir       = "../LUT_bin/spice_raw_char_out/"
save_spice_processed_char_output = 0
spice_processed_char_out_dir = "../LUT_bin/spice_processed_char_out/"
save_human_readable_LUT = 0
human_readable_LUT_dir = "../LUT_bin/human_readable_LUT/"

#################################   Spice transient analysis parameter   #######################################
pulse_rise_time = 0.5e-12


#################################   Temperary files directory  #################################################
temp_folder = "./temp_files/"
