# Author: haoge <haoge@usc.edu> at USC SPORT Lab

import re
from classes import *

def create_net_instance(list_of_net): # create_net_instance from list of net names to be created
    for each_item in list_of_net:
        net_name = each_item
        nets_dict[net_name] = net(name=net_name, initial_voltage=0)


#def the_creator(verlog_netlist_dir): # this function create all instances that is going to be used for simulation.

NAND2_LUT = load_LUT("../../LUT_bin/FINFET_7nm_LSTP_NAND2_VL-0.14_VH0.84_VSTEP0.05_P1.0_V0.7_T25.0.lut")

verlog_netlist_dir = "./c17.v"

# open verilog netlist to read
netlist_file = open(verlog_netlist_dir, "r")
nets_dict = dict()
gates_dict = dict()
for line in netlist_file:
    # step 1, create all net instances
    if "input " in line:
        line = re.split('\W+', line) # extract all words from line
        input_nodes = line[1:-1] # primary input list
        create_net_instance(input_nodes)
    elif "output " in line:
        line = re.split('\W+', line) # extract all words from line
        output_nodes = line[1:-1]
        create_net_instance(output_nodes)
    elif "wire " in line:
        line = re.split('\W+', line) # extract all words from line
        circuit_internal_nodes = line[1:-1]
        create_net_instance(circuit_internal_nodes)

    # step 2, create all logic gates instances, pass net instance to gates, according to netlist
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
        gates_dict[gate_name] = NAND2(name=gate_name, LUT_and_boundary=NAND2_LUT,
                                      output_net=nets_dict[output_net_name],
                                      input_net_A=nets_dict[input_A_net_name] ,
                                      input_net_B=nets_dict[input_B_net_name])


# circuit levelization. input arguement to this block all gate and net instance. list of PI and all else nets.
for each_net in input_nodes: # primary input list
    nets_dict[each_net].level = 0 # set to 0
for each_net in (circuit_internal_nodes + output_nodes): # all other nodes
    nets_dict[each_net].level = 1 # initialize to 1

# begin levlization loop
while True:
    circuit_level_updated = False  # initialize to false
    # go through all gates
    for each_gate in gates_dict.keys():
        level_updated = gates_dict[each_gate].update_level()
        if level_updated:
            circuit_level_updated = True
            # if any gate updated its output net level during iteration, then the circuit overall has updated its level

    # at the end of all gate iteration, check if the circuit level has been updated
    # if no gate has updated its output net level during this iteration, then levlization is done
    if circuit_level_updated == False:
        break
# levelization end

# levelization recording
# iterate through all gate again to get max level,
# # and record all gate record all gate level according to their output net level
# I choose to do this in th end hope to reduce comparison brough by max level recording in previous iterations.
circuit_max_level = 1 # should at least be 1
for each_gate in gates_dict.keys():
    this_gate_output_net_level = gates_dict[each_gate].output_net.level
    # I choose to define a gate's level as its output net's level
    gates_dict[each_gate].level = this_gate_output_net_level
    if this_gate_output_net_level > circuit_max_level:
        circuit_max_level = this_gate_output_net_level # record max level

# iterate though all gate again to put their name to corresponding level list
#create an empty list with max_level+1 slots, so we can put PI in this list as well
level_list = [[] for i in range(circuit_max_level+1)]

level_list[0] = input_nodes # put PI in level 0
for each_gate in gates_dict.keys():
    this_gate_level = gates_dict[each_gate].level
    level_list[this_gate_level].append(gates_dict[each_gate].name) # put gates name in corresponding list
# levelization recording end

# below is gold, pre-simulate Cin loaing iteration
# run all gates at 0 time just to get cap_load value on nets populated.
for each_gate in gates_dict.keys():
    gates_dict[each_gate].simulate(just_update_CI=True)
# above is gold


#CL = nets_dict["N22"].sum_CL()
#print CL
# does not seem to work. add cap load to all output nets, this fix the problem for CSM simulator not stable
for each_net in output_nodes:
    nets_dict[each_net].extra_cap_load = 1e-16
#CL = nets_dict["N22"].sum_CL()
#print CL

# extra setting, save voltage to file
save_file = open("./voltage_save.csv", "w")

# let's get on with the actual simulation
t_tot = 300e-12
t_step = 0.01e-12

# remember to get signal to PI
PI_signal_dict = {
    "N1":Signal(mode = "constant", constant=0.7),
    "N2":Signal(mode = "constant", constant=0.0),
    "N3":Signal(mode = "constant", constant=0.7),
    "N6":Signal(mode = "constant", constant=0.0),
    "N7":Signal(mode="ramp_lh", param={"vdd": 0.7, "t_0": 5e-12, "t_lh": 50e-12})}

#N22 stay at 1
#N23 will go up

# same way as CL pre-load, we can figure out the initial condition, by pre-simulaing the circuit before time 0, to wait until every
# voltage nodes settles.
# here we can add a configurable setup. if user degined initial condition in config file, we use that way. otherwise,
# pre-simulate and find out initial condition ourself
initial_voltage_settle_threshold = 0.00001/0.01e-12 # change < 0.00001 in 0.01 ps
print "finding initial conditions..."
all_nets_settled = False
while (all_nets_settled == False):
    #print "finding initial conditions..."
    all_nets_settled = True
    for level in range(len(level_list)):  # simulate circuit level by level, from PI to output
        if level == 0:  # For Primary inputs
            for each_PI in level_list[level]:
                nets_dict[each_PI].update_voltage(PI_signal_dict[each_PI].get_val(0))  # use the PI value at time 0
        else:
            for each_gate in level_list[level]:
                gates_dict[each_gate].simulate(t_step)  # simulate the gate for this time step
    # TODO: this may not be the best orgnization todo this, check later
    # after simulation, check if all nets besides PI have settled
    for each_net in (circuit_internal_nodes + output_nodes):  # all other nodes
        dV_of_this_net = nets_dict[each_net].voltage - nets_dict[each_net].voltage_just_now
        slope = dV_of_this_net/t_step
        #print slope
        #print "th: " + str(initial_voltage_settle_threshold)
        if (slope > initial_voltage_settle_threshold):
            all_nets_settled = False
    #print all_nets_settled

# print initial conditions
print "initial conditions:"
for each_net in (circuit_internal_nodes + output_nodes):  # all other nodes
    print each_net +": " + str(nets_dict[each_net].voltage)


# actual simulation
for step_number in range(int(t_tot / t_step)):
    t = step_number * t_step
    t_ps = t * 1e12  # just for readability

    #print "simulating for t = " +str(t_ps) + "ps"
    for level in range(len(level_list)): # simulate circuit level by level, from PI to output
        if level == 0: # For Primary inputs
            for each_PI in level_list[level]:
                nets_dict[each_PI].update_voltage(PI_signal_dict[each_PI].get_val(t)) #(signal(t))
        else:
            for each_gate in level_list[level]:
                gates_dict[each_gate].simulate(t_step) # simulate the gate for this time step


    # extra save voltage
    save_file.write(str(t) +","+ str(nets_dict["N22"].voltage) +","+ str(nets_dict["N23"].voltage)+"\n")

save_file.close()

# once this works, consider putting all settings in a config file, much like spice style


#N16 =1, N19 = 1, N23 =0
