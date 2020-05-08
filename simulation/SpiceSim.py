
import re
import os
import importlib
from verilog2spice import *
from func_spice import *

# TODO: Saeed needs to fix this
# Let it be the way it is now. 
def get_model_dict():
    LIB_DIR_MAP = dict()
    LIB_DIR_MAP["FINFET_7nm_HP"] = "../data/modelfiles/PTM_MG/hp/7nm_HP.pm"
    LIB_DIR_MAP["FINFET_7nm_LSTP"]="../data/modelfiles/PTM_MG/lstp/7nm_LSTP.pm"
    LIB_DIR_MAP["MOSFET_16nm_HP"] = "../data/modelfiles/PTM_MOSFET/16nm_HP.pm"
    LIB_DIR_MAP["MOSFET_16nm_LP"] = "../data/modelfiles/PTM_MOSFET/16nm_LP.pm"
    return LIB_DIR_MAP



class SpiceSim:
    def __init__(self, config_file):
        self.config = importlib.import_module(config_file)
        self.out_dir = self.config.SP_DATA_DIR
        self.LIB_DIR = get_model_dict()[self.config.TECH]

    def gen_sp_gates(self):
           
        # extract library related parameters from library header section
        library_file = open(self.LIB_DIR, "r")
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
        template_dir = "./gate_gen/" + self.config.TECH[0:6] + "_GATES.sp"

        generate_from_template(template_directory = template_dir, \
                output_directory = self.out_dir + "gate_inventory_gen.sp", \
                replace = {"$$library": owd +"/"+ self.LIB_DIR, "$$lg_p": LIB_LEN, "$$lg_n": LIB_LEN, "$$w_n": LIB_WIDTH_N, "$$w_p": LIB_WIDTH_P, "$$nfin":NFIN})
        
        
    def add_load_to_output(self, out_list):
        #only add load to final outputs based on config file
        load_str = []
        load_str.append("* extra load at final output\n")
        if self.config.load_all_PO == False:
            sp_extra_output_load = self.config.final_output_load
            i = 1
            for key in sp_extra_output_load:
                load_str.append("cL" + str(i) + " " + key + " 0 " + str(sp_extra_output_load[key]) + "\n")
                i = i + 1
        else:
            spice_output_load = self.config.cap_value
            i = 1
            out_list = out_list[0].split()[1]
            out_list = out_list.strip(';\n')
            out_list = out_list.split(',')
            for output in out_list:
                load_str.append("cL" + str(i) + " " + output + " 0 " + str(spice_output_load) + "\n")
                i = i + 1
        load_str.append("\n")
        return load_str
        
    def gen_input_signals(self):
        '''
        generate input signals
        use Piecewise Linear Source for ramp_lh or ramp_hl signals
        use pulse for pulse signals
        use DC Source for constant signals
        '''
        input_signals = self.config.PI_signal_dict
        input_str = []
        input_str.append("* input signals\n")
        for key in input_signals:
            net_name = key
            signal = input_signals[key]
            if signal.mode == "pulse":
                input_str.append("V" + net_name + " " + net_name + " 0 " + "pulse(" +\
                                 str(signal.param["V1"]) + " " + str(signal.param["V2"]) + " " +\
                                 float2string(signal.param["TD"]) + " " + float2string(signal.param["TR"]) + " " +\
                                 float2string(signal.param["TF"]) + " " + float2string(signal.param["PW"]) + " " +\
                                 float2string(signal.param["PER"]) + ")\n")
            elif signal.mode == "constant":
                input_str.append("V" + net_name + " " + net_name + " 0 " + str(signal.constant) + "\n")
            elif signal.mode == "ramp_lh":
                input_str.append("V" + net_name + " " + net_name + " 0 " + "pwl "\
                                 + "0ps" + " 0 " + float2string(signal.param["t_0"]) + " 0 "\
                                 + float2string(signal.param["t_lh"]) + " " + str(signal.param["vdd"]) + " "\
                                 + float2string(self.config.T_TOT) + " " + str(signal.param["vdd"]) + "\n")
            elif signal.mode == "ramp_hl":
                input_str.append("V" + net_name + " " + net_name + " 0 " + "pwl ")
                input_str.append("0ps " + str(signal.param["vdd"]) + " " + float2string(signal.param["t_0"]) + " " + str(signal.param["vdd"]) + " ")
                input_str.append(float2string(signal.param["t_lh"]) + " 0 ")
                input_str.append(float2string(self.config.T_TOT) + " 0\n")
            else:
                print(net_name, ":undefined input signal mode")
        input_str.append("\n\n")
        return input_str
        
        
    def gen_spice_from_verilog(self):
        ''' generate spice netlist from verilog netlist 
        modify it into spice_simulation_file
        '''
        v_path = self.config.VERILOG_DIR + self.config.CKT + ".v"
        sp_path = self.out_dir + self.config.CKT + ".sp"
        # TODO: check this with Eda
        os.system("cp " + v_path + " " +  self.out_dir)
        v_path = self.out_dir + self.config.CKT + ".v"
        output_list = verilog2spice(v_path, sp_path)

        sp_infile = open(sp_path, 'r')
        temp_netlist = sp_infile.readlines()
        sp_infile.close()   
        # TODO: later change this, reading writing again is kinda not good, 
        # .. but I'm not sure
        sp_infile = open(sp_path, 'w')
    
        self.gen_sp_gates()

        #add simulation conditions to spice file

        sp_infile.writelines(["* Eda Yan\n", "* USC - SPORT LAB\n"])
        sp_infile.write(".option NOMOD\n")
        sp_infile.write(".global vdd\n")
        sp_infile.write(".param vdd=" + str(self.config.VDD) + "\n")
        sp_infile.write(".include \'./gate_inventory_gen.sp\'") # TODO: hard coded
        sp_infile.write("\n\n\n")
        
        #add spice netlist to spice file
        for line in temp_netlist:
            sp_infile.writelines([line])
        
        #spice_initial_conditions = NONE
        #let spice pre-simulation without initial conditions
        
        #add load to circuit outputs
        load_str = self.add_load_to_output(output_list)
        for string in load_str:
            sp_infile.write(str(string))
            
        #add input signals to spice file
        input_str = self.gen_input_signals()
        for string in input_str:
            sp_infile.write(str(string))
        
        #add timing step to spice file
        sp_ts = ".tran " + float2string(self.config.T_STEP) + " " + float2string(self.config.T_TOT)
        sp_infile.writelines([sp_ts, "\n", ".op", "\n"])
        
        #add information for printing signals
        sp_print_list = []
        #for key in input_signals:
        #    sp_print_list.append(key)
        output_list = output_list[0].split()[1]
        output_list = output_list.strip(';\n')
        output_list = output_list.split(',')
        for output in output_list:
            sp_print_list.append(output)
        sp_infile.writelines([".print "])
        for item in sp_print_list:
            sp_infile.writelines(["v(", item, ") "])
        sp_infile.writelines(["\n"])
        sp_infile.writelines([".end"])
        sp_infile.close()

    def simulate_hspice(self):
        print('hsipce simulating...')
        self.gen_spice_from_verilog()
        owd = os.getcwd()
        os.chdir(self.out_dir)
        os.system("hspice " + self.config.CKT + ".sp > " + self.config.CKT + ".out")
        os.chdir(owd)

#ss = SpiceSim("config")
#ss.simulate_hspice()