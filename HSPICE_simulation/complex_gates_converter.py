# author: Eda Yan <yidayan@usc.edu>
# input file type : .v
# output file type : .v
import re

def complex_gates_converter(verilog_file_name):
        fin = open (verilog_file_name,'r')
        f = fin.readlines()
        f_copy = f
        fin.close()
        origin_netlist = f
        count_line = len(f)
        for i in range(count_line):
                f[i] = f[i].strip('\n')
                f[i] = f[i].strip(' ')
        count = 0
        for line in f:
                if line == '':
                        f.remove(line)
                if line[:2] == '//':
                        count += 1
        f = f[count:]

        complex_gate = []
        input_line = []
        output_line = []
        wire_line = []
        gate_line = []
        input_flag = 0
        output_flag = 0
        wire_flag = 0
        for line in f:
                if re.search('input', line[:6], re.IGNORECASE) or input_flag == 1:
                    input_flag = 1
                    input_line.append(line)
                    if ';' in line:
                        input_flag = 0
                elif re.search('output', line[:6], re.IGNORECASE) or output_flag == 1:
                    output_flag = 1
                    output_line.append(line)
                    if ';' in line:
                        output_flag = 0
                elif re.search('wire', line[:6], re.IGNORECASE) or wire_flag == 1:
                    wire_flag = 1
                    wire_line.append(line)
                    if ';' in line:
                        wire_flag = 0
                elif re.search('and', line[:6], re.IGNORECASE) or\
                   re.search('or', line[:6], re.IGNORECASE) or\
                   re.search('nand', line[:6], re.IGNORECASE) or\
                   re.search('nor', line[:6], re.IGNORECASE) or\
                   re.search('not', line[:6], re.IGNORECASE) or\
                   re.search('xor', line[:6], re.IGNORECASE) or\
                   re.search('buf', line[:6], re.IGNORECASE):
                        gate_line.append(line)
        input_line1 = ''
        for line in input_line:
                input_line1 = input_line1 + line
        output_line1 = ''
        for line in output_line:
                output_line1 = output_line1 + line
        wire_line1 = ''
        for line in wire_line:
                wire_line1 = wire_line1 + line
        input_line = [input_line1]
        output_line = [output_line1]
        wire_line = [wire_line1]
        
        for gate in gate_line:
                if not (re.search('NAND2', gate[2:], re.IGNORECASE) or\
                        re.search('NOR2', gate[2:], re.IGNORECASE) or\
                        re.search('NOT', gate[2:], re.IGNORECASE) or\
                        re.search('BUFF', gate[2:], re.IGNORECASE)):
                        complex_gate.append(gate)

        gate_to_be_deleted = []
        gate_to_be_added = []
        new_gate_num = 1
        node_to_be_added = []

        for gate in complex_gate:
                gate_to_be_deleted.append(gate)
                gate_list = gate.split()
                gate_ports = []
                for item in gate_list:
                        if '(' in item:
                                gate_ports.append(item[1:-1])
                        elif ')' in item:
                                gate_ports.append(item[0:-2])
                        elif ',':
                                gate_ports.append(item[0:-1])
                gate_ports = gate_ports[2:]
                if "AND2" in gate:
                        input_ports = gate_ports[1:]
                        output_port = gate_ports[0]
                        nand_2 = 'nand NAND2_NEW_' + str(new_gate_num) + ' (' + \
                                 output_port + '_1, ' + input_ports[0] + ', ' + \
                                 input_ports[1] + ');\n'
                        new_gate_num = new_gate_num + 1
                        inv = 'not NOT1_NEW_' + str(new_gate_num) + ' (' + \
                              output_port + ', ' + output_port + '_1);\n'
                        new_gate_num = new_gate_num + 1
                        gate_to_be_added.append(nand_2)
                        gate_to_be_added.append(inv)
                        new_node = output_port + '_1'
                        node_to_be_added.append(new_node)
                elif "OR2" in gate:
                        input_ports = gate_ports[1:]
                        output_port = gate_ports[0]
                        nor_2 = 'nor NOR2_NEW_' + str(new_gate_num) + ' (' + \
                                 output_port + '_1, ' + input_ports[0] + ', ' + \
                                 input_ports[1] + ');\n'
                        new_gate_num = new_gate_num + 1
                        inv = 'not NOT1_NEW_' + str(new_gate_num) + ' (' + \
                              output_port + ', ' + output_port + '_1);\n'
                        new_gate_num = new_gate_num + 1
                        gate_to_be_added.append(nor_2)
                        gate_to_be_added.append(inv)
                        new_node = output_port + '_1'
                        node_to_be_added.append(new_node)
                elif "XOR2" in gate:
                        input_ports = gate_ports[1:]
                        output_port = gate_ports[0]
                        inv1 = 'not NOT1_NEW_' + str(new_gate_num) + ' (' + \
                               output_port + '_1, ' + input_ports[0] + ');\n'
                        new_gate_num = new_gate_num + 1
                        inv2 = 'not NOT1_NEW_' + str(new_gate_num) + ' (' + \
                               output_port + '_2, ' + input_ports[1] + ');\n'
                        new_gate_num = new_gate_num + 1
                        nand1 = 'nand NAND2_NEW_' + str(new_gate_num) + ' (' + \
                                 output_port + '_3, ' + input_ports[0] + ', ' + \
                                 output_port + '_2);\n'
                        new_gate_num = new_gate_num + 1
                        nand2 = 'nand NAND2_NEW_' + str(new_gate_num) + ' (' + \
                                 output_port + '_4, ' + input_ports[1] + ', ' + \
                                 output_port + '_1);\n'
                        new_gate_num = new_gate_num + 1
                        nand3 = 'nand NAND2_NEW_' + str(new_gate_num) + ' (' + \
                                 output_port + ', ' + output_port + '_3, ' + \
                                 output_port + '_4);\n'
                        new_gate_num = new_gate_num + 1
                        gate_to_be_added.append(inv1)
                        gate_to_be_added.append(inv2)
                        gate_to_be_added.append(nand1)
                        gate_to_be_added.append(nand2)
                        gate_to_be_added.append(nand3)
                        new_node = []
                        for i in range(1,5):
                                new_node = output_port + '_' + str(i)
                                node_to_be_added.append(new_node)
                elif "NAND3" in gate:
                        input_ports = gate_ports[1:]
                        output_port = gate_ports[0]
                        nand1 = 'nand NAND2_NEW_' + str(new_gate_num) + ' (' + \
                                 output_port + '_1, ' + input_ports[0] + ', ' + \
                                 input_ports[1] + ');\n'
                        new_gate_num = new_gate_num + 1
                        inv1 = 'not NOT1_NEW_' + str(new_gate_num) + ' (' + \
                               output_port + '_2, ' + output_port + '_1);\n'
                        new_gate_num = new_gate_num + 1
                        nand2 = 'nand NAND2_NEW_' + str(new_gate_num) + ' (' + \
                                 output_port + ', ' + input_ports[2] + ', ' + \
                                 output_port + '_2);\n'
                        new_gate_num = new_gate_num + 1
                        gate_to_be_added.append(inv1)
                        gate_to_be_added.append(nand1)
                        gate_to_be_added.append(nand2)
                        new_node1 = output_port + '_1'
                        new_node2 = output_port + '_2'
                        node_to_be_added.append(new_node1)
                        node_to_be_added.append(new_node2)
                elif "NAND4" in gate:
                        input_ports = gate_ports[1:]
                        output_port = gate_ports[0]
                        O_1 = output_port + '_1'
                        O_2 = output_port + '_2'
                        O_3 = output_port + '_3'
                        O_4 = output_port + '_4'
                        nand1 = 'nand NAND2_NEW_' + str(new_gate_num) + ' (' + \
                                 O_1 + ', ' + input_ports[0] + ', ' + input_ports[1] + ');\n'
                        new_gate_num = new_gate_num + 1
                        nand2 = 'nand NAND2_NEW_' + str(new_gate_num) + ' (' + \
                                 O_2 + ', ' + input_ports[2] + ', ' + input_ports[3] + ');\n'
                        new_gate_num = new_gate_num + 1
                        inv1 = 'not NOT1_NEW_' + str(new_gate_num) + ' (' + \
                               O_3 + ', ' + O_1 + ');\n'
                        new_gate_num = new_gate_num + 1
                        inv2 = 'not NOT1_NEW_' + str(new_gate_num) + ' (' + \
                               O_4 + ', ' + O_2 + ');\n'
                        new_gate_num = new_gate_num + 1
                        nand3 = 'nand NAND2_NEW_' + str(new_gate_num) + ' (' + \
                                 output_port + ', ' + O_3 + ', ' + O_4 + ');\n'
                        new_gate_num = new_gate_num + 1
                        gate_to_be_added.append(inv1)
                        gate_to_be_added.append(inv2)
                        gate_to_be_added.append(nand1)
                        gate_to_be_added.append(nand2)
                        gate_to_be_added.append(nand3)
                        node_to_be_added.append(O_1)
                        node_to_be_added.append(O_2)
                        node_to_be_added.append(O_3)
                        node_to_be_added.append(O_4)
                elif "NOR3" in gate:
                        input_ports = gate_ports[1:]
                        output_port = gate_ports[0]
                        O_1 = output_port + '_1'
                        O_2 = output_port + '_2'
                        nor1 = 'nor NOR2_NEW_' + str(new_gate_num) + ' (' + \
                                O_1 + ', ' + input_ports[0] + ', ' + input_ports[1] + ');\n'
                        new_gate_num = new_gate_num + 1
                        inv1 = 'not NOT1_NEW_' + str(new_gate_num) + ' (' + \
                               O_2 + ', ' + O_1 + ');\n'
                        new_gate_num = new_gate_num + 1
                        nor2 = 'nor NOR2_NEW_' + str(new_gate_num) + ' (' + \
                                output_port + ', ' + input_ports[2] + ', ' + O_2 + ');\n'
                        new_gate_num = new_gate_num + 1
                        gate_to_be_added.append(inv1)
                        gate_to_be_added.append(nor1)
                        gate_to_be_added.append(nor2)
                        node_to_be_added.append(O_1)
                        node_to_be_added.append(O_2)
                elif "NOR4" in gate:
                        input_ports = gate_ports[1:]
                        output_port = gate_ports[0]
                        O_1 = output_port + '_1'
                        O_2 = output_port + '_2'
                        O_3 = output_port + '_3'
                        O_4 = output_port + '_4'
                        nor1 = 'nor NOR2_NEW_' + str(new_gate_num) + ' (' + \
                                 O_1 + ', ' + input_ports[0] + ', ' + input_ports[1] + ');\n'
                        new_gate_num = new_gate_num + 1
                        nor2 = 'nor NOR2_NEW_' + str(new_gate_num) + ' (' + \
                                 O_2 + ', ' + input_ports[2] + ', ' + input_ports[3] + ');\n'
                        new_gate_num = new_gate_num + 1
                        inv1 = 'not NOT1_NEW_' + str(new_gate_num) + ' (' + \
                               O_3 + ', ' + O_1 + ');\n'
                        new_gate_num = new_gate_num + 1
                        inv2 = 'not NOT1_NEW_' + str(new_gate_num) + ' (' + \
                               O_4 + ', ' + O_2 + ');\n'
                        new_gate_num = new_gate_num + 1
                        nor3 = 'nor NOR2_NEW_' + str(new_gate_num) + ' (' + \
                                 output_port + ', ' + O_3 + ', ' + O_4 + ');\n'
                        new_gate_num = new_gate_num + 1
                        gate_to_be_added.append(inv1)
                        gate_to_be_added.append(inv2)
                        gate_to_be_added.append(nor1)
                        gate_to_be_added.append(nor2)
                        gate_to_be_added.append(nor3)
                        node_to_be_added.append(O_1)
                        node_to_be_added.append(O_2)
                        node_to_be_added.append(O_3)
                        node_to_be_added.append(O_4)
                elif "AND3" in gate:
                        input_ports = gate_ports[1:]
                        output_port = gate_ports[0]
                        nand1 = 'nand NAND2_NEW_' + str(new_gate_num) + ' (' + \
                                 output_port + '_1, ' + input_ports[0] + ', ' + \
                                 input_ports[1] + ');\n'
                        new_gate_num = new_gate_num + 1
                        inv1 = 'not NOT1_NEW_' + str(new_gate_num) + ' (' + \
                               output_port + '_2, ' + output_port + '_1);\n'
                        new_gate_num = new_gate_num + 1
                        nand2 = 'nand NAND2_NEW_' + str(new_gate_num) + ' (' + \
                                 output_port + '_3, ' + input_ports[2] + ', ' + \
                                 output_port + '_2);\n'
                        new_gate_num = new_gate_num + 1
                        inv2 = 'not NOT1_NEW_' + str(new_gate_num) + ' (' + \
                               output_port + ', ' + output_port + '_3);\n'
                        new_gate_num = new_gate_num + 1
                        gate_to_be_added.append(inv1)
                        gate_to_be_added.append(inv2)
                        gate_to_be_added.append(nand1)
                        gate_to_be_added.append(nand2)
                        new_node1 = output_port + '_1'
                        new_node2 = output_port + '_2'
                        new_node3 = output_port + '_3'
                        node_to_be_added.append(new_node1)
                        node_to_be_added.append(new_node2)
                        node_to_be_added.append(new_node3)
                elif "AND4" in gate:
                        input_ports = gate_ports[1:]
                        output_port = gate_ports[0]
                        O_1 = output_port + '_1'
                        O_2 = output_port + '_2'
                        O_3 = output_port + '_3'
                        O_4 = output_port + '_4'
                        O_5 = output_port + '_5'
                        nand1 = 'nand NAND2_NEW_' + str(new_gate_num) + ' (' + \
                                 O_1 + ', ' + input_ports[0] + ', ' + input_ports[1] + ');\n'
                        new_gate_num = new_gate_num + 1
                        nand2 = 'nand NAND2_NEW_' + str(new_gate_num) + ' (' + \
                                 O_2 + ', ' + input_ports[2] + ', ' + input_ports[3] + ');\n'
                        new_gate_num = new_gate_num + 1
                        inv1 = 'not NOT1_NEW_' + str(new_gate_num) + ' (' + \
                               O_3 + ', ' + O_1 + ');\n'
                        new_gate_num = new_gate_num + 1
                        inv2 = 'not NOT1_NEW_' + str(new_gate_num) + ' (' + \
                               O_4 + ', ' + O_2 + ');\n'
                        new_gate_num = new_gate_num + 1
                        nand3 = 'nand NAND2_NEW_' + str(new_gate_num) + ' (' + \
                                 O_5 + ', ' + O_3 + ', ' + O_4 + ');\n'
                        new_gate_num = new_gate_num + 1
                        inv3 = 'not NOT1_NEW_' + str(new_gate_num) + ' (' + \
                               output_port + ', ' + O_5 + ');\n'
                        new_gate_num = new_gate_num + 1
                        gate_to_be_added.append(inv1)
                        gate_to_be_added.append(inv2)
                        gate_to_be_added.append(inv3)
                        gate_to_be_added.append(nand1)
                        gate_to_be_added.append(nand2)
                        gate_to_be_added.append(nand3)
                        node_to_be_added.append(O_1)
                        node_to_be_added.append(O_2)
                        node_to_be_added.append(O_3)
                        node_to_be_added.append(O_4)
                        node_to_be_added.append(O_5)
                elif "OR3" in gate:
                        input_ports = gate_ports[1:]
                        output_port = gate_ports[0]
                        O_1 = output_port + '_1'
                        O_2 = output_port + '_2'
                        O_3 = output_port + '_3'
                        nor1 = 'nor NOR2_NEW_' + str(new_gate_num) + ' (' + \
                                O_1 + ', ' + input_ports[0] + ', ' + input_port[1] + ');\n'
                        new_gate_num = new_gate_num + 1
                        inv1 = 'not NOT1_NEW_' + str(new_gate_num) + ' (' + \
                               O_2 + ', ' + O_1 + ');\n'
                        new_gate_num = new_gate_num + 1
                        nor2 = 'nor NOR2_NEW_' + str(new_gate_num) + ' (' + \
                                O_3 + ', ' + input_ports[2] + ', ' + O_2 + ');\n'
                        new_gate_num = new_gate_num + 1
                        inv2 = 'not NOT1_NEW_' + str(new_gate_num) + ' (' + \
                               output_port + ', ' + O_3 + ');\n'
                        new_gate_num = new_gate_num + 1
                        gate_to_be_added.append(inv1)
                        gate_to_be_added.append(inv2)
                        gate_to_be_added.append(nor1)
                        gate_to_be_added.append(nor2)
                        node_to_be_added.append(O_1)
                        node_to_be_added.append(O_2)
                        node_to_be_added.append(O_3)
                elif "OR4" in gate:
                        input_ports = gate_ports[1:]
                        output_port = gate_ports[0]
                        O_1 = output_port + '_1'
                        O_2 = output_port + '_2'
                        O_3 = output_port + '_3'
                        O_4 = output_port + '_4'
                        O_5 = output_port + '_5'
                        nor1 = 'nor NOR2_NEW_' + str(new_gate_num) + ' (' + \
                                 O_1 + ', ' + input_ports[0] + ', ' + input_ports[1] + ');\n'
                        new_gate_num = new_gate_num + 1
                        nor2 = 'nor NOR2_NEW_' + str(new_gate_num) + ' (' + \
                                 O_2 + ', ' + input_ports[2] + ', ' + input_ports[3] + ');\n'
                        new_gate_num = new_gate_num + 1
                        inv1 = 'not NOT1_NEW_' + str(new_gate_num) + ' (' + \
                               O_3 + ', ' + O_1 + ');\n'
                        new_gate_num = new_gate_num + 1
                        inv2 = 'not NOT1_NEW_' + str(new_gate_num) + ' (' + \
                               O_4 + ', ' + O_2 + ');\n'
                        new_gate_num = new_gate_num + 1
                        nor3 = 'nor NOR2_NEW_' + str(new_gate_num) + ' (' + \
                                 O_5 + ', ' + O_3 + ', ' + O_4 + ');\n'
                        new_gate_num = new_gate_num + 1
                        inv3 = 'not NOT1_NEW_' + str(new_gate_num) + ' (' + \
                               output_port + ', ' + O_5 + ');\n'
                        new_gate_num = new_gate_num + 1
                        gate_to_be_added.append(inv1)
                        gate_to_be_added.append(inv2)
                        gate_to_be_added.append(inv3)
                        gate_to_be_added.append(nor1)
                        gate_to_be_added.append(nor2)
                        gate_to_be_added.append(nor3)
                        node_to_be_added.append(O_1)
                        node_to_be_added.append(O_2)
                        node_to_be_added.append(O_3)
                        node_to_be_added.append(O_4)
                        node_to_be_added.append(O_5)
                else:
                        print(gate, " : this gate is too complex to be converted yet")

        # delete complex gates which are already converted
        i = 0
        for gate in gate_line:
                if gate == gate_to_be_deleted[i]:
                        gate_line.remove(gate)
                        i = i + 1
        # add new gates into gate_line
        for gate in gate_to_be_added:
                gate_line.append(gate)

        # print out to output file
        # need to add node_to_be_added into wire and add gate_to_be_added into netlist
        # and delete the gate_to_be_deleted
        # print(wire_line)
        # print(node_to_be_added)
        wire_str = ''
        for node in node_to_be_added:
                if wire_str == '':
                        wire_str = wire_str + node
                else:
                        wire_str = wire_str + ',' + node
        wire_str = wire_str + ';\n'
        
        new_file_name = verilog_file_name.replace('.v', '_flated.v')
        fout = open(new_file_name, 'w')
        wire_flag = 0
        i = 0
        # print(len(gate_to_be_deleted))
        for line in f_copy:
                if 'wire' in line or wire_flag == 1:
                        wire_flag = 1
                        if ';' in line:
                                line = line.replace(';', ',')
                                fout.writelines([line, '\n'])
                                fout.writelines(wire_str)
                                wire_flag = 0
                                continue
                        fout.writelines([line, '\n'])
                elif 'endmodule' in line:
                        for newgate in gate_to_be_added:
                                fout.writelines(newgate)
                        fout.writelines('endmodule\n')
                elif line == gate_to_be_deleted[i]:
                        # print(line, gate_to_be_deleted[i])
                        # print(i)
                        if (i < (len(gate_to_be_deleted) - 1)):
                                i = i + 1
                        continue
                else:
                        fout.writelines([line, '\n'])
        fout.close()

        
complex_gates_converter('c880.v')





