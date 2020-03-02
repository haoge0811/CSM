import matplotlib.pyplot as plt
import glob

# list the file to be ploted here, then go to bottom to plot to your liking.
# can use wildcard here e.g. *NAND2* glob is used to expand wiildcard
to_be_plotted = ["voltage_save.csv","spice.txt"]


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
# below is just an example of plotting, you can plot however you like.
# all_file_data_dict["file_name"] has it's data avaliable in dict format

# CSM
CSM_file_name = to_be_plotted[0]
CSM_signal_to_be_plotted = ["N22","N23"]
for a_signal in CSM_signal_to_be_plotted:
    plt.plot("time",a_signal, data=all_file_data_dict[CSM_file_name],label="CSM_"+a_signal)

# spice
spice_file_name = to_be_plotted[1]
spice_signal_to_be_plotted = ["N22","N23"]
for a_signal in spice_signal_to_be_plotted:
    plt.plot("time",a_signal, data=all_file_data_dict[spice_file_name],label="spice_"+a_signal)


plt.legend()
plt.show()