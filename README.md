

## Introduction and structure of program:
The CSM simulator has 2 main parts, characterisation and simulation.

The CSM model of standard gates needs to be created before CSM simulation can be run.
Further explanation about CSM: [link to paper]
Note: python 2.7 is used for this project. require package ........ Characterisation part can only be run on a
linux machine with H-SPICE installed. simulation part can be run on any machine with Python installed.

When user opens the CSM package, there will be 4 folders.
- characterisation -- the section that creates CSM models in the form of Look-Up-Table (LUT)
    or Neuron-Network (NN)
- LUT_bin -- where characterised CSM model (LUT and NN) is stored
- modelfiles -- spice model libraries, we use PTM in our case
- simulation -- the tool that perform circuit simulation using CSM models (LUT and NN) created

Some additional files:
Wrapper -- provided example wrapper (or shell) to operate the tool from top level

## Explanation and usage:
- characterisation   
    **Usage: there are 2 ways to call the characterisation tool**
    - in linux command line type e.g: "python characterisation.py --gate_name NAND2 --VSTEP 0.05 \
    --LIB_DIR ../modelfiles/PTM_MG/lstp/7nm_LSTP.pm --VDD 0.7 --TEMPERATURE 25"
    see shell_command.sh for example
    - import the characterisation.py as a module in a top level python file. then use
    characterisation.main("NAND2", 0.05, "../modelfiles/PTM_MG/lstp/7nm_LSTP.pm", 0.7, 25.0)
    see char_top.py for example

    **Explanation**
    The characterisation tool create CSM models (LUT) according to user's configuration
    input: gate name, resolution of LUT (VSTEP), spice library to use, VDD, temperature
    output: CSM model (LUT)
    There is another config.py file in the characterisation folder, that is used to change some relatively
    non-changing variables. e.g. extra saving options.

    During characterisation process, a series of DC and trasient spice simulations were performed on the
    gate in question, to record the it's characteristic under different situations, hence creating the
    CSM LUT. See paper for more detail on this process [].

    Note: Currently the tool only supports INV, NAND2, NOR2 gates.


- LUT_bin  
    User does NOT interact with this folder.
    This folder serves as a inventory of all the created CSM models, whether in the form of LUT or NN.
    It is the only connection between the characterisation part and simulation part of the tool.
    Note that LUT and NN are in the form of python pickle dump file.
    There will be a human_readable_LUT folder, if user choose to create it in the characterisation 
    config.py file. In this file, data of LUT will be stored in format that can be imported to Excel.
    It can be used for debugging purpose.

- modelfiles  
    User does NOT interact with this folder.
    It is used by characterisation process, and can be used for equivalent spice simulation to verify the
    accuracy of CSM.

- simulation  
    **Usage: there are 2 ways to call the simulation tool**
    - in linux command line type e.g: "python OOP_circuit_simulator.py config.py"
    - import the characterisation.py as a module in a top level python file. then use
    OOP_circuit_simulator.main("config.py")   Note: use quotation marks aroud config.py
    Note: config.py can be any .py file written in compatiable format, does not need to literally be 
    called config.py. 

    **Explanation**
    The simulation tool uses the CSM model created in previous step to simulate a circuit in gate level.
    It does simulation by solving differential equations for the gate in question, using components values
    retrieved from LUT.
    The config.py file very much like spice .sp file, describes the simulation setup, then the simulation
    tool can be called to simulate this setup as described above. User can create many config file ahead 
    of time, then call them in a shell script, just as H-spice.
    The output of voltage nodes is saved in csv format.

    Note: input netlist need to be in verilog format, and currently the tool only supports INV, NAND2, 
    NOR2 gates.
