

import pdb
import sys

import classes
from func_spice import print_header

if __name__ == '__main__':
    print_header()
    '''
    if -func or -f == "csm": do csm simulation 
    if -func or -f == "spice": do spice simulation 
    if -func or -f == "esim-all": do csm-sim and spice-sim and report esim
    if -func or -f == "esim": calculate esim, given csm and spice waveforms
    a new argument -plot which plots the results, diff for diff -func
    '''
    print sys.argv[1]
    parser = argparse.ArgumentParser()
    parser.add_argument('-func', type=str, required=True, help='Function')
    parser.add_argument('-conf', type=str, default="config.py", help='config file name')
    parser.add_argument('-plot', type=bool, default=False, help='plot flag')
    # parser.add_argument('-gpu', type=bool, default=True, help='use gpu or not')
    args = parser.parse_args()
    
    if args.func == "csm":
        config_file = importlib.import_module(args.conf)
        ckt = classes.Circuit(verilog_path=config_file.verilog_netlist_dir, config=config_file)
        ckt.read_netlist()
        ckt.levelize()
        ckt.set_caps()
        ckt.init_ckt()
        ckt.simulate_signal()
    elif args.func == "spice":
        pass

    else:
        print "function argument not found"


