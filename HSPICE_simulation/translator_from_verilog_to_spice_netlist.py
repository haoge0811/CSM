# author: Eda Yan <yidayan@usc.edu>
# input file type : .v
# output file type : .sp
import re

def translator_from_verilog_to_spice_netlist(verilog_file_name, spice_file_name):
	fin = open (verilog_file_name,'r')
	f = fin.readlines()
	fin.close()
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
	#print(f)

	input_line = []
	output_line = []
	wire_line = []
	gate_line = []
	for line in f:
		if re.search('input', line[:6], re.IGNORECASE):
			input_line.append(line)
		if re.search('output', line[:6], re.IGNORECASE):
			output_line.append(line)
		if re.search('wire', line[:6], re.IGNORECASE):
			wire_line.append(line)
		if re.search('and', line[:6], re.IGNORECASE) or\
		   re.search('or', line[:6], re.IGNORECASE) or\
		   re.search('nand', line[:6], re.IGNORECASE) or\
		   re.search('nor', line[:6], re.IGNORECASE) or\
		   re.search('not', line[:6], re.IGNORECASE) or\
		   re.search('xor', line[:6], re.IGNORECASE) or\
		   re.search('buf', line[:6], re.IGNORECASE):
			gate_line.append(line)


	fout = open (spice_file_name, 'w')

	fout.writelines('vhi hi 0 vdd\n')
	fout.writelines('vlo lo 0 0\n\n')

	for line in gate_line:
		a = line.find(' ') #index1 of ' '
		b = line[a+1:].find(' ') #index2 of ' '
		gate_name = line[a+1:a+b+1]
		gate_ports = line[a+b+2:]
		c = gate_ports.find(',') #index1 of ','
		gate_output = gate_ports[1:c]
		gate_input = gate_ports[c+2:-2]
		d = gate_name.find('_') #index of '_'
		gate_type = gate_name[:d]
		gate_input = gate_input.replace(',','')
		fout.writelines([gate_name, '  ', 'hi  ', '0  ', \
						gate_input, '    ', gate_output, '    ', gate_type.upper(), '\n'])

	fout.writelines('\n')
	fout.close()
	return output_line
