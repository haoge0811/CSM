# Author: haoge <haoge@usc.edu> at USC SPORT Lab
import numpy as np
import pickle

# this function look up value from LUT using multi-dimension linear interpolation
# current voltages is passed in as a dict. in order to have 1 function for all gates
def read_LUT(LUT_and_boundary, GATE_NAME, voltages_now):
    # un pack
    LUT=LUT_and_boundary["LUT"]
    V_L=LUT_and_boundary["V_L"]
    V_H=LUT_and_boundary["V_H"]
    VSTEP=LUT_and_boundary["VSTEP"]

    # sainity check for debug
    for each_voltage in voltages_now.keys():
        if voltages_now[each_voltage] < V_L:
            print("Error, \"" + each_voltage + "\" value for interpolation is out of lower bound...")
            print("Python exiting...")
            exit()
        elif voltages_now[each_voltage] > V_H:
            print("Error, \"" + each_voltage + "\" value for interpolation is out of upper bound...")
            print("Python exiting...")
            exit()

    if (GATE_NAME == "INV"):
        (Vin_low_idx, a_Vin)   = get_interpolation_params(voltages_now["Vin"], V_L, VSTEP)
        (Vout_low_idx, a_Vout) = get_interpolation_params(voltages_now["Vout"], V_L, VSTEP)

        result = dict()
        for each_component_name in LUT.keys():
            each_component = LUT[each_component_name]
            # select a small section of LUT
            mat = each_component[Vin_low_idx:Vin_low_idx + 2, Vout_low_idx:Vout_low_idx + 2]
            # 2D linear interpolation
            val = a_Vin * a_Vout * mat[0, 0] + (1 - a_Vin) * a_Vout * mat[1, 0] + \
                  a_Vin * (1 - a_Vout) * mat[0, 1] + (1 - a_Vin) * (1 - a_Vout) * mat[1, 1]
            result[each_component_name] = val

    elif (GATE_NAME == "NAND2") or (GATE_NAME == "NOR2"):
        (Vna_low_idx, a_Vna)   = get_interpolation_params(voltages_now["Vna"], V_L, VSTEP)
        (Vnb_low_idx, a_Vnb)   = get_interpolation_params(voltages_now["Vnb"], V_L, VSTEP)
        (Vn1_low_idx, a_Vn1)   = get_interpolation_params(voltages_now["Vn1"], V_L, VSTEP)
        (Vout_low_idx, a_Vout) = get_interpolation_params(voltages_now["Vout"], V_L, VSTEP)

        result = dict()
        for each_component_name in LUT.keys():
            each_component = LUT[each_component_name]
            # select a section of table to output. Order of index terms need to match the order previously stored.
            mat = each_component[Vna_low_idx:Vna_low_idx + 2, Vnb_low_idx:Vnb_low_idx + 2, Vn1_low_idx:Vn1_low_idx + 2,
                  Vout_low_idx:Vout_low_idx + 2]
            # 4D linear interpolation
            val = 0
            for D1 in range(2):
                for D2 in range(2):
                    for D3 in range(2):
                        for D4 in range(2):
                            if D1 == 0:
                                param1 = (1 - a_Vna)
                            else:
                                param1 = a_Vna
                            if D2 == 0:
                                param2 = (1 - a_Vnb)
                            else:
                                param2 = a_Vnb
                            if D3 == 0:
                                param3 = (1 - a_Vn1)
                            else:
                                param3 = a_Vn1
                            if D4 == 0:
                                param4 = (1 - a_Vout)
                            else:
                                param4 = a_Vout

                            partial_val = mat[D1, D2, D3, D4] * param1 * param2 * param3 * param4
                            val += partial_val
            # testing and comparing purposes
            # val1 = mat.mean() # use mean value of matrix for test run
            # print"\nmatrix_mean", val1, "      interpolate", val, "\n"
            result[each_component_name] = val
    else:
        print "Cannot read from LUT, Invalid or not yet implemented gate name."
    return result

# a sub-function used by read LUT function
def get_interpolation_params(voltage, V_L, VSTEP):
    # since it's low_idx, we should use floor instead of round
    voltage_low_idx = int(np.floor((voltage - V_L) / VSTEP))
    voltage_low = voltage_low_idx * VSTEP + V_L  # floored voltage value to closest LUT stored voltage value

    # deviation factor for interpolation
    a_voltage = ((voltage - voltage_low) / VSTEP)
    return (voltage_low_idx, a_voltage)

def load_LUT(LUT_dir):
    LUT = pickle.load(open(LUT_dir, 'r'))

    # extract V_L, V_H, VSTEP value from file name
    extracted_list = LUT_dir.split("_")
    for a_section in extracted_list:
        if "VL" in a_section:
            V_L = float(a_section[2:])
        if "VH" in a_section:
            V_H = float(a_section[2:])
        if "VSTEP" in a_section:
            VSTEP = float(a_section[5:])

    return {"LUT": LUT, "V_L": V_L, "V_H": V_H, "VSTEP": VSTEP}



# maybe don't use this, use another function called signal generator, so that we can generate noise signal also there
class Signal:
    time = 0

    # set default as None is user do not input
    def __init__(self, mode, infile=None, param=None, constant=0):
        self.mode = mode
        self.param = param
        self.constant = constant

        # if user inputed infile name, then read up infile ot be an array
        if (infile != None):
            # open and read up csm input file as an object, later we can just query it
            input_file = open(infile, "r")

            # TODO: the structure of input array should allow interpolation when being queried
            # so that the input file time step does not have to match the simulation time step
            # input file can just be a piece wise linear source.
            # for now let just assume it's the same time step

            # empty array
            time_array = []
            v_in_array = []

            for a_line in input_file:
                # input file use # as comment sign
                if (a_line[0] != "#"):
                    a_line = a_line.split()
                    a_line = [float(t) for t in a_line]

                    time_array.append(a_line[0])
                    # look at the last column, as we put Vout of previous gate there
                    # previous Vout becomes v_in here
                    v_in_array.append(a_line[-1])

            # combine to be complete input array
            # time array is stored for later interpolation purpose

            self.input_array = [time_array, v_in_array]
            input_file.close()

        else:
            self.input_array = None

    def get_val(self, t):
        if self.mode == "ramp_lh":
            # 0 to vdd ramp, start at time t_0, rise finish at time config.T_DR_TRAN
            if t < self.param["t_0"]:
                sig = 0
            elif t < (self.param["t_0"] + self.param["t_lh"]):
                # linear up ramp
                sig = self.param["vdd"] * (t - self.param["t_0"]) / self.param["t_lh"]
            else:
                sig = self.param["vdd"]
            return sig
        elif self.mode == "ramp_hl":
            if t < self.param["t_0"]:
                sig = self.param["vdd"]
            elif t < (self.param["t_0"] + self.param["t_lh"]):
                sig = self.param["vdd"] * (1 - (t - self.param["t_0"]) / self.param["t_lh"])
            else:
                sig = 0
            return sig
        elif self.mode == "from_file":
            t_step = 0.01e-12  # should be the t_step of input file

            index = int(np.round(t / t_step, 3))

            sig = self.input_array[1][index]
            return sig

        elif self.mode == "constant":
            sig = self.constant
            return sig


def circuit_levelizer():
    pass