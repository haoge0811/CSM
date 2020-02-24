# this config file is used by OOP circuit simulator
# set simulation conditions in this file, then call OOP circuit simulator from terminal
# command:
from functions import *

verilog_netlist_dir = "./c17.v"

# if LUT not exist, create it using characterzation process
NAND2_LUT_dir = "../../LUT_bin/FINFET_7nm_LSTP_NAND2_VL-0.14_VH0.84_VSTEP0.05_P1.0_V0.7_T25.0.lut"


#extra_cap_load_at_final_output
final_output_load = {"N22": 1e-16, "N23": 1e-16}


# simulation parameters
t_tot = 300e-12
t_step = 0.01e-12
# inputs
PI_signal_dict = {
    "N1":Signal(mode = "constant", constant=0.7),
    "N2":Signal(mode = "constant", constant=0.0),
    "N3":Signal(mode = "constant", constant=0.7),
    "N6":Signal(mode = "constant", constant=0.0),
    "N7":Signal(mode="ramp_lh", param={"vdd": 0.7, "t_0": 5e-12, "t_lh": 50e-12})}

# saving options
save_file_dir = "./voltage_save.csv"
voltage_nodes_to_save = ["N22", "N23"]