# author: Eda Yan <yidayan@usc.edu>

def float2string(s):
    ss = str(s)
    if ss[-3:] == 'e-3':
        ss = ss.replace('e-3', 'm')
    elif ss[-3:] == 'e-4':
        ss = ss.replace('e-4','')
        ss = str(float(ss) * 100)+'u'
    elif ss[-3:] == 'e-5':
        ss = ss.replace('e-5','')
        ss = str(float(ss) * 10)+'u'
    elif ss[-3:] == 'e-6':
        ss = ss.replace('e-6', 'u')
    elif ss[-3:] == 'e-7':
        ss = ss.replace('e-7','')
        ss = str(float(ss) * 100)+'n'
    elif ss[-3:] == 'e-8':
        ss = ss.replace('e-8','')
        ss = str(float(ss) * 10)+'n'
    elif ss[-3:] == 'e-9':
        ss = ss.replace('e-9', 'n')
    elif ss[-4:] == 'e-10':
        ss = ss.replace('e-10','')
        ss = str(float(ss) * 100)+'p'
    elif ss[-4:] == 'e-11':
        ss = ss.replace('e-11','')
        ss = str(float(ss) * 10)+'p'
    elif ss[-4:] == 'e-12':
        ss = ss.replace('e-12', 'p')
    elif ss[-4:] == 'e-13':
        ss = ss.replace('e-13','')
        ss = str(float(ss) * 100)+'f'
    elif ss[-4:] == 'e-14':
        ss = ss.replace('e-14','')
        ss = str(float(ss) * 10)+'f'
    elif ss[-4:] == 'e-15':
        ss = ss.replace('e-15', 'f')
    elif ss[-4:] == 'e-16':
        ss = ss.replace('e-16','')
        ss = str(float(ss) * 100)+'a'
    elif ss[-4:] == 'e-17':
        ss = ss.replace('e-17','')
        ss = str(float(ss) * 10)+'a'
    elif ss[-4:] == 'e-18':
        ss = ss.replace('e-18', 'a')
    return ss
	
	
class Signal:
    time = 0

    # set default as None is user do not input
    def __init__(self, mode, infile=None, param=None, constant=0):
        self.mode = mode
        self.param = param
        self.constant = constant

        # if user inputed infile name, then read up infile ot be an array
        if (infile != None):
            # open and read up csm input file as an object, later we can just query it
            input_file = open(infile, "r")

            # TODO: the structure of input array should allow interpolation when being queried
            # so that the input file time step does not have to match the simulation time step
            # input file can just be a piece wise linear source.
            # for now let just assume it's the same time step

            # empty array
            time_array = []
            v_in_array = []

            for a_line in input_file:
                # input file use # as comment sign
                if (a_line[0] != "#"):
                    a_line = a_line.split()
                    a_line = [float(t) for t in a_line]

                    time_array.append(a_line[0])
                    # look at the last column, as we put Vout of previous gate there
                    # previous Vout becomes v_in here
                    v_in_array.append(a_line[-1])

            # combine to be complete input array
            # time array is stored for later interpolation purpose

            self.input_array = [time_array, v_in_array]
            input_file.close()

        else:
            self.input_array = None

    def get_val(self, t):
        if self.mode == "ramp_lh":
            # 0 to vdd ramp, start at time t_0, rise finish at time config.T_DR_TRAN
            if t < self.param["t_0"]:
                sig = 0
            elif t < (self.param["t_0"] + self.param["t_lh"]):
                # linear up ramp
                sig = self.param["vdd"] * (t - self.param["t_0"]) / self.param["t_lh"]
            else:
                sig = self.param["vdd"]
            return sig
        elif self.mode == "ramp_hl":
            if t < self.param["t_0"]:
                sig = self.param["vdd"]
            elif t < (self.param["t_0"] + self.param["t_lh"]):
                sig = self.param["vdd"] * (1 - (t - self.param["t_0"]) / self.param["t_lh"])
            else:
                sig = 0
            return sig
        elif self.mode == "from_file":
            t_step = 0.01e-12  # should be the t_step of input file

            index = int(np.round(t / t_step, 3))

            sig = self.input_array[1][index]
            return sig

        elif self.mode == "constant":
            sig = self.constant
            return sig

def generate_from_template(template_directory, output_directory, replace):
    infile  = open(template_directory, "r")
    outfile = open(output_directory, "w", buffering=0)

    for line in infile:
        if "$$" in line:      # if this line is to be replaced
            for k in replace:    # if an item is listed in input dictionary
                if k in line: # then replace it with the dictionary value
                    line = line.replace(k, str(replace[k]))
        if ".subckt" in line:
            line = line.replace(' n1 ', ' ')
        outfile.write(line)

    infile.close()
    outfile.close()


def print_header():
    print " ______       ______       __       ___"
    print "/$$$$$$\      $$$$$$\      $$\      $$ |" 
    print "|$$$$$$$\    $$  __$$\     $$$\    $$$ |" 
    print "|$$/  \_|    $$ /  \__|    $$$$\  $$$$ |"
    print "|$$|         \$$$$$$\      $$\$$\$$ $$ |"
    print "|$$|          \____$$\     $$ \$$$  $$ |"
    print "|$$|  $$\    $$\   $$ |    $$ |\$  /$$ |"
    print "\$$$$$$ |    \$$$$$$  |    $$ | \_/ $$ |"
    print " \_____/     \______/     \__|     \__|"

