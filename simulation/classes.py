# Author: haoge <haoge@usc.edu> at USC SPORT Lab

from func_csm import *
import re 
import pdb
import numpy as np
import itertools


# def _print_dict_csm(r, gate="INV"):
    # {'I_out_DC': 9.5782e-06, 'CI': 3.0417e-17, 'CO': -1.2112465e-17, 'CM': 3.003316e-17}
    # if gate == "INV":
        # print "I_out_DC={:.4e} \t CI={:.4e} \t CO={:0.4e} \t CM={:.4e}".format(r["I_out_DC"], r["CI"], r["CO"], r["CM"])

def _trick_char_gate(temp, path):

    data = dict()
    data["dim_idx"] = dict()
    data["lut"] = temp["LUT"]

    if "_INV_" in path:
        dim_name = ["Vin", "Vout"]
        data["low"] = [0] * 2
        data["high"] = [0] * 2
        data["step"] = [0] * 2
        data["idx_dim"] = [0] * 2
    elif ("_NAND2_" in path) or ("_NOR2_" in path):
        dim_name = ["Vna", "Vnb", "Vn1", "Vout"]
        data["low"] = [0] * 4
        data["high"] = [0] * 4
        data["step"] = [0] * 4
        data["idx_dim"] = [0] * 4
    for i, name in enumerate(dim_name):
        data["low"][i] = temp["V_L"]
        data["high"][i] = temp["V_H"]
        data["step"][i] = temp["VSTEP"]
        data["dim_idx"][name] = i
        data["idx_dim"][i] = name

    return data


class LUT:
    def __init__(self, path):
        self.load(path)
        self.dim = len(self.dim_idx)


    def load(self, path):
        # TODO: params should not be based on the name. 
        """Loads a saved LUT (by characterization) from pickle files
        
        arguments: 
        path:   the LUT filename includes info of all the hyper-parameters, 
        
        assignments: 
        lut:    dict of np.ndarray of different params
        low:    dict of low values of each parameter lut
        high    dict of high values of each paramter lut
        step:   dict of the steps for each parameter
        dim_idx:    dict ??? 

        note: currently only supporting uniform characterization
        thus only one step is being reported for each parameter
        """
        
        print ">] Loading LUT from " + path 
        
        ###############################
        # Here is a trick until Hao gives me the new pickle files
        # data = pickle.load(open(path, 'r'))
        temp = load_LUT(path)
        data = _trick_char_gate(temp, path)
        ###############################

        self.lut = data["lut"]
        self.low = data["low"]
        self.high = data["high"]
        self.step = data["step"]
        self.dim_idx = data["dim_idx"]
        self.idx_dim = data["idx_dim"]

        print "\tLUT loaded with keys: " + str(self.lut.keys())
    

    def get_val(self, val, params=None, debug=False):
        """ returns the value of list of params at values val
        based on interpolation on LUTs
        curretnly only supprts interpolation, not extrapolation
        code is dimension number independent. 

        arguments:
        val:    values of each dimention of the LUT, ordered list
        params: what parameters are required, all if None,

        returns:
        res:    dict of params with calculated values
        """

        params = self.lut.keys() if params == None else params

        for idx, v in enumerate(val):
            assert ((v >= self.low[idx]) or (v <= self.high[idx])), "out of bound"

        indices, slope = self.get_hypercube(val)

        if debug:
            print "\nInterpolation\n"
            print "Values:\n", val, "\n"
            print "IDX:\n", indices, "\n"
            print "Slope: \n", slope, "\n"
            Iout = self.lut["I_out_DC"]
            p00 = Iout[indices[0][0], indices[1][0]]
            p01 = Iout[indices[0][1], indices[1][0]]
            p10 = Iout[indices[0][0], indices[1][1]]
            p11 = Iout[indices[0][1], indices[1][1]]

            a_vi = slope[0]
            a_vo = slope[1]
            for p in p00, p01, p10, p11:
                print p

            print "\n\n"
            #pdb.set_trace()

        _slope = np.array([[1-x for x in slope], slope]).T

        _slope = _slope.tolist()
        #_slope = np.round(slope, 3).tolist()
        indices = indices.tolist()
        slope_expand = np.array(list(itertools.product(*_slope)))
        slope_coef = np.prod(slope_expand, axis=1)
        res = dict()

        for param in self.lut.keys():
            if param == "header_info":
                continue
            dd = self.lut[param]
            # print param
            # print dd
            # print "indices:" , indices
            mat_expand = np.array([dd[x] for x in list(itertools.product(*indices))])
            res[param] = np.sum(slope_coef* mat_expand)
        
        if debug:
            print "\n", slope, "\n"
            print "\n", slope_expand
            print "\n", slope_coef
            #pdb.set_trace()

        return(res)

    def get_hypercube(self, val):
        ''' notes here TODO:
        slope is ratio from lower bound
        '''

        idx_low = [0] * self.dim
        idx_high = [0] * self.dim
        val_low = [0] * self.dim
        val_high = [0] * self.dim
        slope = [0] * self.dim
        mat_idx = np.zeros((self.dim, 2), dtype=np.uint16)
        for dim, v in enumerate(val):
            idx_low[dim] = int(np.floor((val[dim] - self.low[dim]) / self.step[dim]))
            idx_high[dim] = int(np.ceil((val[dim] - self.low[dim]) / self.step[dim]))
            val_low[dim] = (idx_low[dim] * self.step[dim]) + self.low[dim]
            val_high[dim] = (idx_high[dim] * self.step[dim]) + self.low[dim]
            mat_idx[dim, 0] = idx_low[dim]
            mat_idx[dim, 1] = idx_high[dim] 
            slope[dim] = (val[dim] - val_low[dim]) / self.step[dim]
            #slope[dim] = np.round((val[dim] - val_low[dim]) / self.step[dim], 3)
        return mat_idx, slope


class net:
    def __init__(self, name, initial_voltage, extra_cap_load = 0):
        self.name = name

        self.voltage = initial_voltage
        # a net has a single driver, and potentially multiple load. this value records the capacitance load that is due
        # to the input cap of next stage (i.e. gates being driven by this net). If multiple gates being driven, this
        # value is their input cap combined.
        self.voltage_just_now = initial_voltage# change of voltage between the currently stored voltage and last value
        self.cap_load_dict = dict() # an empty dict, to store cap due to different gate load
        self.extra_cap_load = extra_cap_load

        # now i want the cap_load value to be updated by the gates that is being driven by this net.
        # e.g. when ever a gate is simulated, it does its thing, and update the cap_load value of its input net.
        self.level = None # reserve a space here

    def sum_CL(self):
        CL = 0
        for each_gate in self.cap_load_dict.keys(): # if dict empty, this is skipped
            CL += self.cap_load_dict[each_gate]  # read and accumulate all cap on this net
        CL += self.extra_cap_load
        return CL

    def update_voltage(self,new_voltage):
        self.voltage_just_now = self.voltage
        self.voltage = new_voltage


    #def save_voltage(self, time_now, file_or_list_to_save):
        # save self.voltage along side time_now in file_or_list_to_save





class Gate: # TODO: Saeed add doc for this as an example to Eda 
    def __init__(self, name, lut, n_out):
        '''
        since there could be 1 or more input net depending on logic gate type,
        construction of input is going to be in logic gate specific class
        there can be 3 status for event driven purpose.
        "active":      everything active, working as normal
        "stabilising": all input nets has stabled, waiting on output net to settle. technically internal net will
                also need to be checked. however it's not straight forward to implement. hence, not included
        "sleep":       not active. simulation is simply skipped. output net voltage will naturally not change.
        '''
        self.name = name
        self.n_out = n_out # this can convinently be net instance, and can be changed later within object
        self.lut = lut
        self.status = "active"
        self.level = None 

    # def simulate(self, t_step, just_update_CI=False):
        # raise NotImplementedError

    # def update_level(self):
        # raise NotImplementedError
   
    # def check_status(self, t_step, settle_th):
        # raise NotImplementedError



class INV(Gate):
    def __init__(self, name, lut, n_out, n_in):
        '''
        arguments
        n_in:   input node 
        n_out:  output node
        lut:    CSM look up table
        name:   name/id of this gate in the ckt/netlist
        '''
        Gate.__init__(self, name, lut, n_out) 
        self.n_in = n_in

        # added for event driven
        # its going to be initial voltage anyway.
        self.input_net_last_active_voltage = n_in.voltage 

    def simulate(self, t_step, just_update_CI = False): 
        ''' csm simulation of gate for 1 time step
        standing at time "now", given Vin_next, find Vout_next
        '''
        # step 1, get next value from input net object.
        Vin_next = self.n_in.voltage   # since Vin net has already been updated by last simulation of previous gate
        Vin = self.n_in.voltage_just_now # intput net voltage now is actually Vin_next for this gate.
        d_Vin = Vin_next - Vin

        # step 2 get output node information
        # output external load of this gate, i.e. input cap of output gates
        Vout = self.n_out.voltage
        CL = self.n_out.sum_CL()

        # step 3, apply csm step simulation
        r = self.lut.get_val([Vin, Vout])
 
        if not just_update_CI: # if True then skip the diff eq solving, and voltage updating part
            d_Vout = (r["CM"] * d_Vin - r["I_out_DC"] * t_step) / (CL + r["CO"] + r["CM"])

            # step 4, update output net object voltage value
            self.n_out.update_voltage(Vout + d_Vout) 
        else:
            d_Vout = -1

        # update input net for cap value change.
        self.n_in.cap_load_dict[self.name] = r["CI"]
        # below is for debugging
        # print "{:.4f} \t {:.4f} \t {:.4f} \t {:.4f} \t {:.4f}".format(Vin, Vin_next, d_Vin, Vout, d_Vout)
        # if Vout > 0.67 :
            # _print_dict_csm(r, "INV")
            # print "CM * d_Vin  = {:.5e}".format(r["CM"] * d_Vin)
            # print "Io * t_step = {:.5e}".format(r["I_out_DC"] * t_step)
            # print "\n"
            # if d_Vout < 0.001:
                # val = [Vin, Vout]
                # self.lut.get_val(val, debug=True)
                # pdb.set_trace()


    def update_level(self): # returns a boolean, if out net level is updated.
        new_level = self.n_in.level + 1
        if self.n_out.level != new_level:
            gate_level_updated = True
        else:
            gate_level_updated = False
        self.n_out.level = new_level
        return gate_level_updated

    def check_status(self, t_step, settle_th): # check and set the status of this gate.
        d_Vin_slope = abs((self.n_in.voltage - self.input_net_last_active_voltage)/t_step)
        d_Vout_slope = abs((self.n_out.voltage - self.n_out.voltage_just_now)/t_step)

        if (d_Vin_slope > settle_th): # input not settled
            self.status = "active"
            self.input_net_last_active_voltage = self.n_in.voltage # update last active voltage
        elif (d_Vout_slope > settle_th): # input settled, but waiting on output to settle
            self.status = "stabilising"
        else: # all settled, let's sleep
            self.status = "sleep"
        # TODO: a bug is, the point input is considered to be settled, the voltage at that point need to be rememberd and
        # compared against. otherwise, if input ramp-up slowly, the gate will never wake up.


class NAND2(Gate):
    def __init__(self, name, lut, n_out, n_in1, n_in2, n_int_v=0):

        ''' arguments
        n_int_V:    initial voltage of internal node 
        '''
        Gate.__init__(self, name, lut, n_out) 
        self.n_in1 = n_in1
        self.n_in2 = n_in2
        self.n_int_v = n_int_v # 

        # for event driven
        self.n_in1_last_active_voltage = n_in1.voltage # its going to be initial voltage anyway.
        self.n_in2_last_active_voltage = n_in2.voltage


    def simulate(self, t_step, just_update_CI = False):

        # step 1, get next value from input net object.
        Vna_next = self.n_in1.voltage   # since Vin net has already been updated by last simulation of previous gate
        Vna = self.n_in1.voltage_just_now # intput net voltage now is actually Vin_next for this gate.
        d_Vna = Vna_next - Vna
        Vnb_next = self.n_in2.voltage   # since Vin net has already been updated by last simulation of previous gate
        Vnb = self.n_in2.voltage_just_now # intput net voltage now is actually Vin_next for this gate.
        d_Vnb = Vnb_next - Vnb

        # step 2 get output node information
        Vout = self.n_out.voltage
        CL = self.n_out.sum_CL()

        # get internal node voltage also
        Vn1 = self.n_int_v
        # print self.name
        # print "{:.4f} \t {:.4f} \t {:.4f} \t {:.4f} \t {:.4f} \t {:.4f}".format(Vna, Vna_next, Vnb, Vnb_next, Vn1, Vout)
        # step 3, apply csm step simulation
        r = self.lut.get_val([Vna, Vnb, Vn1, Vout])

        if not just_update_CI:  
            # if True then skip the diff eq solving, and voltage updating part
            # the actual diffrential equation for circuit simulation, plus minus sign checked.
            d_Vout = (r["CM_A"] * d_Vna + r["CM_B"] * d_Vnb - r["I_out_DC"] * t_step) / (
                    CL + r["CO"] + r["CM_A"] + r["CM_B"])

            d_Vn1 = ((-r["I_inter_DC"]) * t_step) / r["CINT"]

            # step 4, update output-net-object voltage value
            self.n_out.update_voltage(Vout + d_Vout) # update output net voltage value
            self.n_int_v = Vn1 + d_Vn1

        # also remember to update input net for cap value change.
        self.n_in1.cap_load_dict[self.name] = r["CI_A"]
        self.n_in2.cap_load_dict[self.name] = r["CI_B"]
        # if self.name == "NAND2_5":
            # print "{:.4f} \t {:.4f} \t {:.4f} \t {:.4f} \t {:.4f} \t {:.4f} \t {:.4f} \t {:.4f}".format(Vna, Vna_next, Vnb, Vnb_next, Vn1, d_Vn1, Vout, d_Vout)
            # pdb.set_trace()

    def update_level(self): # returns a boolean, if output net level is updated.
        new_level = max(self.n_in1.level, self.n_in2.level) + 1 # take max of input A and B, then + 1
        if self.n_out.level != new_level:
            gate_level_updated = True
        else:
            gate_level_updated = False
        self.n_out.level = new_level
        return gate_level_updated


    # only difference to INV is, it now checks 2 input nodes
    def check_status(self, t_step, settle_th): # check and set the status of this gate.
        d_Vna_slope = abs((self.n_in1.voltage - self.n_in1_last_active_voltage)/t_step)
        d_Vnb_slope = abs((self.n_in2.voltage - self.n_in2_last_active_voltage)/t_step)
        d_Vout_slope = abs((self.n_out.voltage - self.n_out.voltage_just_now)/t_step)

        if (d_Vna_slope > settle_th) or (d_Vnb_slope > settle_th): # input not settled
            self.status = "active"
            self.n_in1_last_active_voltage = self.n_in1.voltage  # update last active voltage
            self.n_in2_last_active_voltage = self.n_in2.voltage
        elif (d_Vout_slope > settle_th): # input settled, but waiting on output to settle
            self.status = "stabilising"
        else: # all settled, let's sleep
            self.status = "sleep"
        # print self.name, "\t", self.status

class NOR2(NAND2):
    # they have no difference in this simulation procedure
    # when creating gate instances, different lut will be given to them, hence defineing their charactrstic
    pass


class Circuit:

    def __init__(self, verilog_path, config=None):
        self.config = config
        self.verilog_path = verilog_path

    def read_netlist(self):
        # open verilog netlist to read
        print "reading netlist file: ", self.verilog_path
        netlist_file = open(self.verilog_path, "r")
        
        self.nets_dict = dict()
        self.gates_dict = dict()

        # TODO: no idea what we are doing here, @Hao please check
        # It seems we are just trying to know what LUT to load
        #presence_detection and LUT loading TODO: could do this section in a more tidy way
        LUT_name_front = self.config.LUT_bin_dir + self.config.TECH
        LUT_name_back = "VL" + str(self.config.VL) + "_VH" + str(self.config.VH) + "_VSTEP" + \
                str(self.config.VSTEP) + "_P" + str(self.config.PROCESS_VARIATION) + "_V" \
                + str(self.config.VDD) + "_T" + str(self.config.TEMPERATURE) + ".lut"

        presence_detection = dict()
        sensitive_names = ["inv", "nand", "nor"]
        for a_name in sensitive_names:
            presence_detection[a_name] = False
        for line in netlist_file:
            for a_name in sensitive_names:
                if a_name in line:
                    presence_detection[a_name] = True
        netlist_file.seek(0) # reset input file position cursor
        
        if presence_detection["inv"]:
            _path = LUT_name_front + "_INV_" + LUT_name_back
            _INV_LUT = LUT(_path)

        if presence_detection["nand"]:
            _path = LUT_name_front + "_NAND2_" + LUT_name_back
            _NAND2_LUT = LUT(_path)

        if presence_detection["nor"]:
            _path = LUT_name_front + "_NOR2_" + LUT_name_back
            _NOR2_LUT = LUT(_path)
        
        # TODO @Hao: please look at the sample code below and change the code
        # _path = NAND2_LUT = LUT_name_front + "_NAND2_" + LUT_name_back
        # nand2 = LUT(_path)
        # mat_idx, slope = nand2.get_hypercube([0.22, 0.313, 0.04, 0.543])
        # nand2.get_val([0.22, 0.313, 0.04, 0.543])

        # TODO: above object creation is only testing verion. it can not read nets if it's in multiple line in verilog.
        #       --Fixed by Eda
        # TODO: it cannot function correctly if gate is defined before net. don't know if it's allowed in verilog.
        # TODO: it cannot detect nand2 from nand3, and only work for nand2 at this point
        in_flag = 0
        out_flag = 0
        wire_flag = 0
        self.int_nodes = []
        for line in netlist_file:
            # step 1, create all net instances
            if re.search('input', line[:6], re.IGNORECASE) or in_flag == 1:
                in_flag = 1
                if ';' in line:
                    in_flag = 0
                line = re.split('\W+', line) # extract all words from line
                if line[0] == 'input':
                    self.in_nodes = line[1:-1] # primary input list for first line
                else:
                    self.in_nodes = self.in_nodes + line # primary input list for other lines
            elif re.search('output', line[:6], re.IGNORECASE) or out_flag == 1:
                out_flag = 1
                if ';' in line:
                    out_flag = 0
                line = re.split('\W+', line) # extract all words from line
                if line[0] == 'output':
                    self.out_nodes = line[1:-1]
                else:
                    self.out_nodes = self.out_nodes + line
            elif re.search('wire', line[:6], re.IGNORECASE) or wire_flag == 1:
                wire_flag = 1
                if ';' in line:
                    wire_flag = 0
                line = re.split('\W+', line) # extract all words from line
                if line[0] == 'wire':
                    self.int_nodes = line[1:-1]
                else:
                    self.int_nodes = self.int_nodes + line

        for each_net_name in self.in_nodes:
            self.nets_dict[each_net_name] = net(name=each_net_name, initial_voltage=0)
        for each_net_name in self.out_nodes:
            self.nets_dict[each_net_name] = net(name=each_net_name, initial_voltage=0)
        if len(self.int_nodes) > 0:
            for each_net_name in self.int_nodes:
                self.nets_dict[each_net_name] = net(name=each_net_name, initial_voltage=0)

        netlist_file.seek(0) #reread file for gate instances
        for line in netlist_file:
            # step 2, create all logic gates instances, pass net instance to gates, according to netlist
            if "not" in line:
                line = re.split('\W+', line) # extract all words from line
                line = line[1:-1]
                # 0 name, 1 output, 2 input
                gate_name = line[0]
                n_out_name = line[1]
                n_in_name = line[2]
                # note: output net and input net instance are passed in as argument here
                self.gates_dict[gate_name] = INV(name=gate_name, lut=_INV_LUT,
                                              n_out=self.nets_dict[n_out_name],
                                              n_in=self.nets_dict[n_in_name])

            elif "nand" in line:
                line = re.split('\W+', line) # extract all words from line
                line = line[1:-1]
                # 0 name, 1 output, 2 in_A, 3 in_B
                gate_name = line[0]
                n_out_name = line[1]
                n_in1_name = line[2]
                n_in2_name = line[3]
                # note: output net and input net instance are passed in as argument here
                self.gates_dict[gate_name] = NAND2(name=gate_name, lut=_NAND2_LUT,
                                              n_out=self.nets_dict[n_out_name],
                                              n_in1=self.nets_dict[n_in1_name] ,
                                              n_in2=self.nets_dict[n_in2_name])

            elif "nor" in line:
                line = re.split('\W+', line) # extract all words from line
                line = line[1:-1]
                # 0 name, 1 output, 2 in_A, 3 in_B
                gate_name  = line[0]
                n_out_name = line[1]
                n_in1_name = line[2]
                n_in2_name = line[3]
                # note: output net and input net instance are passed in as argument here
                self.gates_dict[gate_name] = NOR2(name=gate_name, lut=_NOR2_LUT,
                                              n_out=self.nets_dict[n_out_name],
                                              n_in1=self.nets_dict[n_in1_name] ,
                                              n_in2=self.nets_dict[n_in2_name])

    def attach_LUTs(self): 
        pass

    
    def levelize(self):
        # TODO: @Hao just check if its working good here later

        for each_net in self.in_nodes: # primary input list
            self.nets_dict[each_net].level = 0 # set to 0
        # TODO URGENT: @Hao, what is this int_nodes
        # TODO: Saeed 2 @Hao: I guess just the internal nodes level init is enough?
        for each_net in (self.int_nodes + self.out_nodes): # all other nodes
            self.nets_dict[each_net].level = 1 # initialize to 1
    
        while True:
            circuit_level_updated = False  # initialize to false
            for each_gate in self.gates_dict.keys():
                level_updated = self.gates_dict[each_gate].update_level()
                if level_updated:
                    circuit_level_updated = True

            # at the end of all gate iteration, check if the circuit level has been updated
            # no gate updated output net level > levlization is done
            if circuit_level_updated == False:
                break
        
        # levelization ends but needs to be recorded (?)
        # iterate through all gate again to get max level,
        # # and record all gate record all gate level according to their output net level
        # I choose to do this in th end hope to reduce comparison brough by max level recording in previous iterations.
        circuit_max_level = 1 # should at least be 1
        for each_gate in self.gates_dict.keys():
            n_out_lvl = self.gates_dict[each_gate].n_out.level
            # I choose to define a gate's level as its output net's level
            self.gates_dict[each_gate].level = n_out_lvl
            if n_out_lvl > circuit_max_level:
                circuit_max_level = n_out_lvl # record max level

        # iterate though all gate again to put their name to corresponding level list
        #create an empty list with max_level+1 slots, so we can put PI in this list as well
        level_list = [[] for i in range(circuit_max_level+1)]

        level_list[0] = self.in_nodes # put PI in level 0
        for each_gate in self.gates_dict.keys():
            this_gate_level = self.gates_dict[each_gate].level
            level_list[this_gate_level].append(self.gates_dict[each_gate].name) 
        # levelization recording end
        self.level_list = level_list


    def set_caps(self):

        # TODO: this is just initializing a value for CL of each gate ...
        # ... to not have zero value. This can be changed to Cout of itself.  
        # below is GOLD, pre-simulate Cin loaing iteration
        # run all gates at 0 time just to get cap_load value on nets populated.
        for each_gate in self.gates_dict.keys():
            self.gates_dict[each_gate].simulate(t_step = None, just_update_CI=True)
            
        # LOAD CAP of PRIMARY OUTPUTs 
        if (self.config.load_all_PO == True):
            final_output_load = dict()
            for each_net in self.out_nodes:
                final_output_load[each_net] = self.config.cap_value
        else:
            final_output_load = self.config.final_output_load
    
        # TODO: does not seem to work. ...
        # ... add cap load to all output nets, this fix the problem for CSM simulator not stable
        for each_net in self.out_nodes:
            #nets_dict[each_net].extra_cap_load = 1e-16
            self.nets_dict[each_net].extra_cap_load = final_output_load[each_net]


    def init_ckt(self):
        # TODO: first check if levelization is done
        # TODO: think about removing this signal later from here:
        PI_signal_dict = self.config.PI_signal_dict
        t_step = self.config.T_STEP

        print "finding initial conditions..."
        initial_voltage_settle_th = self.config.initial_voltage_settle_th
        # print(initial_voltage_settle_th, t_step)
        all_nets_settled = False
        while (all_nets_settled == False):
            all_nets_settled = True
            for level in range(len(self.level_list)):  # simulate circuit level by level 
                if level == 0:  # Primary inputs
                    for each_PI in self.level_list[level]:
                        self.nets_dict[each_PI].update_voltage(PI_signal_dict[each_PI].get_val(0))  
                else:
                    for each_gate in self.level_list[level]:
                        self.gates_dict[each_gate].simulate(t_step) 
                        # simulate the gate for this time step

            # TODO: this may not be the best orgnization todo this, check later
            # after simulation, check if all nets besides PI have settled
            for each_net in (self.int_nodes + self.out_nodes):
                dV_of_this_net = self.nets_dict[each_net].voltage - self.nets_dict[each_net].voltage_just_now
                slope = abs(dV_of_this_net/t_step)
                if (slope > initial_voltage_settle_th):
                    all_nets_settled = False
            #print all_nets_settled

        print "initial conditions:"
        for each_net in (self.int_nodes + self.out_nodes):
            print "{}: {:.4f}".format(each_net, self.nets_dict[each_net].voltage) 
            # each_net +": " + str(self.nets_dict[each_net].voltage)

    
    def simulate_step(self, t):
        t_step = self.config.T_STEP
        signal = self.config.PI_signal_dict
        init_vth = self.config.initial_voltage_settle_th
        # print "t = ", t
        # TODO: why not iterate over levels themselves? 
        for level in range(len(self.level_list)): # simulate ckt level by level
            
            if level == 0: # PIs
                for each_PI in self.level_list[level]:
                    self.nets_dict[each_PI].update_voltage(signal[each_PI].get_val(t))
            else: 
                for each_gate in self.level_list[level]:
                    # event driven logic exist 
                    # -- 1. here 
                    # -- 2. in "logic_gate" class, "status" attribute.
                    # 3. check_status function in each logic gate sub class.
                    # 4. input_net_last_active_voltage attribute in each logic gate sub class.

                    # this function check and set status of logic gates appropriatly
                    # re-using voltage settle th. from initial voltage finding here. 
                    # they very well could be the same, and defined in config file
                    self.gates_dict[each_gate].check_status(t_step, init_vth)
                    if (self.gates_dict[each_gate].status == "active") or (self.gates_dict[each_gate].status == "stabilising"):
                        # simulate as usual
                        self.gates_dict[each_gate].simulate(t_step)
                    
                    # else just skip the simulation
                    # we can print out status of each gate at given time for debugging.
                    # print each_gate + " " + gates_dict[each_gate].status

                    # if event_driven is turned off as global setting:
                    # gates_dict[each_gate].simulate(t_step)


    def simulate_signal(self):
        t_tot = self.config.T_TOT
        t_step = self.config.T_STEP
        signal = self.config.PI_signal_dict

        save_file = open(self.config.save_file_path, "w")
        save_file.write("# time")
        for each_net in self.config.voltage_nodes_to_save:
            save_file.write(" " + each_net)
        save_file.write("\n")

        print "simulating..."
        for step_number in range(int(np.ceil(t_tot / t_step))):
            t = step_number * t_step
            # t_ps = t * 1e12  # just for readability
            # print "t = ", t
            self.simulate_step(t)
            
            # save voltage of chosen nets
            save_file.write(str(t))
            for each_net in self.config.voltage_nodes_to_save:
                save_file.write(","+ str(self.nets_dict[each_net].voltage))
            save_file.write("\n")

        save_file.close()


    def info(self):
        print self.ckt_name


