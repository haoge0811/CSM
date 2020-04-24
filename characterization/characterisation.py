# Author: haoge <haoge@usc.edu> at USC SPORT Lab
import os
import pickle

# convention: variables use import file. functions use from file import *
import config
from functions import *

# example input
# GATE_NAME = "INV"
# VSTEP = 0.1 # resolution of LUT
# LIB_DIR = "../modelfiles/PTM_MOSFET/16nm_LP_TEMPLATE.pm" # input library
# VDD = 0.9
# TEMPERATURE = 25
def main(GATE_NAME, VSTEP, LIB_DIR, VDD, TEMPERATURE, return_unique_id = 0):
    #################################### extract and setup some parameters ##########################################
    # extract library related parameters from library header section
    library_file = open(LIB_DIR, "r")
    # set some default value to None, since depending on MOSFET or FINFET, some value will not be provided
    LIB_WIDTH_N = None
    LIB_WIDTH_P = None
    NFIN = None
    for line in library_file:
        if "device_name" in line:
            DEVICE_NAME = line.split()[-1] # take the last element of the line
        elif "tech_name" in line:
            TECH_NAME = line.split()[-1]
        elif "Vth_multiplier" in line:
            Vth_multiplier = float(line.split()[-1])
        elif "nominal_length" in line:
            LIB_LEN = float(line.split()[-1])
        elif "nominal_width_n" in line:
            LIB_WIDTH_N = float(line.split()[-1])
        elif "nominal_width_p" in line:
            LIB_WIDTH_P = float(line.split()[-1])
        elif "nominal_nfin" in line:
            NFIN = float(line.split()[-1])
    library_file.close()
    # extraction end

    owd = os.getcwd() # record original working directory
    sweep_low  = -(VDD * config.VOLTAGE_OVERSCAN)  # V_L
    sweep_high = VDD * (1+config.VOLTAGE_OVERSCAN) # V_H

    print("Characterising for PVT value %.4f %.4f %.1fC" % (Vth_multiplier, VDD, TEMPERATURE))
    unique_identifier = DEVICE_NAME +"_"+ TECH_NAME +"_"+ GATE_NAME \
        +"_VL"+str(sweep_low) +"_VH"+str(sweep_high) +"_VSTEP"+str(VSTEP) \
        +"_P"+str(Vth_multiplier) +"_V"+str(VDD) +"_T"+str(TEMPERATURE)
    print(unique_identifier)

    create_dir_if_not_exist(config.temp_folder) # create temp folder
    create_dir_if_not_exist(config.LUT_bin_dir) # LUT_bin folder

    #################################### main work begins ###########################################################
    # Step1 generate library. we don't do this now. library directory is directly passed in
    # library_gen.pm, gate_inventory_gen.sp, sweep_table.inc, spice_gen.sp need to be in the same folder
    # tested to be working

    # Step2 generate gate inventory file from its templates. this process is different for MOS and FIN.
    # hence, DEVICE_NAME is used to pick templates
    generate_from_template(template_directory = config.spice_template_dir + DEVICE_NAME + "_GATES.sp",
                           output_directory   = config.temp_folder+"gate_inventory_gen.sp",
                           replace = {"$$library": owd +"/"+ LIB_DIR,
                                      "$$lg_p": LIB_LEN, "$$lg_n": LIB_LEN,
                                      "$$w_n": LIB_WIDTH_N, "$$w_p": LIB_WIDTH_P,
                                      "$$nfin":NFIN})
    # MOSFET don't use NFIN, it will be skipped, FINFET don't use LIB_WIDTH, it will be skipped
    # owd is added to lib dir because gate inventory is in temp folder, gate inventory cannot know its relative position
    # to the owd

    # Step3 sweep_table generator for spice parametric analysis, which is gate specific
    # As gate name is one of the input
    sweep_table_generator(GATE_NAME, sweep_low, sweep_high, VSTEP,
                          config.temp_folder+"sweep_table.inc")
    # need to check for NAND2

    # Step4 generate spice file
    # shared parameters for all gates.
    TO_BE_REPLACED = {"$$vdd": VDD, "$$temp": TEMPERATURE, # which will vary here according to setting
                      "$$gate_inventory": "./gate_inventory_gen.sp",
                      "$$sweep_table": "./sweep_table.inc",
                      "$$v_l": sweep_low, "$$v_h": sweep_high,
                      "$$t_rise": config.pulse_rise_time, "$$vstep":VSTEP,
                      "$$sp_extend_res": config.SP_EXTEND_RES}

    # for different gate, different components need to be analysed
    # CI can be get using CM analysis
    if GATE_NAME == "INV":
        component_to_char = ["DC", "CM", "CO"]
        template_keyword = "INV_"

    elif (GATE_NAME == "NAND2") or (GATE_NAME == "NOR2"):
        component_to_char = ["DC", "CM_A", "CM_B", "CO", "CINT"]
        template_keyword = "NAND2_NOR2_"

        TO_BE_REPLACED["$$gate_name"] = GATE_NAME # add additional term to be replaced, specificlly for NAND2_NOR2
        # gate_name is to pick gate from gate inventory, to differentiate NAND2 NOR2.
        # as they share same template. INV does not use this. hence this key is only added for NAND2_NOR2
        if (GATE_NAME == "NAND2"):
            TO_BE_REPLACED["$$print_NAND2"] = ""   # selectively disable spice .print according to which gate
            TO_BE_REPLACED["$$print_NOR2"]  = "*"  # use * to comment this out in spice
        else: # NOR2 then
            TO_BE_REPLACED["$$print_NAND2"] = "*"   # selectively disable spice .print according to which gate
            TO_BE_REPLACED["$$print_NOR2"]  = ""  # use * to comment this out in spice

    else:
        print("Cannot generate from spice template, GATE_NAME illegal.")

    print("Running hspice analysis...")

    nd_array=dict() # to contain n-dimensional array of data from all component_to_char
    for component in component_to_char:
        generate_from_template(template_directory=config.spice_template_dir + template_keyword+component+".sp",
                               output_directory=config.temp_folder+"spice_gen.sp",
                               replace=TO_BE_REPLACED)
        # tested to be working

        # Step5 call os to run spice
        try:
            os.chdir(config.temp_folder) # change to temp folder dir
            os.system("hspice spice_gen.sp > spice_raw.out 2> run_hspice_error.log")
        finally:
            os.chdir(owd) # change dir back
        # save spice_raw_out according to need
        if config.save_spice_raw_char_output == 1:
            create_dir_if_not_exist(config.spice_raw_char_out_dir)
            os.system("cp "+config.temp_folder+"spice_raw.out"+" " \
                      +config.spice_raw_char_out_dir + unique_identifier +"_"+component+".raw")

        DC_mode = 1 if "DC" in component else 0
        if config.save_spic_processed_char_output == 1: # check/create processed output folder
            create_dir_if_not_exist(config.spice_processed_char_out_dir)
        flat_data = read_spice(spice_raw_out=config.temp_folder+"spice_raw.out",
                               DC_mode=DC_mode, # depends on analysis type
                               spice_extend_res=config.SP_EXTEND_RES,
                               save_processed_out=config.save_spic_processed_char_output,
                               save_dir=config.spice_processed_char_out_dir \
                                        + unique_identifier +"_"+component+".pro")

        # fill nd_array using flat_data, each gate need different dimension
        nd_array[component] = fill_nd_array(flat_data,
                                            GATE_NAME, sweep_low, sweep_high, VSTEP)
        # voltage columns in flat_data are ditched after fill. they are used to find coordinates.

    # now we have data from all analysis
    # calculate LUT here.
    LUT = calculate_LUT(input_nd_array = nd_array,
                        GATE_NAME = GATE_NAME,
                        dv2dt = ((sweep_high - sweep_low + VSTEP)/config.pulse_rise_time))
    # dv2dt is that of the pulse used during char, which in spice is
    # .param Vlow_start='$$v_l-$$vstep'
    # PULSE (Vlow_start $$v_h t_delay $$t_rise $$t_rise 10ns 20ns)
    # hence there is the above calculation

    # Last step !! yeah! save LUT using pickle to LUT bin
    print("Dumping results to .lut file...")
    pickle.dump(LUT, open(config.LUT_bin_dir + unique_identifier + ".lut", 'w'))

    # extra saving of LUT if needed
    if config.save_human_readable_LUT == 1:
        create_dir_if_not_exist(config.human_readable_LUT_dir)
        create_human_readable_LUT(LUT, config.human_readable_LUT_dir + unique_identifier + ".hlut",
                                  GATE_NAME, sweep_low, sweep_high, VSTEP)

    if (return_unique_id == 1):
        return unique_identifier

# if running stand alone
if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('gate_name', help="the gate to char e.g. 'INV' or 'NAND2'", type=str)
    p.add_argument('VSTEP', help="the resolution of created LUT e.g. '0.1'", type=float)
    p.add_argument('LIB_DIR',
        help="directory of spice library that is going to be used for this char e.g. './modelfiles/lib.pm'", type=str)
    p.add_argument('VDD', help="Vdd to run the char at e.g. '0.9'", type=float)
    p.add_argument('TEMPERATURE', help="Temperature to run the char at e.g. '25'", type=float)
    args = p.parse_args()

    main(args.gate_name, args.VSTEP, args.LIB_DIR, args.VDD, args.TEMPERATURE)