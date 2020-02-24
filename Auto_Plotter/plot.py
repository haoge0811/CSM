import matplotlib.pyplot as plt
import glob


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


def drop_resolution(input_list, drop_factor = 10):
    counter = 0
    output_list = []
    for element in input_list:
        if counter == (drop_factor-1):
            output_list.append(element)
            counter = 0
        else:
            counter += 1
    return output_list


# can use wildcard here e.g. *NAND2* glob is used to expand wiildcard
to_be_plotted = ["voltage_save.csv","spice.txt"]

expanded_plot_list = []
for a_name in to_be_plotted:
    wildcard_expanded_name = glob.glob(a_name) # expand whild card
    expanded_plot_list.extend(wildcard_expanded_name)
# expansion complete
#print expanded_plot_list
all_file_data_dict = dict()
for each_file in expanded_plot_list:
    infile = open(each_file, "r")
    data = dict()
    for line in infile:
        if line[0] == "#": # title line
            title = line[1:].split()
            for each_title in title:
                data[each_title] = [] # create empty list to store data

        else: # data lines
            #print line
            line = line.replace(',', ' ')
            #print line
            line = line.split()
            #print line
            for i in range(len(line)):
                data[title[i]].append(string2float(line[i]))
    infile.close()

    # everything drop resolution, so plot is quicker
    for each_key in data.keys():
        data[each_key] = drop_resolution(data[each_key], drop_factor=200)

    short_file_name = each_file.split("/")[-1]
    all_file_data_dict[short_file_name] = data


# manual plotting part.
# all_file_data_dict["file_name"] has it's data avaliable in dict format

#print all_file_data_dict["spice.txt"].keys()

# CSM
#plt.plot("time","N22", data=all_file_data_dict["voltage_save.csv"],label="CSM_N22")
plt.plot("time","N23", data=all_file_data_dict["voltage_save.csv"],label="CSM_N23")

# spice
#plt.plot("time","N22", data=all_file_data_dict["spice.txt"],label="spice_N22")
plt.plot("time","N23", data=all_file_data_dict["spice.txt"],label="spice_N23")


plt.legend()
plt.show()