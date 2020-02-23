from csm_simulator import *
import pickle


# NAND2 FINFET 7nm LSTP
# load LUT and NN
NAND2_LUT_and_boundary = load_LUT("../../LUT_bin/FINFET_7nm_LSTP_NAND2_VL-0.14_VH0.84_VSTEP0.05_P1.0_V0.7_T25.0.lut")
NAND2_NN_model = pickle.load(open("../../LUT_bin/FINFET_7nm_LSTP_NAND2_VL-0.14_VH0.84_VSTEP0.05_P1.0_V0.7_T25.0.nn", 'r'))
# simulation parameter
t_step = 0.01e-12
t_tot  = 300e-12
C_L = 1e-15
CL_used_before = 2.5e-16
# input signal parameter
m = param = {"vdd": 0.7, "t_0": 5e-12, "t_lh": 50e-12}
constant_signal = Signal(mode="constant", constant = 0.7)

# Primary inputs
input_A   = Signal(mode="ramp_lh",param=m)
input_B   = Signal(mode="ramp_lh",param=m)
input_Cin = Signal(mode="ramp_hl",param=m)
'''
# call simulator
# FA made entirely of NAND2
#---- Level 1
# NAND2 X0
print "Simulating X0"
csm_simulate_NN("NAND2", NAND2_NN_model, NAND2_LUT_and_boundary, {"Vna": input_A, "Vnb": input_B}, {"Vout": 0, "Vn1": 0}, "./circuit_NAND2_X0_out.wv", C_L,  t_step, t_tot)

#---- Level 2
net_1 = Signal(mode="from_file", infile="circuit_NAND2_X0_out.wv")
# NAND2 X1
print "Simulating X1"
csm_simulate_NN("NAND2", NAND2_NN_model, NAND2_LUT_and_boundary, {"Vna": input_A, "Vnb": net_1}, {"Vout": 0, "Vn1": 0}, "./circuit_NAND2_X1_out.wv", C_L,  t_step, t_tot)
# NAND2 X2
print "Simulating X2"
csm_simulate_NN("NAND2", NAND2_NN_model, NAND2_LUT_and_boundary, {"Vna": net_1, "Vnb": input_B}, {"Vout": 0, "Vn1": 0}, "./circuit_NAND2_X2_out.wv", C_L,  t_step, t_tot)

#---- Level 3
net_2 = Signal(mode="from_file", infile="circuit_NAND2_X1_out.wv")
net_3 = Signal(mode="from_file", infile="circuit_NAND2_X2_out.wv")
# NAND2 X3
print "Simulating X3"
csm_simulate_NN("NAND2", NAND2_NN_model, NAND2_LUT_and_boundary, {"Vna": net_2, "Vnb": net_3}, {"Vout": 0, "Vn1": 0}, "./circuit_NAND2_X3_out.wv", C_L,  t_step, t_tot)

#---- Level 4
net_4 = Signal(mode="from_file", infile="circuit_NAND2_X3_out.wv")
# NAND2 X4
print "Simulating X4"
csm_simulate_NN("NAND2", NAND2_NN_model, NAND2_LUT_and_boundary, {"Vna": net_4, "Vnb": input_Cin}, {"Vout": 0, "Vn1": 0}, "./circuit_NAND2_X4_out.wv", C_L,  t_step, t_tot)

#---- Level 5
net_5 = Signal(mode="from_file", infile="circuit_NAND2_X4_out.wv")
# NAND2 X5
print "Simulating X5"
csm_simulate_NN("NAND2", NAND2_NN_model, NAND2_LUT_and_boundary, {"Vna": net_4, "Vnb": net_5}, {"Vout": 0, "Vn1": 0}, "./circuit_NAND2_X5_out.wv", C_L,  t_step, t_tot)
# NAND2 X6
print "Simulating X6"
csm_simulate_NN("NAND2", NAND2_NN_model, NAND2_LUT_and_boundary, {"Vna": net_5, "Vnb": input_Cin}, {"Vout": 0, "Vn1": 0}, "./circuit_NAND2_X6_out.wv", C_L,  t_step, t_tot)
# NAND2 X7
print "Simulating X7"
csm_simulate_NN("NAND2", NAND2_NN_model, NAND2_LUT_and_boundary, {"Vna": net_5, "Vnb": net_1}, {"Vout": 0, "Vn1": 0}, "./circuit_NAND2_X7_out.wv", C_L,  t_step, t_tot)

#---- Level 6
net_6 = Signal(mode="from_file", infile="circuit_NAND2_X5_out.wv")
net_7 = Signal(mode="from_file", infile="circuit_NAND2_X6_out.wv")
# NAND2 X8
print "Simulating X8"
csm_simulate_NN("NAND2", NAND2_NN_model, NAND2_LUT_and_boundary, {"Vna": net_6, "Vnb": net_7}, {"Vout": 0, "Vn1": 0}, "./circuit_NAND2_X8_out.wv", C_L,  t_step, t_tot)

## Sum is out of X8
## Cout is out of X7
'''


# call simulator
# FA made entirely of NAND2
#---- Level 1
# NAND2 X0
print "Simulating X0"
csm_simulate("NAND2", NAND2_LUT_and_boundary, {"Vna": input_A, "Vnb": input_B}, {"Vout": 0, "Vn1": 0}, "./circuit_NAND2_X0_out.wv", C_L,  t_step, t_tot)

#---- Level 2
net_1 = Signal(mode="from_file", infile="circuit_NAND2_X0_out.wv")
# NAND2 X1
print "Simulating X1"
csm_simulate("NAND2", NAND2_LUT_and_boundary, {"Vna": input_A, "Vnb": net_1}, {"Vout": 0, "Vn1": 0}, "./circuit_NAND2_X1_out.wv", C_L,  t_step, t_tot)
# NAND2 X2
print "Simulating X2"
csm_simulate("NAND2", NAND2_LUT_and_boundary, {"Vna": net_1, "Vnb": input_B}, {"Vout": 0, "Vn1": 0}, "./circuit_NAND2_X2_out.wv", C_L,  t_step, t_tot)

#---- Level 3
net_2 = Signal(mode="from_file", infile="circuit_NAND2_X1_out.wv")
net_3 = Signal(mode="from_file", infile="circuit_NAND2_X2_out.wv")
# NAND2 X3
print "Simulating X3"
csm_simulate("NAND2", NAND2_LUT_and_boundary, {"Vna": net_2, "Vnb": net_3}, {"Vout": 0, "Vn1": 0}, "./circuit_NAND2_X3_out.wv", C_L,  t_step, t_tot)

#---- Level 4
net_4 = Signal(mode="from_file", infile="circuit_NAND2_X3_out.wv")
# NAND2 X4
print "Simulating X4"
csm_simulate("NAND2", NAND2_LUT_and_boundary, {"Vna": net_4, "Vnb": input_Cin}, {"Vout": 0, "Vn1": 0}, "./circuit_NAND2_X4_out.wv", C_L,  t_step, t_tot)

#---- Level 5
net_5 = Signal(mode="from_file", infile="circuit_NAND2_X4_out.wv")
# NAND2 X5
print "Simulating X5"
csm_simulate("NAND2", NAND2_LUT_and_boundary, {"Vna": net_4, "Vnb": net_5}, {"Vout": 0, "Vn1": 0}, "./circuit_NAND2_X5_out.wv", C_L,  t_step, t_tot)
# NAND2 X6
print "Simulating X6"
csm_simulate("NAND2", NAND2_LUT_and_boundary, {"Vna": net_5, "Vnb": input_Cin}, {"Vout": 0, "Vn1": 0}, "./circuit_NAND2_X6_out.wv", C_L,  t_step, t_tot)
# NAND2 X7
print "Simulating X7"
csm_simulate("NAND2", NAND2_LUT_and_boundary, {"Vna": net_5, "Vnb": net_1}, {"Vout": 0, "Vn1": 0}, "./circuit_NAND2_X7_out.wv", C_L,  t_step, t_tot)

#---- Level 6
net_6 = Signal(mode="from_file", infile="circuit_NAND2_X5_out.wv")
net_7 = Signal(mode="from_file", infile="circuit_NAND2_X6_out.wv")
# NAND2 X8
print "Simulating X8"
csm_simulate("NAND2", NAND2_LUT_and_boundary, {"Vna": net_6, "Vnb": net_7}, {"Vout": 0, "Vn1": 0}, "./circuit_NAND2_X8_out.wv", C_L,  t_step, t_tot)

## Sum is out of X8
## Cout is out of X7