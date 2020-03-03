# Writing in progress

## Introduction and structure of program:
    The CSM simulator has 2 main parts, characterisation and simulation.

    The CSM model of standard gates needs to be created before CSM simulation can be run.
    Further explanation about CSM: [link to paper]
    Note: python 2.7 is used for this project. require package ........ Characterisation part can only be run on a
    linux machine with H-SPICE installed. simulation part can be run on any machine with Python installed.

    When user opens the CSM package, there will be 4 folders.
        1. characterisation -- the section that creates CSM models in the form of Look-Up-Table (LUT)
            or Neuron-Network (NN)
        2. LUT_bin -- where characterised CSM model (LUT and NN) is stored
        3. modelfiles -- spice model libraries, we use PTM in our case
        4. simulation -- the tool that perform circuit simulation using CSM models (LUT and NN) created

    Some additional files:
        Wrapper -- provided example wrapper (or shell) to operate the tool from top level

## Explanation and usage:
    1. characterisation
        usage: there are 2 ways to call the characterisation tool
            1. in linux command line type e.g: "python characterisation.py --gate_name NAND2 --VSTEP 0.05 \
            --LIB_DIR ../modelfiles/PTM_MG/lstp/7nm_LSTP.pm --VDD 0.7 --TEMPERATURE 25"
            see shell_command.sh for example
            2. import the characterisation.py as a module in a top level python file. then use
            characterisation.main("NAND2", 0.05, "../modelfiles/PTM_MG/lstp/7nm_LSTP.pm", 0.7, 25.0)
            see char_top.py for example

        the characterisation tool create CSM models (LUT) according to user's configuration
        input:
        output:


    2. LUT_bin
        This folder serves as a inventory of all the created CSM models, whether in the form of LUT or NN.
        It is the only connection between the characterisation part and simulation part of the tool.
        Note that LUT and NN are in the form of python pickle dump file.

    3. modelfiles
        This folder does not directly interact with user, it is used by characterisation process, and can be used
        for equivalent spice simulation to verify the accuracy of CSM.

    4. simulation