import os
import sys
import importlib
import numpy as np

class Esim:
    def __init__(self, config_file):
        self.sp_data_dir = './output_spice/'
        self.csm_data_dir = './output_csm/'
        self.config = importlib.import_module(config_file)
        self.sp_out_path = self.sp_data_dir + self.config.CKT + '.out'
        self.sp_wv_path = self.sp_out_path.replace('.out', '.wv')
        # should this csm out name hardcoded ??
        self.csm_wv_path = self.csm_data_dir + 'voltage_save.csv'
        
    def string2float(self, s):
        if s[-1] == 'm':
            s = s.replace('m', 'e-3')
        elif s[-1] == 'u':
            s = s.replace('u', 'e-6')
        elif s[-1] == 'n':
            s = s.replace('n', 'e-9')
        elif s[-1] == 'p':
            s = s.replace('p', 'e-12')
        elif s[-1] == 'f':
            s = s.replace('f', 'e-15')
        elif s[-1] == 'a':
            s = s.replace('a', 'e-18')
        return float(s)
        
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
                        line = [self.string2float(t) for t in line]
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

#es = Esim("config")
#es.data_extract()
#es.Esim_calculate()