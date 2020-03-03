# Author: haoge <haoge@usc.edu> at USC SPORT Lab

import re
import importlib # to import config file given name string
from classes import *

def main(config_file_name):
    # improting variable from config file
    #config_file_name = "config"
    config_file = importlib.import_module(config_file_name)

    # added section for different style LUT loading
    LUT_name_front = config_file.LUT_bin_dir + config_file.TECH
    LUT_name_back = "VL" + str(config_file.VL) + "_VH" + str(config_file.VH) + "_VSTEP" + \
                    str(config_file.VSTEP) + "_P" + str(config_file.PROCESS_VARIATION) + "_V" \
                    + str(config_file.VDD) + "_T" + str(config_file.TEMPERATURE) + ".lut"
    # section end


    #LUT_dir = config_file.LUT_dir
    verilog_netlist_dir = config_file.verilog_netlist_dir
    #final_output_load = config_file.final_output_load
    PI_signal_dict = config_file.PI_signal_dict
    t_step = config_file.T_STEP
    t_tot = config_file.T_TOT
    save_file_dir = config_file.save_file_dir
    voltage_nodes_to_save = config_file.voltage_nodes_to_save
    # importing compelete
    # checked after this modification, original function not affected



    #def the_creator(verlog_netlist_dir): # this function create all instances that is going to be used for simulation.

    #verilog_netlist_dir = "./c17.v"
    # open verilog netlist to read
    print "reading netlist file..."
    netlist_file = open(verilog_netlist_dir, "r")
    nets_dict = dict()
    gates_dict = dict()

    #presence_detection and LUT loading TODO: could do this section in a more tidy way
    presence_detection = dict()
    sensitive_names = ["inv", "nand", "nor"]
    for a_name in sensitive_names:
        presence_detection[a_name] = False
    for line in netlist_file:
        for a_name in sensitive_names:
            if a_name in line:
                presence_detection[a_name] = True
    netlist_file.seek(0) # reset input file position cursor

    # Load corresponding LUT
    if presence_detection["inv"]:
        #INV_LUT = load_LUT(LUT_dir["INV"])
        INV_LUT = load_LUT(LUT_name_front + "_INV_" + LUT_name_back) # different style LUT loading
    if presence_detection["nand"]:
        #NAND2_LUT = load_LUT(LUT_dir["NAND2"])
        NAND2_LUT = load_LUT(LUT_name_front + "_NAND2_" + LUT_name_back)
    if presence_detection["nor"]:
        #NOR2_LUT = load_LUT(LUT_dir["NOR2"])
        NOR2_LUT = load_LUT(LUT_name_front + "_NOR2_" + LUT_name_back)

    for a_name in sensitive_names:
        if presence_detection[a_name]:
            print a_name + ", detected in netlist"
    #quit()
    # section end
    # checked function still correct after all this

    for line in netlist_file:
        # step 1, create all net instances
        if "input " in line:
            line = re.split('\W+', line) # extract all words from line
            input_nodes = line[1:-1] # primary input list
            for each_net_name in input_nodes:
                nets_dict[each_net_name] = net(name=each_net_name, initial_voltage=0)
        elif "output " in line:
            line = re.split('\W+', line) # extract all words from line
            output_nodes = line[1:-1]
            for each_net_name in output_nodes:
                nets_dict[each_net_name] = net(name=each_net_name, initial_voltage=0)
        elif "wire " in line:
            line = re.split('\W+', line) # extract all words from line
            circuit_internal_nodes = line[1:-1]
            for each_net_name in circuit_internal_nodes:
                nets_dict[each_net_name] = net(name=each_net_name, initial_voltage=0)

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
            gates_dict[gate_name] = INV(name=gate_name, LUT_and_boundary=INV_LUT,
                                          output_net=nets_dict[output_net_name],
                                          input_net=nets_dict[input_net_name])

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
            gates_dict[gate_name] = NOR2(name=gate_name, LUT_and_boundary=NOR2_LUT,
                                          output_net=nets_dict[output_net_name],
                                          input_net_A=nets_dict[input_A_net_name] ,
                                          input_net_B=nets_dict[input_B_net_name])

    # TODO above object creation is only testing verion. it can not read nets if it's in multiple line in verilog.
    # it cannot function correctly if gate is defined before net. don't know if it's allowed in verilog.
    # it cannot detect nand2 from nand3, and only work for nand2 at this point

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

    # added section for load all PO
    if (config_file.load_all_PO == True):
        final_output_load = dict()
        for each_net in output_nodes:
            final_output_load[each_net] = config_file.cap_value
    else:
        final_output_load = config_file.final_output_load
    # section end



    #CL = nets_dict["N22"].sum_CL()
    #print CL
    # does not seem to work. add cap load to all output nets, this fix the problem for CSM simulator not stable
    for each_net in output_nodes:
        #nets_dict[each_net].extra_cap_load = 1e-16
        nets_dict[each_net].extra_cap_load = final_output_load[each_net]
    #CL = nets_dict["N22"].sum_CL()
    #print CL

    # extra setting, save voltage to file
    #save_file = open("./voltage_save.csv", "w")

    # let's get on with the actual simulation
    #t_tot = 300e-12
    #t_step = 0.01e-12

    # remember to get signal to PI
    #PI_signal_dict = {
    #    "N1":Signal(mode = "constant", constant=0.7),
    #    "N2":Signal(mode = "constant", constant=0.0),
    #    "N3":Signal(mode = "constant", constant=0.7),
    #    "N6":Signal(mode = "constant", constant=0.0),
    #    "N7":Signal(mode="ramp_lh", param={"vdd": 0.7, "t_0": 5e-12, "t_lh": 50e-12})}

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

    save_file = open(save_file_dir, "w")
    # write heading
    save_file.write("# time")
    for each_net in voltage_nodes_to_save:
        save_file.write(" " + each_net)
    save_file.write("\n")
    # write heading ends

    # actual simulation
    print "simulating..."
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
        save_file.write(str(t))
        for each_net in voltage_nodes_to_save:
            save_file.write(","+ str(nets_dict[each_net].voltage))
        save_file.write("\n")

    save_file.close()


# if running stand alone
if __name__ == '__main__':
    import sys
    print sys.argv[1]
    if len(sys.argv) != 2:
        print "Usage: python OOP_circuit_simulator.py config.py"
        print "config.py must be in same directory as simulator"
    else:
        main(sys.argv[1][:-3]) # -3 to strip out ".py"