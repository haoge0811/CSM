import os

'''
tech_list: choose from "FINFET_7nm_HP", "FINFET_7nm_LSTP", "MOSFET_16nm_HP", "MOSFET_16nm_LP"
vstep_list: choose from 0.1, 0.075, 0.05, 0.025
tstep_list: choose from 0.01e-12, 0.1e-12, 1e-12
VDD, VL, VH need to be changed based on technology
'''

tech_list = ["MOSFET_16nm_HP", "MOSFET_16nm_LP"]
vstep_list = [0.1, 0.05]
tstep_list = [0.01e-12, 0.1e-12, 1e-12]

old_config = open("config.py", "r")
o_c = old_config.readlines()
old_config.close()

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
                    else:
                        temp_config.write("VDD = " + str(0.7) + "\n")
                elif "VL = " in line:
                    if tech == "MOSFET_16nm_LP":
                        temp_config.write("VL = " + str(-0.18) + "\n")
                    else:
                        temp_config.write("VL = " + str(-0.14) + "\n")
                elif "VH = " in line:
                    if tech == "MOSFET_16nm_LP":
                        temp_config.write("VH = " + str(1.08) + "\n")
                    else:
                        temp_config.write("VH = " + str(0.84) + "\n")
                else:
                    temp_config.write(line)
            temp_config.close()
            os.system("python main.py -func pass -conf temp_config.py -plot 1")
