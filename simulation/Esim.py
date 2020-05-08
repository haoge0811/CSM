import os
import sys
import importlib
from func_spice import *
import numpy as np

class Esim:
    def __init__(self, config_file):
        self.config = importlib.import_module(config_file)
        self.sp_data_dir = self.config.SP_DATA_DIR
        self.csm_data_dir = self.config.CSM_DATA_DIR
        self.sp_out_path = self.sp_data_dir + self.config.CKT + '.out'
        self.sp_wv_path = self.sp_out_path.replace('.out', '.wv')
        self.csm_wv_path = self.config.save_file_dir
        
    def data_extract(self):
        '''extract data from .out file of spice simulation into .wv'''
        infile_spice = open(self.sp_out_path, 'r')
        outfile_spice = open(self.sp_wv_path, 'w')
        record_flag = 0
        skip_counter = 0
        for line in infile_spice:
            if line[0] == 'x':
                record_flag = 1
                skip_counter = 0
            elif line[0] == 'y':
                record_flag =0
            else:
                if record_flag == 1: # once in the target data block
                    
                    if skip_counter < 3: # skip 3 line of blank space
                       skip_counter += 1
                    else:
                        line = line.split()
                        # convert si unit to e"notation"
                        line = [string2float(t) for t in line]
                        line = [str(t) for t in line]
                        #
                        line = ' '.join(line)
                        line = line + "\n"

                        outfile_spice.write(line)

        infile_spice.close()
        outfile_spice.close()
    
    def Esim_calculate(self):
        '''Calculate wave similarity given the path of csm and spice waveform data'''
        print("\n# Output wave similarity calculation:\n# Mean of absolute point wise difference, nomalize by vdd value...\n")
        csm_infile   = open(self.csm_wv_path,"r")
        spice_infile = open(self.sp_wv_path,"r")

        # read up data into array
        num_of_voltage = len(self.config.voltage_nodes_to_save)
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
        vdd = self.config.VDD

        difference = np.subtract(csm_voltages, spice_voltages)
        absolute   = np.absolute(difference)
        mean_Vout = np.mean(absolute,axis=0)

        similarity_Vout = [x for x in range(num_of_voltage)]
        # best case mean = 0, similarity = 1. worst case, every point differs by vdd, similarity = 0.
        for i in range(num_of_voltage):
            similarity_Vout[i]  = 1 - mean_Vout[i]/vdd
            print("V" + self.config.voltage_nodes_to_save[i] + " similarity = %.4f%%\n" % (similarity_Vout[i]*100))

    def Esim_calculate_without_config(self, wv_1, wv_2, vdd):
        '''Calculate wave similarity given the path of any two waveform data files and vdd'''
        print("\n# Output wave similarity calculation:\n# Mean of absolute point wise difference, nomalize by vdd value...\n")
        wv_1_infile = open(wv_1,"r")
        wv_2_infile = open(wv_2,"r")

        line = wv_1_infile.readlines()[1]
        if ',' in line:
            num_of_voltage = len(line.split(',')[1:])
        else:
            num_of_voltage = len(line.split(' ')[1:])
        
        wv_1_infile.close()
        wv_1_infile = open(wv_1,"r")
        # read up data into array
        wv_1_temp = []
        wv_1_voltages = []
        for line in wv_1_infile:
            if (line[0] != "#"):
                for i in range(num_of_voltage):
                    Vouti_now = float(line.split(',')[i+1])
                    wv_1_temp.append(Vouti_now)
                wv_1_voltages.append(wv_1_temp)
                wv_1_temp = []

        wv_2_voltages = []
        wv_2_temp = []
        for line in wv_2_infile:
            if (line[0] != "#"):
                for i in range(num_of_voltage):
                    Vouti_now = float(line.split()[i+1])
                    wv_2_temp.append(Vouti_now)
                wv_2_voltages.append(wv_2_temp)
                wv_2_temp = []
        
        if (np.size(wv_1_voltages) < np.size(wv_2_voltages)):
            wv_2_voltages = wv_2_voltages[:-1]
        elif (np.size(wv_1_voltages) > np.size(wv_2_voltages)):
            wv_1_voltages = wv_1_voltages[:-1]
        
        wv_1_infile.close()
        wv_2_infile.close()

        # similarity calculation
        # convert to numpy array
        wv_1_voltages = np.asarray(wv_1_voltages)
        wv_2_voltages = np.asarray(wv_2_voltages)

        # mean of absolute point wise difference, nomalize by vdd value
        difference = np.subtract(wv_1_voltages, wv_2_voltages)
        absolute   = np.absolute(difference)
        mean_Vout = np.mean(absolute,axis=0)

        similarity_Vout = [x for x in range(num_of_voltage)]
        # best case mean = 0, similarity = 1. worst case, every point differs by vdd, similarity = 0.
        for i in range(num_of_voltage):
            similarity_Vout[i]  = 1 - mean_Vout[i]/vdd
            print("V" + str(i) + " similarity = %.4f%%\n" % (similarity_Vout[i]*100))

# es = Esim("config")
# es.data_extract()
# es.Esim_calculate()
# es.Esim_calculate_without_config("./output_csm/voltage_save.csv", "./output_spice/c17.wv", 0.7)