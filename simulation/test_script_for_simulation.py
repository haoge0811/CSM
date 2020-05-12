import os
import os.path
from os import path
import csv

'''
tech_list: choose from "FINFET_7nm_HP", "FINFET_7nm_LSTP", "MOSFET_16nm_HP", "MOSFET_16nm_LP"
vstep_list: choose from 0.1, 0.075, 0.05, 0.025
tstep_list: choose from 0.01e-12, 0.1e-12, 1e-12
VDD, VL, VH need to be changed based on technology
'''
CKT = "c17"
tech_list = ["MOSFET_16nm_HP", "MOSFET_16nm_LP"]
vstep_list = [0.1, 0.05]
tstep_list = [0.01e-12, 0.1e-12, 1e-12]

old_config = open("config.py", "r")
o_c = old_config.readlines()
old_config.close()

n = len(tech_list)*len(vstep_list)*len(tstep_list)
form = [[] for i in range(0, n)]
config = [[] for i in range(0, n)]
i = 0
for tech in tech_list:
    for vstep in vstep_list:
        for tstep in tstep_list:
            temp_config = open("temp_config.py", "w")
            for line in o_c:
                if "TECH = " in line:
                    temp_config.write("TECH = " + '"' + tech + '"' + "\n")
                elif "VSTEP = " in line:
                    temp_config.write("VSTEP = " + str(vstep) + "\n")
                elif "T_STEP = " in line:
                    temp_config.write("T_STEP = " + str(tstep) + "\n")
                elif "VDD = " in line:
                    if tech == "MOSFET_16nm_LP":
                        temp_config.write("VDD = " + str(0.9) + "\n")
                        VDD = 0.9
                    else:
                        temp_config.write("VDD = " + str(0.7) + "\n")
                        VDD = 0.7
                elif "VL = " in line:
                    if tech == "MOSFET_16nm_LP":
                        temp_config.write("VL = " + str(-0.18) + "\n")
                        VL = -0.18
                    else:
                        temp_config.write("VL = " + str(-0.14) + "\n")
                        VL = -0.14
                elif "VH = " in line:
                    if tech == "MOSFET_16nm_LP":
                        temp_config.write("VH = " + str(1.08) + "\n")
                        VH = 1.08
                    else:
                        temp_config.write("VH = " + str(0.84) + "\n")
                        VH = 0.84
                else:
                    temp_config.write(line)
            temp_config.close()
            os.system("python main.py -func esim-all -conf temp_config.py")
            esim_path = "output_esim/" + CKT + '_' + tech + "_VL" + \
                        str(VL) + "_VH" + str(VH) + "_VSTEP" + \
                        str(vstep) + "_P" + str(1.0) + "_V" \
                        + str(VDD) + "_T" + str(25.0) + "_TSTEP" + str(tstep) + '.esim'
            form[i].append(tech)
            form[i].append(str(vstep))
            form[i].append(str(tstep))
            if path.exists(esim_path):
                f_esim = open(esim_path, "r")
                for line in f_esim:
                    esim_num = line.split(" = ")[-1].strip('\n')
                    form[i].append(esim_num)
            else:
                form[i].append("failed")
            i = i + 1
# print form
with open('output_esim/experiment_results.csv', 'w') as csvfile:
    writer=csv.writer(csvfile)
    writer.writerow(['TECH','VSTEP','TSTEP','Esim for all outputs'])
    writer.writerows(form)