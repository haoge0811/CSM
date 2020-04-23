'''
this function reads the .out of hspice simulation, and extract the 
waveform data of outputs we need to calculate similarity of spice
result and CSM result
'''
def data_trim_ref(sp_out_path, sp_wv_path):
    # trim data
    infile_spice = open(sp_out_path, 'r')
    outfile_spice = open(sp_wv_path, 'w')
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
