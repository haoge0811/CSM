# Author: haoge <haoge@usc.edu> at USC SPORT Lab

from func_csm import *
import re 
import pdb
import numpy as np


class LUT:
    def __init__(path):
        load_LUT(path)
        self.dim = len(self.dim_idx)


    def load_LUT(path):
        # TODO: params should not be based on the name. 
        """Loads a saved LUT (by characterization) from pickle files
        
        arguments: 
        path:   the LUT filename includes info of all the hyper-parameters, 
        
        assignments: 
        lut:    dict of np.ndarray of different params
        low:    dict of low values of each parameter lut
        high    dict of high values of each paramter lut
        step:   dict of the steps for each parameter

        note: currently only supporting uniform characterization
        thus only one step is being reported for each parameter
        """
        print ">] Loading LUT from " + path 
        
        data = pickle.load(open(LUT_dir, 'r'))
        self.lut = data["lut"]
        self.low = data["low"]
        self.high = data["high"]
        self.dim_idx = data["dim_idx"]

        print "\tLUT loaded with keys: " + str(LUT.keys())
        # extract V_L, V_H, VSTEP value from file name
    
    def get_val(points):
        """ returns the value of points for all parameters

        arguments:
        points: dictionary of values of each dimention of LUT
        curretnly only supprts interpolation, not extrapolation
        """
        for v, k in enumerate(points):
            assert v < self.low[k] or v > self.high[k], "out of bound"

        mat = np.zeros((self.dim, 2))



    

    def get_hypercube(val, low, step):
        # since it's low_idx, we should use floor instead of round
        idx_low = int(np.floor((val - low) / step))

        # floored voltage value to closest LUT stored voltage value
        val_low = (idx_low * step) + low

        # deviation factor for interpolation
        a_voltage = ((voltage - voltage_low) / VSTEP)
        return (voltage_low_idx, a_voltage)


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





class logic_gate: # base (or parent) class for all logic gates
    # this is the constructor, that is run at the creation of instance
    def __init__(self, name, LUT_and_boundary, output_net):
        self.name = name
        # since there could be 1 or more input net depending on logic gate type,
        # construction of input is going to be in logic gate specific class
        # self.input_net = input_net
        self.output_net = output_net # this can convinently be net instance, and can be changed later within object
        self.LUT_and_boundary = LUT_and_boundary
        self.status = "active"
        # there can be 3 status for event driven purpose.
        #   "active":      everything active, working as normal
        #   "stabilising": all input nets has stabled, waiting on output net to settle. technically internal net will
        #                  also need to be checked. however it's not straight forward to implement. hence, not included
        #   "sleep":       not active. simulation is simply skipped. output net voltage will naturally not change.
        self.level = None # reserve a space here

class INV(logic_gate):
    def __init__(self, name, LUT_and_boundary, output_net, input_net):
        logic_gate.__init__(self, name, LUT_and_boundary, output_net) # inherite from parent class
        self.input_net = input_net

        # added for event driven
        self.input_net_last_active_voltage = input_net.voltage # its going to be initial voltage anyway.

    # instance function, unique to INV, NAND2, NOR2, since differenct differential equation
    def simulate(self, t_step = None, just_update_CI = False): # it is going to simulate for 1 single time step
        # standing at time "now", given Vin_next, find Vout_next

        # step 1, get next value from input net object.
        Vin_next = self.input_net.voltage   # since Vin net has already been updated by last simulation of previous gate
        Vin = self.input_net.voltage_just_now # intput net voltage now is actually Vin_next for this gate.
        d_Vin = Vin_next - Vin

        # step 2 get output node information
        Vout = self.output_net.voltage
        # output external load of this gate, which is all input cap of gates on output net
        CL = self.output_net.sum_CL()

        # step 3, apply csm step simulation
        # interpolation
        r = read_LUT(LUT_and_boundary=self.LUT_and_boundary,
                     GATE_NAME="INV",
                     voltages_now={"Vin": Vin, "Vout": Vout})

        if just_update_CI == False: # if True then skip the diff eq solving, and voltage updating part
            # the actual diffrential equation for circuit simulation, plus minus sign checked.
            # diff eq for INV
            d_Vout = (r["CM"] * d_Vin - r["I_out_DC"] * t_step) / (CL + r["CO"] + r["CM"])

            # step 4, update output net object voltage value
            Vout_next = Vout + d_Vout  # record and accumulate
            self.output_net.update_voltage(Vout_next) # update output net voltage value

        # also remember to update input net for cap value change.
        self.input_net.cap_load_dict[self.name] = r["CI"]

    def update_level(self): # returns a boolean, if output net level is updated.
        new_level = self.input_net.level + 1
        if self.output_net.level != new_level:
            gate_level_updated = True
        else:
            gate_level_updated = False
        self.output_net.level = new_level
        return gate_level_updated

    def check_status(self, t_step, settle_threshold): # check and set the status of this gate.
        d_Vin_slope = abs((self.input_net.voltage - self.input_net_last_active_voltage)/t_step)
        d_Vout_slope = abs((self.output_net.voltage - self.output_net.voltage_just_now)/t_step)

        if (d_Vin_slope > settle_threshold): # input not settled
            self.status = "active"
            self.input_net_last_active_voltage = self.input_net.voltage # update last active voltage
        elif (d_Vout_slope > settle_threshold): # input settled, but waiting on output to settle
            self.status = "stabilising"
        else: # all settled, let's sleep
            self.status = "sleep"

        # a bug is, the point input is considered to be settled, the voltage at that point need to be rememberd and
        # compared against. otherwise, if input ramp-up slowly, the gate will never wake up.

class NAND2(logic_gate):
    def __init__(self, name, LUT_and_boundary, output_net, input_net_A, input_net_B, internal_node_initial_V=0):
        logic_gate.__init__(self, name, LUT_and_boundary, output_net) # inherite from parent class
        self.input_net_A = input_net_A
        self.input_net_B = input_net_B

        # added for event driven
        self.input_net_A_last_active_voltage = input_net_A.voltage # its going to be initial voltage anyway.
        self.input_net_B_last_active_voltage = input_net_B.voltage

        # special to NAND2 NOR2, it has internal node. This node is currently not visible to top level circuit
        # however, we do need to store it's voltage for simulation
        self.internal_node_voltage = internal_node_initial_V # set initial to 0 by default.

    # instance function, unique to INV, NAND2, NOR2, since differenct differential equation
    def simulate(self, t_step = None, just_update_CI = False): # it is going to simulate for 1 single time step
        # standing at time "now", given Vin_next, find Vout_next

        # step 1, get next value from input net object.
        Vna_next = self.input_net_A.voltage   # since Vin net has already been updated by last simulation of previous gate
        Vna = self.input_net_A.voltage_just_now # intput net voltage now is actually Vin_next for this gate.
        d_Vna = Vna_next - Vna
        Vnb_next = self.input_net_B.voltage   # since Vin net has already been updated by last simulation of previous gate
        Vnb = self.input_net_B.voltage_just_now # intput net voltage now is actually Vin_next for this gate.
        d_Vnb = Vnb_next - Vnb

        # step 2 get output node information
        Vout = self.output_net.voltage
        # output external load of this gate, which is all input cap of gates on output net
        CL = self.output_net.sum_CL()

        # get internal node voltage also
        Vn1 = self.internal_node_voltage

        # step 3, apply csm step simulation
        # interpolation LUT to retrive value
        r = read_LUT(LUT_and_boundary=self.LUT_and_boundary,
                     GATE_NAME="NAND2",
                     voltages_now={"Vna": Vna, "Vnb": Vnb, "Vn1": Vn1, "Vout": Vout})

        if just_update_CI == False:  # if True then skip the diff eq solving, and voltage updating part
            # the actual diffrential equation for circuit simulation, plus minus sign checked.
            # 1
            d_Vout = (r["CM_A"] * d_Vna + r["CM_B"] * d_Vnb - r["I_out_DC"] * t_step) / (
                    CL + r["CO"] + r["CM_A"] + r["CM_B"])
            # 2
            d_Vn1 = ((-r["I_inter_DC"]) * t_step) / r["CINT"]

            # step 4, update output-net-object voltage value
            Vout_next = Vout + d_Vout  # record and accumulate
            Vn1_next = Vn1 + d_Vn1

            self.output_net.update_voltage(Vout_next) # update output net voltage value
            self.internal_node_voltage = Vn1_next

        # also remember to update input net for cap value change.
        self.input_net_A.cap_load_dict[self.name] = r["CI_A"]
        self.input_net_B.cap_load_dict[self.name] = r["CI_B"]

    def update_level(self): # returns a boolean, if output net level is updated.
        new_level = max(self.input_net_A.level, self.input_net_B.level) + 1 # take max of input A and B, then + 1
        if self.output_net.level != new_level:
            gate_level_updated = True
        else:
            gate_level_updated = False
        self.output_net.level = new_level
        return gate_level_updated

    # only difference to INV is, it now checks 2 input nodes
    def check_status(self, t_step, settle_threshold): # check and set the status of this gate.
        d_Vna_slope = abs((self.input_net_A.voltage - self.input_net_A_last_active_voltage)/t_step)
        d_Vnb_slope = abs((self.input_net_B.voltage - self.input_net_B_last_active_voltage)/t_step)
        d_Vout_slope = abs((self.output_net.voltage - self.output_net.voltage_just_now)/t_step)

        if (d_Vna_slope > settle_threshold) or (d_Vnb_slope > settle_threshold): # input not settled
            self.status = "active"
            self.input_net_A_last_active_voltage = self.input_net_A.voltage  # update last active voltage
            self.input_net_B_last_active_voltage = self.input_net_B.voltage
        elif (d_Vout_slope > settle_threshold): # input settled, but waiting on output to settle
            self.status = "stabilising"
        else: # all settled, let's sleep
            self.status = "sleep"

class NOR2(NAND2):
    # they have no difference in this simulation procedure
    # when creating gate instances, different LUT_and_boundary will be given to them, hence defineing their charactrstic
    pass


class Circuit:

    def __init__(self, verilog_path, config=None):
        self.config = config
        self.verilog_path = verilog_path

    def read_netlist(self):
        # open verilog netlist to read
        print "reading netlist file..."
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
            #INV_LUT = load_LUT(LUT_dir["INV"])
            INV_LUT = load_LUT(LUT_name_front + "_INV_" + LUT_name_back) # different style LUT loading
        if presence_detection["nand"]:
            #NAND2_LUT = load_LUT(LUT_dir["NAND2"])
            NAND2_LUT = load_LUT(LUT_name_front + "_NAND2_" + LUT_name_back)
        if presence_detection["nor"]:
            #NOR2_LUT = load_LUT(LUT_dir["NOR2"])
            NOR2_LUT = load_LUT(LUT_name_front + "_NOR2_" + LUT_name_back)

        
        # TODO: above object creation is only testing verion. it can not read nets if it's in multiple line in verilog.
        # TODO: it cannot function correctly if gate is defined before net. don't know if it's allowed in verilog.
        # TODO: it cannot detect nand2 from nand3, and only work for nand2 at this point
        for line in netlist_file:
            # step 1, create all net instances
            if "input " in line:
                line = re.split('\W+', line) # extract all words from line
                self.input_nodes = line[1:-1] # primary input list
                for each_net_name in self.input_nodes:
                    self.nets_dict[each_net_name] = net(name=each_net_name, initial_voltage=0)
            elif "output " in line:
                line = re.split('\W+', line) # extract all words from line
                self.output_nodes = line[1:-1]
                for each_net_name in self.output_nodes:
                    self.nets_dict[each_net_name] = net(name=each_net_name, initial_voltage=0)
            elif "wire " in line:
                line = re.split('\W+', line) # extract all words from line
                self.circuit_internal_nodes = line[1:-1]
                for each_net_name in self.circuit_internal_nodes:
                    self.nets_dict[each_net_name] = net(name=each_net_name, initial_voltage=0)

            # step 2, create all logic gates instances, pass net instance to gates, according to netlist
            elif "inv" in line:
                line = re.split('\W+', line) # extract all words from line
                line = line[1:-1]
                #print line
                # 0 name, 1 output, 2 in_A, 3 in_B
                gate_name        = line[0]
                output_net_name  = line[1]
                input_net_name = line[2]
                # note: output net and input net instance are passed in as argument here
                self.gates_dict[gate_name] = INV(name=gate_name, LUT_and_boundary=INV_LUT,
                                              output_net=self.nets_dict[output_net_name],
                                              input_net=self.nets_dict[input_net_name])

            elif "nand" in line:
                line = re.split('\W+', line) # extract all words from line
                line = line[1:-1]
                #print line
                # 0 name, 1 output, 2 in_A, 3 in_B
                gate_name        = line[0]
                output_net_name  = line[1]
                input_A_net_name = line[2]
                input_B_net_name = line[3]
                # note: output net and input net instance are passed in as argument here
                self.gates_dict[gate_name] = NAND2(name=gate_name, LUT_and_boundary=NAND2_LUT,
                                              output_net=self.nets_dict[output_net_name],
                                              input_net_A=self.nets_dict[input_A_net_name] ,
                                              input_net_B=self.nets_dict[input_B_net_name])

            elif "nor" in line:
                line = re.split('\W+', line) # extract all words from line
                line = line[1:-1]
                #print line
                # 0 name, 1 output, 2 in_A, 3 in_B
                gate_name        = line[0]
                output_net_name  = line[1]
                input_A_net_name = line[2]
                input_B_net_name = line[3]
                # note: output net and input net instance are passed in as argument here
                self.gates_dict[gate_name] = NOR2(name=gate_name, LUT_and_boundary=NOR2_LUT,
                                              output_net=self.nets_dict[output_net_name],
                                              input_net_A=self.nets_dict[input_A_net_name] ,
                                              input_net_B=self.nets_dict[input_B_net_name])


    def attach_LUTs(self): 
        pass

    
    def levelize(self):
        # TODO: @Hao just check if its working good here later

        for each_net in self.input_nodes: # primary input list
            self.nets_dict[each_net].level = 0 # set to 0
        # TODO URGENT: @Hao, what is this circuit_internal_nodes
        # TODO: Saeed 2 @Hao: I guess just the internal nodes level init is enough?
        for each_net in (self.circuit_internal_nodes + self.output_nodes): # all other nodes
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
            this_gate_output_net_level = self.gates_dict[each_gate].output_net.level
            # I choose to define a gate's level as its output net's level
            self.gates_dict[each_gate].level = this_gate_output_net_level
            if this_gate_output_net_level > circuit_max_level:
                circuit_max_level = this_gate_output_net_level # record max level

        # iterate though all gate again to put their name to corresponding level list
        #create an empty list with max_level+1 slots, so we can put PI in this list as well
        level_list = [[] for i in range(circuit_max_level+1)]

        level_list[0] = self.input_nodes # put PI in level 0
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
            self.gates_dict[each_gate].simulate(just_update_CI=True)
            
        # LOAD CAP of PRIMARY OUTPUTs 
        if (self.config.load_all_PO == True):
            final_output_load = dict()
            for each_net in self.output_nodes:
                final_output_load[each_net] = self.config.cap_value
        else:
            final_output_load = self.config.final_output_load
    
        # TODO: does not seem to work. ...
        # ... add cap load to all output nets, this fix the problem for CSM simulator not stable
        for each_net in self.output_nodes:
            #nets_dict[each_net].extra_cap_load = 1e-16
            self.nets_dict[each_net].extra_cap_load = final_output_load[each_net]


    def init_ckt(self):
        # TODO: first check if levelization is done
        # TODO: think about removing this signal later from here:
        PI_signal_dict = self.config.PI_signal_dict
        t_step = self.config.T_STEP

        print "finding initial conditions..."
        initial_voltage_settle_threshold = self.config.initial_voltage_settle_threshold
        all_nets_settled = False
        while (all_nets_settled == False):
            #print "finding initial conditions..."
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
            for each_net in (self.circuit_internal_nodes + self.output_nodes):
                dV_of_this_net = self.nets_dict[each_net].voltage - self.nets_dict[each_net].voltage_just_now
                slope = abs(dV_of_this_net/t_step)
                #print slope
                #print "th: " + str(initial_voltage_settle_threshold)
                if (slope > initial_voltage_settle_threshold):
                    all_nets_settled = False
            #print all_nets_settled

        # print initial conditions
        print "initial conditions:"
        for each_net in (self.circuit_internal_nodes + self.output_nodes):
            print "{}: {:.4f}".format(each_net, self.nets_dict[each_net].voltage) 
            # each_net +": " + str(self.nets_dict[each_net].voltage)

    
    def simulate_step(self, t):
        t_step = self.config.T_STEP
        signal = self.config.PI_signal_dict
        init_vth = self.config.initial_voltage_settle_threshold

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
        init_vth = self.config.initial_voltage_settle_threshold

        save_file = open(self.config.save_file_dir, "w")
        save_file.write("# time")
        for each_net in self.config.voltage_nodes_to_save:
            save_file.write(" " + each_net)
        save_file.write("\n")

        print "simulating..."
        for step_number in range(int(t_tot / t_step)):
            t = step_number * t_step
            # t_ps = t * 1e12  # just for readability
            self.simulate_step(t)
            
            # save voltage of chosen nets
            save_file.write(str(t))
            for each_net in self.config.voltage_nodes_to_save:
                save_file.write(","+ str(self.nets_dict[each_net].voltage))
            save_file.write("\n")

        save_file.close()


    def info(self):
        print self.ckt_name







