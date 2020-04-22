

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
    # parser.add_argument('-netD', type=str, default = None, help='Device net type')
    # parser.add_argument('-netC', type=str, help='Cloud net type')
    # parser.add_argument('-net', type=str, required=True, help='net type')
    # parser.add_argument('-b', type=int, default=64, help='batch size')
    # parser.add_argument('-s', type=int, default=True, help='shuffle')
    # parser.add_argument('-w', type=int, default=4, help='number of workers')
    # parser.add_argument('-bc', type=int, default=1000, help='num batches')
    # parser.add_argument('-e', type=int, default=40, help='num epochs')
    # parser.add_argument('-func', type=str, required=True, help='function')
    # parser.add_argument('-ds', type=str, default="imagenet", help='dataset')
    # parser.add_argument('-gpu', type=bool, default=True, help='use gpu or not')
    args = parser.parse_args()
    print args.net

    if len(sys.argv) != 2:
        print "Usage: python OOP_circuit_simulator.py config.py"
        print "config.py must be in same directory as simulator"
    else:
        config_file_name = sys.argv[1][:-3]
        config_file = importlib.import_module(config_file_name)
        ckt = classes.Circuit(verilog_path=config_file.verilog_netlist_dir, config=config_file)
        ckt.read_netlist()
        ckt.levelize()
        ckt.set_caps()
        ckt.init_ckt()
        ckt.simulate_signal()
        # pdb.set_trace()
        # main(sys.argv[1][:-3]) # -3 to strip out ".py"







