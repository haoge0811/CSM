# Author: haoge <haoge@usc.edu> at USC SPORT Lab

from functions import *

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


