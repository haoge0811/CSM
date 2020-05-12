# this config file is used by OOP circuit simulator
# set simulation conditions in this file, then call OOP circuit simulator from terminal
# command: python OOP_circuit_simulator.py config.py

# TODO: why do we need this? 
from func_csm import Signal

SP_DATA_DIR = './output_spice/'
CSM_DATA_DIR = './output_csm/'
VERILOG_DIR = "../data/ISCAS_85_verilog/"
CKT = "c17"
# if LUT not exist, create it using characterzation process
LUT_bin_dir = "/home/home2/visiting/mitsushij/data/CSM_data/LUT_bin/"
# LUT selection. the following parameter determins which CSM model (LUT) will be loaded for simulation.
TECH = "MOSFET_16nm_LP"
VDD = 0.9
# in fact, there is no way to control the simulation vdd here. user should just pick different CSM model from LUT bin
VL = -0.18
VH = 1.08
VSTEP = 0.05
PROCESS_VARIATION = 1.0 # process variation multiplier
TEMPERATURE = 25.0
# simulation parameters
T_TOT = 1e-9
T_STEP = 1e-12

# primary inputs
PI_signal_dict = {
    "N1":Signal(mode="pulse", param={"V1": 0, "V2": 0.7, "TD": 1e-12, "TR": 20e-12, "TF": 20e-12, "PW": 1.6e-9, "PER": 3.2e-9}),
    "N2":Signal(mode="pulse", param={"V1": 0, "V2": 0.7, "TD": 1e-12, "TR": 20e-12, "TF": 20e-12, "PW": 800e-12, "PER": 1.6e-9}),
    "N3":Signal(mode="pulse", param={"V1": 0, "V2": 0.7, "TD": 1e-12, "TR": 20e-12, "TF": 20e-12, "PW": 400e-12, "PER": 800e-12}),
    "N6":Signal(mode="pulse", param={"V1": 0, "V2": 0.7, "TD": 1e-12, "TR": 20e-12, "TF": 20e-12, "PW": 200e-12, "PER": 400e-12}),
    "N7":Signal(mode="pulse", param={"V1": 0, "V2": 0.7, "TD": 1e-12, "TR": 20e-12, "TF": 20e-12, "PW": 100e-12, "PER": 200e-12})}


# capacitive loading of primary output
# two way of declaring
# 1. load all
load_all_PO = True
cap_value = 1e-16
# 2. manually choose to load how much on each node
#load_all_PO = False
#final_output_load = {"N22": 1e-16, "N23": 1e-16}

# saving options
save_file_path = "./output_csm/" + CKT + '_' + TECH + "_VL" + str(VL) + "_VH" + str(VH) + "_VSTEP" + \
                    str(VSTEP) + "_P" + str(PROCESS_VARIATION) + "_V" + str(VDD) + "_T" + str(TEMPERATURE) + \
                    "_TSTEP" + str(T_STEP) + "_voltage_save.csv"
voltage_nodes_to_save = ["N22", "N23"]

SPICE_OUT_DIR="./output_spice/"
initial_voltage_settle_th = 0.00001/0.01e-12 