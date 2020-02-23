from csm_simulator import *
import pickle

#INV_LUT_and_boundary   = load_LUT("../LUT_bin/FINFET_7nm_HP_INV_VL-0.35_VH1.05_VSTEP0.1_P1.0_V0.7_T25.0.lut")
#NAND2_LUT_and_boundary = load_LUT("../LUT_bin/FINFET_7nm_HP_NAND2_VL-0.35_VH1.05_VSTEP0.1_P1.0_V0.7_T25.0.lut")
#csm_simulate("INV", INV_LUT_and_boundary, signal, {"Vout": 0}, "./csm_test_out.wv", C_L,  t_step, t_tot)
#csm_simulate("NAND2", NAND2_LUT_and_boundary, {"Vna": signal, "Vnb": signal}, {"Vout": 0, "Vn1": 0}, "./csm_test_out.wv", C_L,  t_step, t_tot)

'''
# NAND2 MOSFET 16nm LP
# load LUT and NN
NAND2_LUT_and_boundary = load_LUT("../LUT_bin/MOSFET_16nm_LP_NAND2_VL-0.45_VH1.35_VSTEP0.1_P1.0_V1.0_T25.lut")
NAND2_NN_model = pickle.load(open("../LUT_bin/MOSFET_16nm_LP_NAND2_VL-0.45_VH1.35_VSTEP0.1_P1.0_V1.0_T25.nn", 'r'))
# simulation parameter
t_step = 0.1e-12
t_tot  = 500e-12
C_L = 1e-15
# input signal parameter
m = param = {"vdd": 0.9, "t_0": 5e-12, "t_lh": 50e-12}
signal          = Signal(mode="ramp_hl", param=m)
constant_signal = Signal(mode="constant", constant = 0.9)
# call simulator
csm_simulate_NN("NAND2", NAND2_NN_model, NAND2_LUT_and_boundary, {"Vna": signal, "Vnb": constant_signal}, {"Vout": 0, "Vn1": 0}, "./csm_test_out.wv", C_L,  t_step, t_tot)
'''
'''
# NAND2 FINFET 7nm HP
# load LUT and NN
NAND2_LUT_and_boundary = load_LUT("../LUT_bin/FINFET_7nm_HP_NAND2_VL-0.14_VH0.84_VSTEP0.05_P1.0_V0.7_T25.0.lut")
NAND2_NN_model = pickle.load(open("../LUT_bin/FINFET_7nm_HP_NAND2_VL-0.14_VH0.84_VSTEP0.05_P1.0_V0.7_T25.0.nn", 'r'))
# simulation parameter
t_step = 0.01e-12
t_tot  = 200e-12
C_L = 1e-15
# input signal parameter
m = param = {"vdd": 0.7, "t_0": 5e-12, "t_lh": 50e-12}
signal          = Signal(mode="ramp_hl", param=m)
constant_signal = Signal(mode="constant", constant = 0.7)
# call simulator
csm_simulate_NN("NAND2", NAND2_NN_model, NAND2_LUT_and_boundary, {"Vna": signal, "Vnb": constant_signal}, {"Vout": 0, "Vn1": 0}, "./csm_test_out.wv", C_L,  t_step, t_tot)
'''

# NAND2 FINFET 7nm LSTP
# load LUT and NN
NAND2_LUT_and_boundary = load_LUT("../LUT_bin/FINFET_7nm_LSTP_NAND2_VL-0.14_VH0.84_VSTEP0.05_P1.0_V0.7_T25.0.lut")
NAND2_NN_model = pickle.load(open("../LUT_bin/FINFET_7nm_LSTP_NAND2_VL-0.14_VH0.84_VSTEP0.05_P1.0_V0.7_T25.0.nn", 'r'))
# simulation parameter
t_step = 0.01e-12
t_tot  = 200e-12
C_L = 1e-15
# input signal parameter
m = param = {"vdd": 0.7, "t_0": 5e-12, "t_lh": 50e-12}
signal          = Signal(mode="ramp_hl", param=m)
constant_signal = Signal(mode="constant", constant = 0.7)
# call simulator
csm_simulate_NN("NAND2", NAND2_NN_model, NAND2_LUT_and_boundary, {"Vna": signal, "Vnb": constant_signal}, {"Vout": 0, "Vn1": 0}, "./csm_test_out.wv", C_L,  t_step, t_tot)