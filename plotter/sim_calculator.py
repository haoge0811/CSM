import os
import sys
import numpy as np

def sim_calculator(csm_wv_dir, spice_wv_dir, char_list):
    #Calculate wave similarity

    print("\n# Output wave similarity calculation:\n# Mean of absolute point wise difference, nomalize by vdd value...\n")

    csm_infile   = open(csm_wv_dir,"r")
    spice_infile = open(spice_wv_dir,"r")

    # read up data into array
    num_of_voltage = len(char_list["saved_voltage"])
    csm_temp = []
    csm_voltages = []
    for line in csm_infile:
        if (line[0] != "#"):
            for i in range(num_of_voltage):
                Vouti_now = float(line.split(',')[i+1])
                csm_temp.append(Vouti_now)
            csm_voltages.append(csm_temp)
            csm_temp = []

    spice_voltages = []
    spice_temp = []
    for line in spice_infile:
        if (line[0] != "#"):
            for i in range(num_of_voltage):
                Vouti_now = float(line.split()[i+1])
                spice_temp.append(Vouti_now)
            spice_voltages.append(spice_temp)
            spice_temp = []
    spice_voltages = spice_voltages[:-1]
    
    csm_infile.close()
    spice_infile.close()

    # similarity calculation
    # convert to numpy array
    csm_voltages = np.asarray(csm_voltages)
    spice_voltages = np.asarray(spice_voltages)

    # mean of absolute point wise difference, nomalize by vdd value
    vdd = char_list["vdd"]

    difference = np.subtract(csm_voltages, spice_voltages)
    absolute   = np.absolute(difference)
    mean_Vout = np.mean(absolute,axis=0)

    similarity_Vout = [x for x in range(num_of_voltage)]
    # best case mean = 0, similarity = 1. worst case, every point differs by vdd, similarity = 0.
    for i in range(num_of_voltage):
        similarity_Vout[i]  = 1 - mean_Vout[i]/vdd
        print("V" + char_list["saved_voltage"][i] + " similarity = %.4f%%\n" % (similarity_Vout[i]*100))

