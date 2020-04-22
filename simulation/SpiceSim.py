
import re
import os
import importlib
from translator_from_verilog_to_spice_netlist import *
from functions import *
from ../data/

# TODO: Saeed needs to fix this
# Let it be the way it is now. 
def get_mode_dict():
    LIB_DIR_MAP = dict()
    LIB_DIR_MAP["FINFET_7nm_HP"] = "../data/modelfiles/PTM_MG/hp/7nm_HP.pm"
    LIB_DIR_MAP["FINFET_7nm_LSTP"]="../data/modelfiles/PTM_MG/lstp/7nm_LSTP.pm"
    LIB_DIR_MAP["MOSFET_16nm_HP"] = "../data/modelfiles/PTM_MOSFET/16nm_HP.pm"
    LIB_DIR_MAP["MOSFET_16nm_LP"] = "../data/modelfiles/PTM_MOSFET/16nm_LP.pm"
    return LIB_DIR_MAP



class SpiceSim:
    def __init__(self, config_file):
    self.config = importlib.import_module(config_file_name)
    self.out_dir = './output/' + verilog_name
    self.LIB_DIR = get_model_dict()[self.config.TECH]

    def gen_sp_gates(self):
           
        # extract library related parameters from library header section
        library_file = open(LIB_DIR, "r")
        # set some default value to None, 
        # since depending on MOSFET or FINFET, some value will not be provided
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
        
        owd = os.getcwd()  # record original working directory
        template_dir = "./gate_gen/" + self.config.DEVICE_NAME + "_GATES.sp"

        generate_from_template(template_directory = template_dir, \
                output_directory = self.out_dir + "gate_inventory_gen.sp", \
                replace = {"$$library": owd +"/"+ self.LIB_DIR, "$$lg_p": LIB_LEN, "$$lg_n": LIB_LEN, "$$w_n": LIB_WIDTH_N, "$$w_p": LIB_WIDTH_P, "$$nfin":NFIN})
         
    def gen_spice_from_verilog(self):
    ''' generate spice netlist from verilog netlist 
    modify it into spice_simulation_file
    '''

        v_path = self.config.VERILOG_DIR + "/" + self.config.CKT + ".v"
        sp_path = self.out_dir + "/" + self.config.CKT + ".sp"
        # TODO: check this with Eda
        os.system("cp " + v_path + " " +  self.out_dir + "/")
        v_path = self.out_dir + self.CKT + ".v"
        output_list = verilog2spice(v_path, sp_path)

        sp_infile = open(sp_path, 'r')
        temp_netlist = sp_infile.readlines()
        sp_infile.close()   
        # TODO: later change this, reading writing again is kinda not good, 
        # .. but I'm not sure
        sp_infile = open(sp_path, 'w')
    
        self.gen_gates()

        #add simulation conditions to spice file

        sp_infile.writelines(["* Eda Yan\n", "* USC - SPORT LAB\n"])
        sp_infile.write(".option NOMOD")
        sp_infile.write(".global vdd")
        sp_infile.write(".param vdd=" + self.config.VDD)
        sp_infile.write(".include \'./gate_inventory_gen.sp\'") # TODO: hard coded
        sp_infile.write("\n\n\n")

        for line in temp_netlist:
            sp_infile.writelines([line])
        
        #only add load to final outputs
        sp_infile.writelines(["* extra load at final output\n"])
        if config.load_all_PO == False:
            spice_extra_output_load = config.final_output_load
            i = 1
            for key in spice_extra_output_load:
                sp_infile.writelines(["cL", str(i), " ", key, " 0 ", str(spice_extra_output_load[key]), "\n"])
                i = i + 1
        else:
            spice_output_load = config.cap_value
            i = 1
            output_list = output_list[0].split()[1]
            output_list = output_list.strip(';\n')
            output_list = output_list.split(',')
            for output in output_list:
                sp_infile.writelines(["cL", str(i), " ", output, " 0 ", str(spice_output_load), "\n"])
                i = i + 1
        sp_infile.writelines(["\n"])
        
        #generate input signals
        #use Piecewise Linear Source for ramp_lh or ramp_hl signals, and use DC Source for constant signals
        input_signals = config.PI_signal_dict
        sp_infile.writelines(["* input signals\n"])
        for key in input_signals:
            net_name = key
            signal = input_signals[key]
            if signal.mode == "constant":
                sp_infile.writelines(["V", net_name, " ", net_name, " 0 ", str(signal.constant), "\n"])
            elif signal.mode == "ramp_lh":
                sp_infile.writelines(["V", net_name, " ", net_name, " 0 ", "pwl "])
                sp_infile.writelines(["0ps", " 0 ", float2string(signal.param["t_0"]), " 0 "])
                sp_infile.writelines([float2string(signal.param["t_lh"]), " ", str(signal.param["vdd"]), " "])
                sp_infile.writelines([float2string(config.T_TOT), " ", str(signal.param["vdd"]), "\n"])
            elif signal.mode == "ramp_hl":
                sp_infile.writelines(["V", net_name, " ", net_name, " 0 ", "pwl "])
                sp_infile.writelines(["0ps ", str(signal.param["vdd"]), " ", float2string(signal.param["t_0"]), " ", str(signal.param["vdd"]), " "])
                sp_infile.writelines([float2string(signal.param["t_lh"]), " 0 "])
                sp_infile.writelines([float2string(config.T_TOT), " 0\n"])
            else:
                print(net_name, ":undefined input signal mode")
        sp_infile.writelines(["\n\n"])
        
        #spice_initial_conditions = NONE
        #let spice pre-simulation without initial conditions
        
        spice_timing_step = ".tran " + float2string(config.T_STEP) + " " + float2string(config.T_TOT)
        sp_infile.writelines([spice_timing_step, "\n", ".op", "\n"])
        
        #print all inputs and outputs signals
        
        spice_print_list = []
        #for key in input_signals:
        #    spice_print_list.append(key)
        for output in output_list:
            spice_print_list.append(output)
        sp_infile.writelines([".print "])
        for item in spice_print_list:
            sp_infile.writelines(["v(", item, ") "])
        sp_infile.writelines(["\n"])
        sp_infile.writelines([".end"])
        sp_infile.close()

    def simulate_hspice(self):
        pass


