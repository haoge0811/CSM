
import pdb
import sys
import argparse
import importlib

import classes
from plot import *
from SpiceSim import *
from Esim import *
from func_spice import print_header

if __name__ == '__main__':
    print_header()
    '''
    if -func or -f == "csm": do csm simulation 
    if -func or -f == "spice": do spice simulation 
    if -func or -f == "esim-all": do csm-sim and spice-sim and report esim
    if -func or -f == "esim": calculate esim, given csm and spice waveforms
    
    if -plot == "1": plot and save waveform of CSM and Hspice into image folder
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('-func', type=str, required=True, help='Function')
    parser.add_argument('-conf', type=str, default="config.py", help='config file name')
    parser.add_argument('-plot', type=bool, default=False, help='plot flag')
    # parser.add_argument('-gpu', type=bool, default=True, help='use gpu or not')
    args = parser.parse_args()
    
    if args.func == "csm":
        conf = importlib.import_module(args.conf[:-3])
        v_path = conf.VERILOG_DIR + conf.CKT + ".v"
        ckt = classes.Circuit(verilog_path=v_path, config=conf)
        ckt.read_netlist()
        ckt.levelize()
        ckt.set_caps()
        ckt.init_ckt()
        ckt.simulate_signal()
    elif args.func == "spice":
        ss = SpiceSim(args.conf[:-3])
        ss.simulate_hspice()
    elif args.func == "esim":
        es = Esim(args.conf[:-3])
        es.data_extract()
        es.Esim_calculate()
    elif args.func == "esim-all":
        conf = importlib.import_module(args.conf[:-3])
        v_path = conf.VERILOG_DIR + conf.CKT + ".v"
        ckt = classes.Circuit(verilog_path=v_path, config=conf)
        ckt.read_netlist()
        ckt.levelize()
        ckt.set_caps()
        ckt.init_ckt()
        ckt.simulate_signal()
        ss = SpiceSim(args.conf[:-3])
        ss.simulate_hspice()
        es = Esim(args.conf[:-3])
        es.data_extract()
        es.Esim_calculate()
    elif args.func == "pass":
        pass
    else:
        print "function argument not found"

    if args.plot == True:
        es = Esim(args.conf[:-3])
        es.data_extract()
        pp = plot(args.conf[:-3])
        pp.auto_plot()

