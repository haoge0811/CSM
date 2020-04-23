# this config file is used by OOP circuit simulator
# set simulation conditions in this file, then call OOP circuit simulator from terminal
# command: python OOP_circuit_simulator.py config.py

# TODO: why do we need this? 
from func_csm import Signal

VERILOG_DIR = "../data/ISCAS_85_verilog/"
CKT = "c17"
# if LUT not exist, create it using characterzation process
LUT_bin_dir = "/home/home2/visiting/mitsushij/data/CSM_data/LUT_bin/"
# LUT selection. the following parameter determins which CSM model (LUT) will be loaded for simulation.
TECH = "FINFET_7nm_LSTP"
VDD = 0.7 # this is the vdd used during the creation of CSM model. it has nothing to do with the simulation vdd.
# in fact, there is no way to control the simulation vdd here. user should just pick different CSM model from LUT bin
VL = -0.14
VH = 0.84
VSTEP = 0.05
PROCESS_VARIATION = 1.0 # process variation multiplier
TEMPERATURE = 25.0
# simulation parameters
T_TOT = 300e-12
T_STEP = 0.01e-12

# primary inputs
PI_signal_dict = {
    "N1":Signal(mode = "constant", constant=0.7),
    "N2":Signal(mode = "constant", constant=0.0),
    "N3":Signal(mode = "constant", constant=0.7),
    "N6":Signal(mode = "constant", constant=0.0),
    "N7":Signal(mode="ramp_lh", param={"vdd": 0.7, "t_0": 5e-12, "t_lh": 50e-12})}


# capacitive loading of primary output
# two way of declaring
# 1. load all
load_all_PO = True
cap_value = 1e-16
# 2. manually choose to load how much on each node
#load_all_PO = False
#final_output_load = {"N22": 1e-16, "N23": 1e-16}

# saving options
save_file_dir = "./output_csm/voltage_save.csv"
voltage_nodes_to_save = ["N22", "N23"]

SPICE_OUT_DIR="./output_spice/"
initial_voltage_settle_threshold = 0.00001/0.01e-12 
