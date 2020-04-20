# author: Eda Yan <yidayan@usc.edu>
# generate spice file to be simulated by Hspice using conditions of config.py

import re
import os
import importlib
from translator_from_verilog_to_spice_netlist import *
from functions import *


def main(config_file_name):
    config = importlib.import_module(config_file_name)
    verilog_netlist_dir = config.verilog_netlist_dir
    verilog_name = verilog_netlist_dir.split('/')[3]
    cp_dir = './output/' + verilog_name
    #save_file_dir = config_file.save_file_dir
    #voltage_nodes_to_save = config_file.voltage_nodes_to_save
    
    #generate spice netlist from verilog netlist and modify it into spice_simulation_file
    spice_file_dir = cp_dir.replace('.v', '.sp')
    os.system("cp ../data/ISCAS_85_verilog/c17.v ./output/c17.v")
    output_list = translator_from_verilog_to_spice_netlist(cp_dir, spice_file_dir)
    spice_netlists = open(spice_file_dir, 'r')
    temp_netlist = spice_netlists.readlines()
    spice_netlists.close()
    spice_netlists = open(spice_file_dir, 'w')

    # added by haoge start ------------------------------------------------------------------------------
    LIB_DIR_MAP = dict()
    LIB_DIR_MAP["FINFET_7nm_HP"] = "../data/modelfiles/PTM_MG/hp/7nm_HP.pm"
    LIB_DIR_MAP["FINFET_7nm_LSTP"] = "../data/modelfiles/PTM_MG/lstp/7nm_LSTP.pm"
    LIB_DIR_MAP["MOSFET_16nm_HP"] = "../data/modelfiles/PTM_MOSFET/16nm_HP.pm"
    LIB_DIR_MAP["MOSFET_16nm_LP"] = "../data/modelfiles/PTM_MOSFET/16nm_LP.pm"

    LIB_DIR = LIB_DIR_MAP[config.TECH]
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
    # generate gate inventory
    owd = os.getcwd()  # record original working directory
    generate_from_template(template_directory = "./gate_gen/" + DEVICE_NAME + "_GATES.sp",
                           output_directory   = "./output/gate_inventory_gen.sp",
                           replace = {"$$library": owd +"/"+ LIB_DIR,
                                      "$$lg_p": LIB_LEN, "$$lg_n": LIB_LEN,
                                      "$$w_n": LIB_WIDTH_N, "$$w_p": LIB_WIDTH_P,
                                      "$$nfin":NFIN})
    # added by haoge end ------------------------------------------------------------------------------


    #add simulation conditions to spice file
    spice_option = ".option NOMOD"
    spice_global = ".global vdd"
    spice_temp = ".temp " + str(config.TEMPERATURE)
    spice_param = ".param vdd=0.7"
    spice_include_gate_inventory = ".include " + "'" + "./gate_inventory_gen.sp" + "'"
    spice_netlists.writelines(["* Eda Yan\n", "* USC - SPORT LAB\n"])
    spice_netlists.writelines([spice_option, "\n", spice_global, "\n", spice_temp, "\n", spice_param, "\n\n"])
    # spice_netlists.writelines([spice_include, "\n"])
    spice_netlists.writelines([spice_include_gate_inventory, "\n\n\n"])
    for line in temp_netlist:
        spice_netlists.writelines([line])
    
    #only add load to final outputs
    spice_netlists.writelines(["* extra load at final output\n"])
    if config.load_all_PO == False:
        spice_extra_output_load = config.final_output_load
        i = 1
        for key in spice_extra_output_load:
            spice_netlists.writelines(["cL", str(i), " ", key, " 0 ", str(spice_extra_output_load[key]), "\n"])
            i = i + 1
    else:
        spice_output_load = config.cap_value
        i = 1
        output_list = output_list[0].split()[1]
        output_list = output_list.strip(';\n')
        output_list = output_list.split(',')
        for output in output_list:
            spice_netlists.writelines(["cL", str(i), " ", output, " 0 ", str(spice_output_load), "\n"])
            i = i + 1
    spice_netlists.writelines(["\n"])
    
    #generate input signals
    #use Piecewise Linear Source for ramp_lh or ramp_hl signals, and use DC Source for constant signals
    input_signals = config.PI_signal_dict
    spice_netlists.writelines(["* input signals\n"])
    for key in input_signals:
        net_name = key
        signal = input_signals[key]
        if signal.mode == "constant":
            spice_netlists.writelines(["V", net_name, " ", net_name, " 0 ", str(signal.constant), "\n"])
        elif signal.mode == "ramp_lh":
            spice_netlists.writelines(["V", net_name, " ", net_name, " 0 ", "pwl "])
            spice_netlists.writelines(["0ps", " 0 ", float2string(signal.param["t_0"]), " 0 "])
            spice_netlists.writelines([float2string(signal.param["t_lh"]), " ", str(signal.param["vdd"]), " "])
            spice_netlists.writelines([float2string(config.T_TOT), " ", str(signal.param["vdd"]), "\n"])
        elif signal.mode == "ramp_hl":
            spice_netlists.writelines(["V", net_name, " ", net_name, " 0 ", "pwl "])
            spice_netlists.writelines(["0ps ", str(signal.param["vdd"]), " ", float2string(signal.param["t_0"]), " ", str(signal.param["vdd"]), " "])
            spice_netlists.writelines([float2string(signal.param["t_lh"]), " 0 "])
            spice_netlists.writelines([float2string(config.T_TOT), " 0\n"])
        else:
            print(net_name, ":undefined input signal mode")
    spice_netlists.writelines(["\n\n"])
    
    #spice_initial_conditions = NONE
    #let spice pre-simulation without initial conditions
    
    spice_timing_step = ".tran " + float2string(config.T_STEP) + " " + float2string(config.T_TOT)
    spice_netlists.writelines([spice_timing_step, "\n", ".op", "\n"])
    
    #print all inputs and outputs signals
    
    spice_print_list = []
    for key in input_signals:
        spice_print_list.append(key)
    for output in output_list:
        spice_print_list.append(output)
    spice_netlists.writelines([".print "])
    for item in spice_print_list:
        spice_netlists.writelines(["v(", item, ") "])
    spice_netlists.writelines(["\n"])
    spice_netlists.writelines([".end"])
    spice_netlists.close()
    
    #call hspice and save output to .out file
    print('hsipce simulating...')
    os.chdir("./output")
    os.system('hspice c17.sp > c17.out')

main("config")