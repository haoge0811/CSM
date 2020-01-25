from csm_simulator import *

INV_LUT_and_boundary   = load_LUT("../LUT_bin/FINFET_7nm_HP_INV_VL-0.35_VH1.05_VSTEP0.1_P1.0_V0.7_T25.0.lut")
NAND2_LUT_and_boundary = load_LUT("../LUT_bin/FINFET_7nm_HP_NAND2_VL-0.35_VH1.05_VSTEP0.1_P1.0_V0.7_T25.0.lut")
#NAND2_LUT_and_boundary = load_LUT("../LUT_bin/MOSFET_16nm_LP_NAND2_VL-0.45_VH1.35_VSTEP0.1_P1.0_V1.0_T25.lut")


t_step = 0.1e-12
t_tot  = 100e-12
C_L = 1e-15

m = param = {"vdd": 0.61, "t_0": 5e-12, "t_lh": 50e-12}
signal          = Signal(mode="ramp_hl", param=m)
constant_signal = Signal(mode="constant", constant = 0.6)

#csm_simulate("INV", INV_LUT_and_boundary, signal, {"Vout": 0}, "./csm_test_out.wv", C_L,  t_step, t_tot)

csm_simulate("NAND2", NAND2_LUT_and_boundary, {"Vna": signal, "Vnb": signal}, {"Vout": 0, "Vn1": 0}, "./csm_test_out.wv", C_L,  t_step, t_tot)
