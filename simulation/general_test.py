'''a_dict = dict()
a_dict["dfa"] = 4

for each_key in a_dict.keys():
    print("haha")
'''
import importlib

module_name = "config"

module = importlib.import_module(module_name)

print(module)
#print(module.verilog_netlist_dir)

module.__init__()
print(verilog_netlist_dir)