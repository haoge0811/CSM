# Author: haoge <haoge@usc.edu> at USC SPORT Lab
import os
import numpy as np
# OrderDict is only for python2. python3 regular dict is already ordered.
# it is here to make read_spice function output easier to read
from collections import OrderedDict

# just a file modifier
def generate_from_template(template_directory, output_directory, replace):
    infile  = open(template_directory, "r")
    outfile = open(output_directory, "w", buffering=0)

    for line in infile:
        if "$$" in line:      # if this line is to be replaced
            for k in replace:    # if an item is listed in input dictionary
                if k in line: # then replace it with the dictionary value
                    line = line.replace(k, str(replace[k]))
        outfile.write(line)

    infile.close()
    outfile.close()


def sweep_table_generator(GATE_NAME, V_L, V_H, VSTEP, output_directory):
    if (GATE_NAME == "INV"):
        outfile = open(output_directory, "w")
        outfile.write("* sweep  file \n\n")

        #### generate DC sweep data table ####
        outfile.write(".data sweep_DC\n")
        outfile.write("+ code sweep_Vin sweep_Vout \n")

        r = np.linspace(V_L, V_H, int((V_H - V_L) / VSTEP) + 1)
        r = [str(np.round(k, 2)) for k in r]
        code = 1
        for Vin in r:
            for Vout in r:
                outfile.write(str(code) + " " + Vin + " " + Vout + "\n")
                code += 1
        outfile.write(".enddata\n\n")

        #### CM table ########################
        outfile.write(".data sweep_CM\n")
        outfile.write("+ code sweep_Vout \n")

        r = np.linspace(V_L, V_H, int((V_H - V_L) / VSTEP) + 1)
        r = [str(np.round(k, 2)) for k in r]
        code = 1
        for Vout in r:
            outfile.write(str(code) + " " + Vout + "\n")
            code += 1
        outfile.write(".enddata\n\n")

        #### CO table ########################
        outfile.write(".data sweep_CO\n")
        outfile.write("+ code sweep_Vin \n")

        r = np.linspace(V_L, V_H, int((V_H - V_L) / VSTEP) + 1)
        r = [str(np.round(k, 2)) for k in r]
        code = 1
        for Vin in r:
            outfile.write(str(code) + " " + Vin + "\n")
            code += 1
        outfile.write(".enddata\n\n")

        outfile.close()

    elif (GATE_NAME == "NAND2") or (GATE_NAME == "NOR2"):
        outfile = open(output_directory, "w")
        outfile.write("* sweep  file \n\n")

        #### DC table ########################
        outfile.write(".data sweep_DC\n")
        outfile.write("+ code sweep_VA sweep_VB sweep_Vn1 sweep_Vout \n")

        r = np.linspace(V_L, V_H, int((V_H - V_L) / VSTEP) + 1)
        r = [str(np.round(k, 2)) for k in r]
        code = 1
        for VA in r:
            for VB in r:
                for Vn1 in r:
                    for Vout in r:
                        outfile.write(str(code) + " " + VA + " " + VB + " " + Vn1 + " " + Vout + "\n")
                        code += 1
        outfile.write(".enddata\n\n")

        #### CM_A table ########################
        outfile.write(".data sweep_CM_A\n")
        outfile.write("+ code sweep_VB sweep_Vn1 sweep_Vout \n")

        r = np.linspace(V_L, V_H, int((V_H - V_L) / VSTEP) + 1)
        r = [str(np.round(k, 2)) for k in r]
        code = 1
        for VB in r:
            for Vn1 in r:
                for Vout in r:
                    outfile.write(str(code) + " " + VB + " " + Vn1 + " " + Vout + "\n")
                    code += 1
        outfile.write(".enddata\n\n")

        #### CM_B table ########################
        outfile.write(".data sweep_CM_B\n")
        outfile.write("+ code sweep_VA sweep_Vn1 sweep_Vout \n")

        r = np.linspace(V_L, V_H, int((V_H - V_L) / VSTEP) + 1)
        r = [str(np.round(k, 2)) for k in r]
        code = 1
        for VA in r:
            for Vn1 in r:
                for Vout in r:
                    outfile.write(str(code) + " " + VA + " " + Vn1 + " " + Vout + "\n")
                    code += 1
        outfile.write(".enddata\n\n")

        #### CO table ########################
        outfile.write(".data sweep_CO\n")
        outfile.write("+ code sweep_VA sweep_VB sweep_Vn1 \n")

        r = np.linspace(V_L, V_H, int((V_H - V_L) / VSTEP) + 1)
        r = [str(np.round(k, 2)) for k in r]
        code = 1
        for VA in r:
            for VB in r:
                for Vn1 in r:
                    outfile.write(str(code) + " " + VA + " " + VB + " " + Vn1 + "\n")
                    code += 1
        outfile.write(".enddata\n\n")

        #### CINT table ########################
        outfile.write(".data sweep_CINT\n")
        outfile.write("+ code sweep_VA sweep_VB sweep_Vout \n")

        r = np.linspace(V_L, V_H, int((V_H - V_L) / VSTEP) + 1)
        r = [str(np.round(k, 2)) for k in r]
        code = 1
        for VA in r:
            for VB in r:
                for Vout in r:
                    outfile.write(str(code) + " " + VA + " " + VB + " " + Vout + "\n")
                    code += 1
        outfile.write(".enddata\n\n")


        outfile.close()

    else:
        print "Cannot generate sweep table, Invalid or not yet implemented gate name."


# to read from raw spice output, put selected data into array, for later calculation use
# output data array is always the return value
def read_spice(spice_raw_out, DC_mode, spice_extend_res=None, save_processed_out=0,  save_dir=None):
    infile = open(spice_raw_out, "r")
    # to increase the accuracy of charTran, even if we want LUT V_step = 0.1, we would like spice to use voltage step much finer,
    # so that spice result is accurate first of all. then we only store the point that matches V_step = 0.1 step size
    # read pattern is slightly different for DC and Tran, make the code generic to read both
    # DC_mode if set as 1(on), then spice_extend_res will not be used, first few lines of data will also not be skipped

    ############### originally written by justin and haoge #########
    ######################### tidy up by haoge######################

    data_array = OrderedDict()
    # each column is a key in dictionary
    # use this structure to read lines in file, for better control of lines to skip
    while True: # read entire file loop
        line = infile.readline()
        if len(line) == 0:  # End of file
            break # exit read entire file loop

        else:
            if line[0] == 'x':  # data section
                # skip 2 line of blank
                line = infile.readline()
                line = infile.readline()

                # title of values, i.e. the keys of dict
                title = infile.readline()
                title = title.split() # now title is a list of keys

                # print(title) ## testing
                for each_item in title:
                    # print(each_item) ## testing
                    # if an item (or column, or variable) did not exist before, then create empty array to append later,
                    # otherwise, skip this section so data get appended naturally
                    if each_item not in data_array.keys():
                        # print("item did not exist") ## testing
                        data_array[each_item] = [] # create empty array for each item


                if DC_mode == 1: # spice_extend_res not used. regualr read
                    # read on until it hits y line
                    while True:  # data section loop
                        line = infile.readline()
                        if line[0] == 'y':  # End of data section
                            break  # exit data section loop

                        else:  # actual numerical data
                            line = line.split()[1:] # remove the index
                            line = [string2float(t) for t in line] # convert string with SI unit to float
                            # add each value to its corresponding title dict key
                            for each_item in title:
                                data_array[each_item].append( line[title.index(each_item)] )

                else: # "other" mode
                    # initial skips
                    line = infile.readline()  # waste a line to account delay in pulse start
                    if line[0] == 'y':  # End of data section
                        break # exit data section loop

                    # waste more, account for low start value and its spice_extend_res
                    skip_counter = 0
                    while skip_counter != (spice_extend_res):
                        line = infile.readline()  # waste a line
                        skip_counter += 1
                        if line[0] == "y":
                            break
                    if line[0] == "y":
                        break
                    # initial skips ends

                    while True: # data section loop
                        line = infile.readline()
                        if line[0] == 'y':  # End of data section
                            break # exit data section loop

                        else: # actual numerical data
                            # print line # testing
                            # read of need data
                            line = line.split()[1:]  # remove the index
                            line = [string2float(t) for t in line]  # convert string with SI unit to float
                            # add each value to its corresponding title dict key
                            for each_item in title:
                                data_array[each_item].append(line[title.index(each_item)])

                            # waste rest of not needed lines
                            skip_counter = 1
                            while skip_counter != (spice_extend_res):
                                line = infile.readline()  # waste a line
                                skip_counter += 1
                                if line[0] == "y":
                                    break
                            if line[0] == "y":
                                break
    infile.close()

    # save processed output separately according to need
    if save_processed_out == 1:
        outfile = open(save_dir, "w", buffering=0)
        # use the length of the first key item in dict as total number of rows
        number_of_rows = len(data_array[data_array.keys()[0]])
        #print "number of rows " + str(number_of_rows)
        # write title
        for each_key in data_array.keys():
            outfile.write(each_key + "\t\t") # since dict is ordered, title will match data below
        outfile.write("\n")
        # write data
        for a_row in range(number_of_rows):
            for each_key in data_array.keys():
                outfile.write(str(data_array[each_key][a_row]) + "\t")
            outfile.write("\n")

        outfile.close()

    # consider make array multidimensional here?
    # the process is actually gate dependent.
    # so may be not
    return data_array


def string2float(s):
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

# this function is not very generic, it depends on the name and/or position of spice otuput variable
def fill_nd_array(input_data_dict, GATE_NAME, V_L, V_H, VSTEP):
    # fill n-dimensional array according to voltage position.
    number_of_steps = int(np.round((V_H - V_L) / VSTEP, 3)) + 1
    # use the length of the first key item in dict as total number of rows
    number_of_rows = len(input_data_dict[input_data_dict.keys()[0]])
    # print "number of rows " + str(number_of_rows)

    if (GATE_NAME == "INV"):
        # create 2D array
        I_out = np.ndarray((number_of_steps,number_of_steps))
        I_Vin = np.ndarray((number_of_steps,number_of_steps))

        for a_row in range(number_of_rows):
            Vin_idx  = int(np.round(( input_data_dict["in"][a_row]  - V_L)/VSTEP, 3))
            Vout_idx = int(np.round(( input_data_dict["out"][a_row] - V_L)/VSTEP, 3))
            # fill nd array
            I_out[Vin_idx, Vout_idx] = input_data_dict["i_mn"][a_row] + input_data_dict["i_mp"][a_row]
            I_Vin[Vin_idx, Vout_idx] = input_data_dict["i_vin"][a_row]
        out_dict = {"I_out":I_out, "I_Vin":I_Vin}

    elif (GATE_NAME == "NAND2") or (GATE_NAME == "NOR2"):
        # create 4D array
        I_out = np.ndarray((number_of_steps,number_of_steps,number_of_steps,number_of_steps))
        I_Vn1 = np.ndarray((number_of_steps,number_of_steps,number_of_steps,number_of_steps))
        I_Vna = np.ndarray((number_of_steps,number_of_steps,number_of_steps,number_of_steps))
        I_Vnb = np.ndarray((number_of_steps,number_of_steps,number_of_steps,number_of_steps))

        for a_row in range(number_of_rows):
            Vna_idx  = int(np.round(( input_data_dict["na"][a_row]  - V_L)/VSTEP, 3))
            Vnb_idx  = int(np.round(( input_data_dict["nb"][a_row]  - V_L)/VSTEP, 3))
            Vn1_idx  = int(np.round(( input_data_dict["n1"][a_row]  - V_L)/VSTEP, 3))
            Vout_idx = int(np.round(( input_data_dict["out"][a_row] - V_L)/VSTEP, 3))

            # fill nd array
            I_out[Vna_idx, Vnb_idx, Vn1_idx, Vout_idx] = input_data_dict["i_mn"][a_row] + input_data_dict["i_mp"][a_row]
            I_Vn1[Vna_idx, Vnb_idx, Vn1_idx, Vout_idx] = input_data_dict["i_n1"][a_row]
            I_Vna[Vna_idx, Vnb_idx, Vn1_idx, Vout_idx] = input_data_dict["i_vna"][a_row]
            I_Vnb[Vna_idx, Vnb_idx, Vn1_idx, Vout_idx] = input_data_dict["i_vnb"][a_row]
        out_dict = {"I_out":I_out, "I_Vn1":I_Vn1, "I_Vna":I_Vna, "I_Vnb":I_Vnb}

    else:
        print "Cannot fill n-dimensional array, Invalid or not yet implemented gate name."

    return out_dict


# returns output LUT
def calculate_LUT(input_nd_array, GATE_NAME, dv2dt):
    print("Calculating LUT parameters...")
    # pure multidimensional array calculation

    # Note: calculation need to be in this sequence: DC (current source), CM (one or more), CO or CI.
    # CINT just need to be after DC
    if (GATE_NAME == "INV"):
        # calculate DC (current source) parameter
        I_out_DC = input_nd_array["DC"]["I_out"]

        # CM
        # iout_CM reference direction is into the cell
        iout_CM = input_nd_array["CM"]["I_out"]
        CM = (I_out_DC - iout_CM) / dv2dt

        # CO
        iout_CO = input_nd_array["CO"]["I_out"]
        CO = ((iout_CO - I_out_DC) / dv2dt - CM)

        # CI
        # we don't need to subtract DC value, because current source is not connected to input
        iout_Vin = input_nd_array["CM"]["I_Vin"]
        # ref direction of iout_Vin is into Vin
        CI = (-iout_Vin/dv2dt - CM)

        LUT = {"I_out_DC": I_out_DC, "CM": CM, "CO": CO, "CI": CI}

    elif (GATE_NAME == "NAND2") or (GATE_NAME == "NOR2"):
        # calculate DC (current source) parameter
        I_out_DC   = input_nd_array["DC"]["I_out"]
        I_inter_DC = input_nd_array["DC"]["I_Vn1"]
        # I_inter_DC reference direction is into the cell

        # CM_A
        iout_CM_A = input_nd_array["CM_A"]["I_out"]
        CM_A = (I_out_DC - iout_CM_A) / dv2dt

        # CM_B
        iout_CM_B = input_nd_array["CM_B"]["I_out"]
        CM_B = (I_out_DC - iout_CM_B) / dv2dt

        # CO
        iout_CO = input_nd_array["CO"]["I_out"]
        CO = ((iout_CO - I_out_DC)/dv2dt - CM_A - CM_B)

        # CINT (internal)
        iout_CINT = input_nd_array["CINT"]["I_Vn1"]
        CINT =  (iout_CINT - I_inter_DC)/dv2dt

        # CI_A
        iout_Vna = input_nd_array["CM_A"]["I_Vna"]
        CI_A = (-iout_Vna / dv2dt - CM_A)

        # CI_B
        iout_Vnb = input_nd_array["CM_B"]["I_Vnb"]
        CI_B = (-iout_Vnb / dv2dt - CM_B)

        LUT = {"I_out_DC": I_out_DC, "I_inter_DC": I_inter_DC, "CM_A": CM_A, "CM_B": CM_B, "CO": CO, "CINT": CINT,
               "CI_A": CI_A, "CI_B": CI_B}

    else:
        print "Cannot calculate_LUT, Invalid or not yet implemented gate name."

    return LUT


def create_human_readable_LUT(input_LUT, save_dir, GATE_NAME, V_L, V_H, VSTEP):
    number_of_steps = int(np.round((V_H - V_L) / VSTEP, 3)) + 1
    outfile = open(save_dir, "w")

    if (GATE_NAME == "INV"):
        outfile.write("Vin\t\tVout\t\tI_out_DC\t\tCM\t\tCO\t\tCI\t\t\n ")
        for D1 in range(number_of_steps):
            for D2 in range(number_of_steps):
                # write component value according to  output voltages
                Vin  = V_L + D1*VSTEP
                Vout = V_L + D2 * VSTEP
                I_out_DC = input_LUT["I_out_DC"][D1, D2]
                CM       = input_LUT["CM"][D1, D2]
                CO       = input_LUT["CO"][D1, D2]
                CI       = input_LUT["CI"][D1, D2]
                outfile.write(str(Vin)+"\t" +str(Vout)+"\t" \
                    +str(I_out_DC)+"\t" +str(CM)+"\t" +str(CO)+"\t" +str(CI)+"\t\n")

    elif (GATE_NAME == "NAND2") or (GATE_NAME == "NOR2"):
        outfile.write("Vna\t\tVnb\t\tVn1\t\tVout\t\t \
            I_out_DC\t\tI_inter_DC\t\tCM_A\t\tCM_B\t\tCO\t\tCINT\t\tCI_A\t\tCI_B\t\t\n ")
        for D1 in range(number_of_steps):
            for D2 in range(number_of_steps):
                for D3 in range(number_of_steps):
                    for D4 in range(number_of_steps):
                        # write component value according to  output voltages
                        Vna  = V_L + D1*VSTEP
                        Vnb  = V_L + D2 * VSTEP
                        Vn1  = V_L + D3 * VSTEP
                        Vout = V_L + D4 * VSTEP
                        I_out_DC   = input_LUT["I_out_DC"][D1, D2, D3, D4]
                        I_inter_DC = input_LUT["I_inter_DC"][D1, D2, D3, D4]
                        CM_A       = input_LUT["CM_A"][D1, D2, D3, D4]
                        CM_B       = input_LUT["CM_B"][D1, D2, D3, D4]
                        CO         = input_LUT["CO"][D1, D2, D3, D4]
                        CINT       = input_LUT["CINT"][D1, D2, D3, D4]
                        CI_A       = input_LUT["CI_A"][D1, D2, D3, D4]
                        CI_B       = input_LUT["CI_A"][D1, D2, D3, D4]
                        outfile.write(str(Vna)+"\t" +str(Vnb)+"\t" +str(Vn1)+"\t" +str(Vout)+"\t" \
                            +str(I_out_DC)+"\t" +str(I_inter_DC)+"\t" +str(CM_A)+"\t" +str(CM_B)+"\t" +str(CO)+"\t" \
                            +str(CINT)+"\t" +str(CI_A)+"\t" +str(CI_B)+"\t\n")
    else:
        print "Cannot create human readable LUT, Invalid or not yet implemented gate name."
    outfile.close()


def create_dir_if_not_exist(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print("Directory " + directory + " not exist, creating now")