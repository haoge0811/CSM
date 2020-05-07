import importlib
import matplotlib
import matplotlib.pyplot as plt
import glob
from func_spice import *

class plot:
    def __init__(self, config_file):
        self.config = importlib.import_module(config_file)
        self.sp_data_dir = self.config.SP_DATA_DIR
        self.csm_data_dir = self.config.CSM_DATA_DIR
        self.sp_out_path = self.sp_data_dir + self.config.CKT + '.out'
        self.sp_wv_path = self.sp_out_path.replace('.out', '.wv')
        self.csm_wv_path = self.csm_data_dir + 'voltage_save.csv'
        # list the file to be ploted here, then go to bottom to plot to your liking.
        # can use wildcard here e.g. *NAND2* glob is used to expand wildcard
        self.files = [self.csm_wv_path, self.sp_wv_path]


    def drop_resolution(self, input_list, drop_factor = 10):
        counter = 0
        output_list = []
        for element in input_list:
            if counter == (drop_factor-1):
                output_list.append(element)
                counter = 0
            else:
                counter += 1
        return output_list

    def auto_plot(self):
        '''
        read output data of spice and CSM simulation;
        plot out the low resolution waveform of them
        '''
        data_dict = dict()
        for each_file in self.files:
            infile = open(each_file, "r")
            data = dict()
            title = ["time"] + self.config.voltage_nodes_to_save
            for item in title:
                data[item] = []
            for line in infile:
                if line[0] == "#": # title line of csm data
                    continue
                else:
                    line = line.replace(',', ' ').split()
                    for i in range(len(line)):
                        data[title[i]].append(string2float(line[i]))
            infile.close()

            # everything drop resolution, so plot is quicker
            for each_key in data.keys():
                data[each_key] = self.drop_resolution(data[each_key], drop_factor=200)

            data_dict[each_file] = data
        
        # CSM plotting
        CSM_plot_nodes = self.config.voltage_nodes_to_save
        for a_signal in CSM_plot_nodes:
            time = data_dict[self.files[0]]["time"]
            data = data_dict[self.files[0]][a_signal]
            plt.plot(time, data, label="CSM_"+a_signal)

        # spice plotting
        spice_plot_nodes = self.config.voltage_nodes_to_save
        for a_signal in spice_plot_nodes:
            time = data_dict[self.files[1]]["time"]
            data = data_dict[self.files[1]][a_signal]
            plt.plot(time, data, label="spice_"+a_signal)
        
        plt.xlabel('time')
        plt.ylabel('voltages')
        plt.title('Comparation of CSM and Hspice simulation for ' + self.config.CKT)
        plt.legend()
        plt.show()

# pp = plot("config_inv")
# pp.auto_plot()