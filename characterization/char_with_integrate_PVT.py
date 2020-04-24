# Author: haoge <haoge@usc.edu> at USC SPORT Lab
import config
import characterisation
import numpy as np
import pickle
import os

def main(GATE_NAME, VSTEP, LIB_DIR, VDD_L, VDD_H, VDD_STEP, T_L, T_H, T_STEP):
    VDD_list = np.linspace(VDD_L, VDD_H, int((VDD_H - VDD_L) / VDD_STEP) + 1)
    VDD_list = [np.round(k, 2) for k in VDD_list] # rounding
    T_list = np.linspace(T_L, T_H, int((T_H - T_L) / T_STEP) + 1)
    T_list = [np.round(k, 2) for k in T_list]

    integrated_LUT = None

    # to fix a bug, that higher VDD LUT size is larger than lower VDD LUT size, VDD is used high to low
    VDD_list.sort(reverse=True)
    for VDD in VDD_list:
        for TEMPERATURE in T_list:
            unique_id = characterisation.main(GATE_NAME, VSTEP, LIB_DIR, VDD, TEMPERATURE, return_unique_id = 1)
            # output is going to be at LUT_bin/unique_id.lut
            LUT = pickle.load(open(config.LUT_bin_dir + unique_id + ".lut", 'r'))

            # initialization
            if (integrated_LUT == None): # this is the first LUT
                integrated_LUT = dict()
                for each_item in LUT.keys():
                    if (each_item != "header_info"): # extract data
                        # large LUT. VDD is first axis, T is second axis
                        LUT_shape = LUT[each_item].shape
                        LUT_shape = list(LUT_shape)
                        LUT_shape.extend([len(VDD_list), len(T_list)]) # adding 2 more dimensions.
                        # by extend, VDD and TEMPERATURE are put as 2 last dimensions
                        integrated_LUT[each_item] = np.ndarray(LUT_shape)

            # usual LUT opening
            #open LUT, put the entire LUT in temp dimension according position. vdd dimension according position
            VDD_idx  = int(np.round((VDD         - VDD_L)/VDD_STEP, 3))
            T_idx    = int(np.round((TEMPERATURE - T_L  )/T_STEP  , 3))
            for each_item in LUT.keys():
                if (each_item != "header_info"): # exclude header info
                    for coordiante, value in np.ndenumerate(LUT[each_item]):
                        new_coordiante = list(coordiante)
                        new_coordiante = [int(k) for k in new_coordiante]
                        new_coordiante.extend([VDD_idx, T_idx])
                        new_coordiante = tuple(new_coordiante)
                        integrated_LUT[each_item][new_coordiante] = value

            # os remove the intermediate LUT to save space.
            os.system("rm " + config.LUT_bin_dir + unique_id + ".lut")


    # trimming the unique_id name
    unique_id = unique_id.split("_")
    unique_id = unique_id[:-2] # get rid of V and T in name
    unique_id = "_".join(unique_id)

    # adding header information in large LUT
    integrated_LUT["header_info"] = LUT[["header_info"]]
    # some modificatino in header info
    del integrated_LUT["header_info"]["PROCESS"]
    del integrated_LUT["header_info"]["VDD"]
    del integrated_LUT["header_info"]["TEMPERATURE"]

    integrated_LUT["header_info"].update({"VDD_L":VDD_L, "VDD_H":VDD_H, "VDD_STEP":VDD_STEP,
                                          "T_L": VDD_L, "T_H": VDD_H, "T_STEP": VDD_STEP})

    # dumping the large LUT
    pickle.dump(integrated_LUT, open(config.LUT_bin_dir + unique_id + ".lut", 'w'))

