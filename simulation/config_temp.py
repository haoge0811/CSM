# this config file is used by OOP circuit simulator
# set simulation conditions in this file, then call OOP circuit simulator from terminal
# command: python OOP_circuit_simulator.py config.py

# TODO: why do we need this? 
from func_csm import Signal

SP_DATA_DIR = './output_spice/'
CSM_DATA_DIR = './output_csm/'
VERILOG_DIR = "../data/ISCAS_85_verilog/"
CKT = "inv"
# if LUT not exist, create it using characterzation process
LUT_bin_dir = "/home/home2/visiting/mitsushij/data/CSM_data/LUT_bin/"
# LUT selection. the following parameter determins which CSM model (LUT) will be loaded for simulation.
TECH = "MOSFET_16nm_HP"
VDD = 0.7 # this is the vdd used during the creation of CSM model. it has nothing to do with the simulation vdd.
# in fact, there is no way to control the simulation vdd here. user should just pick different CSM model from LUT bin
VL = -0.14
VH = 0.84
VSTEP = 0.05
PROCESS_VARIATION = 1.0 # process variation multiplier
TEMPERATURE_list = [-25.0, 0.0, 25.0, 50.0, 75.0, 100.0]
# simulation parameters
T_TOT = 100e-12
T_STEP = 0.1e-12

# primary inputs
PI_signal_dict = {
    "N1":Signal(mode="ramp_lh", param={"vdd": 0.7, "t_0": 10e-12, "t_lh": 50e-12})}


# capacitive loading of primary output
# two way of declaring
# 1. load all
load_all_PO = True
cap_value = 1e-16
# 2. manually choose to load how much on each node
#load_all_PO = False
#final_output_load = {"N22": 1e-16, "N23": 1e-16}

# saving options
save_file_path = dict()
for temp in TEMPERATURE_list:
    save_file_path[str(temp)] = "./output_csm/" + CKT + '_' + TECH + "_VL" + str(VL) + "_VH" + str(VH) + "_VSTEP" + \
                        str(VSTEP) + "_P" + str(PROCESS_VARIATION) + "_V" + str(VDD) + "_T" + str(temp) + \
                        "_TSTEP" + str(T_STEP) + "_voltage_save.csv"

voltage_nodes_to_save = ["N2"]

SPICE_OUT_DIR="./output_spice/"
initial_voltage_settle_th = 0.00001/0.01e-12 