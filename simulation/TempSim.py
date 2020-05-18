import importlib
import matplotlib
import matplotlib.pyplot as plt
import glob
import os
from classes import *
from SpiceSim import *
from plot import *
from Esim import *

class TempSim:
    '''
    based on "config_temp.py" file which contains a temperature list including multiple temperatures,
    we simulate both spice and CSM and plot two waveform images which are CSM's and spice's,
    and they both contain simulation results in different temperatures. 
    This is for PVT simulation and plot
    '''
    def __init__(self, config_file):
        self.config_name = config_file
        self.config = importlib.import_module(config_file)
        self.temp_list = self.config.TEMPERATURE_list
        self.sp_data_dir = self.config.SP_DATA_DIR
        self.sp_wv_path = dict()
        for temp in self.temp_list:
            self.sp_wv_path[str(temp)] = self.sp_data_dir + self.config.CKT + '_' + self.config.TECH + "_VL" + \
                                         str(self.config.VL) + "_VH" + str(self.config.VH) + "_VSTEP" + \
                                         str(self.config.VSTEP) + "_P" + str(self.config.PROCESS_VARIATION) + "_V" \
                                         + str(self.config.VDD) + "_T" + str(temp) + "_TSTEP" + str(self.config.T_STEP) + '.wv'
        self.csm_wv_path = self.config.save_file_path
       
    def temp_sim(self):
        fin = open(self.config_name + ".py", "r")
        ori_config = fin.readlines()
        fin.close()
        i = 0
        self.conf = dict()
        for temp in self.temp_list:
            fout = open(self.config_name + "_" + str(i) + ".py", "w")
            for line in ori_config:
                if "TEMPERATURE_list = " in line:
                    fout.write("TEMPERATURE = " + str(temp) + "\n")
                elif "save_file_path = " in line or "for temp in TEMPERATURE_list" in line:
                    continue
                elif "save_file_path[str(temp)]" in line:
                    line = line.replace("save_file_path[str(temp)]", "save_file_path")
                    line = line.strip("    ")
                    fout.write(line)
                elif "str(temp)" in line:
                    fout.write(line.replace("str(temp)", "str(TEMPERATURE)"))
                else:
                    fout.write(line)
            fout.close()
            # simulate CSM
            v_path = self.config.VERILOG_DIR + self.config.CKT + ".v"
            self.conf[i] = importlib.import_module(self.config_name + "_" + str(i))
            ckt = Circuit(verilog_path=v_path, config=self.conf[i])
            ckt.read_netlist()
            ckt.levelize()
            ckt.set_caps()
            ckt.init_ckt()
            ckt.simulate_signal()
            # simulate Spice
            ss = SpiceSim(self.config_name + "_" + str(i))
            ss.simulate_hspice()
            es = Esim(self.config_name + "_" + str(i))
            es.data_extract()
            os.system("rm " + self.config_name + "_" + str(i) + ".py")
            os.system("rm " + self.config_name + "_" + str(i) + ".pyc")            
            i += 1
    
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
    
    def temp_plot(self):
        data_dict = dict()
        for temp in self.temp_list:
            f_in = [self.sp_wv_path[str(temp)], self.csm_wv_path[str(temp)]]
            for each_file in f_in:
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
                    data[each_key] = self.drop_resolution(data[each_key], drop_factor=20)

                data_dict[str(temp)] = data
        # print data_dict
            
        print "auto plot and save for CSM..."
        # CSM plotting
        for temp in self.temp_list:
            CSM_plot_nodes = self.config.voltage_nodes_to_save
            for a_signal in CSM_plot_nodes:
                time = data_dict[str(temp)]["time"]
                data = data_dict[str(temp)][a_signal]
                plt.plot(time, data, label="CSM_" + a_signal + str(temp) + "C")
            
        plt.xlabel('time')
        plt.ylabel('voltages')
        plt.title("CSM_" + self.config.CKT + '_' + self.config.TECH + "_VL" + \
                    str(self.config.VL) + "_VH" + str(self.config.VH) + "_VSTEP" + \
                    str(self.config.VSTEP) + "_P" + str(self.config.PROCESS_VARIATION) + "_V" \
                    + str(self.config.VDD) + "_Multi_Temperatures")
        plt.legend()
        plt.savefig('image/' + "CSM_" + self.config.CKT + '_' + self.config.TECH + "_VL" + \
                    str(self.config.VL) + "_VH" + str(self.config.VH) + "_VSTEP" + \
                    str(self.config.VSTEP) + "_P" + str(self.config.PROCESS_VARIATION) + "_V" \
                    + str(self.config.VDD) + "_Multi_Temperatures" + "_TSTEP" + str(self.config.T_STEP) + '.pdf')
        print "auto plot and save successfully"

        print "auto plot and save for Hspice..."
        # spice plotting
        for temp in self.temp_list:
            spice_plot_nodes = self.config.voltage_nodes_to_save
            for a_signal in spice_plot_nodes:
                time = data_dict[str(temp)]["time"]
                data = data_dict[str(temp)][a_signal]
                plt.plot(time, data, label="spice_" + a_signal + str(temp) + "C")
            
        plt.xlabel('time')
        plt.ylabel('voltages')
        plt.title("spice_" + self.config.CKT + '_' + self.config.TECH + "_VL" + \
                    str(self.config.VL) + "_VH" + str(self.config.VH) + "_VSTEP" + \
                    str(self.config.VSTEP) + "_P" + str(self.config.PROCESS_VARIATION) + "_V" \
                    + str(self.config.VDD) + "_Multi_Temperatures")
        plt.legend()
        plt.savefig('image/' + "spice_" + self.config.CKT + '_' + self.config.TECH + "_VL" + \
                    str(self.config.VL) + "_VH" + str(self.config.VH) + "_VSTEP" + \
                    str(self.config.VSTEP) + "_P" + str(self.config.PROCESS_VARIATION) + "_V" \
                    + str(self.config.VDD) + "_Multi_Temperatures" + "_TSTEP" + str(self.config.T_STEP) + '.pdf')
        print "auto plot and save successfully"

ts = TempSim("config_temp")
ts.temp_sim()
# ts.temp_plot()
        