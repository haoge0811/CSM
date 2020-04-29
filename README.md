
## Current Source Model (CSM) Circuit Simulation and Neural Network Accelerator Platform (CSM-NN \& NN-PARS)
*Curent surce models* (CSMs) use voltage-dependent current sources and possibly voltage-dependent capacitances to model logic cells. In addition to higher accuracy, another advantage of CSM over voltage based look up table (LUT) models is the ability to simulate realistic waveforms for arbitrary input signals and provide the output waveforms. The main disadvantage of using CSM in simulation of circuits is high latency of CSM-parameter retrieval from memory. 

This platform is the result of our research on accelerating CSM circuit simulation taking advantage of NNs and GPU parallel computation. 

## Developers and Affiliation: <br />
The package was developed as a research project at <cite>[**The System Power Optimization and Regulation Technology (SPORT) Lab**][1]</cite> of University of Southern California (USC). <br />


**Lead PhD student:** <br />
<cite>[M. Saeed Abrishami][10]</cite>  <br />

**Graduate Students:** *(equal contribution)* <br /> 
Hao Ge <cite>[Linkedin][13]</cite>  <br />
Eda YAn <cite>[LinkedIn][14]</cite><br />

**Advisors:** <br />
<cite>[Prof. Massoud Pedram][11]</cite>  <br />
<cite>[Prof. Shahin Nazarian][12]</cite>  <br />


**Affiliation:** <br />


**Publication:** <br />
<cite>[NN-PARS: A Parallelized Neural Network Based Circuit Simulation Framework, ISQED 2020][3]</cite>  <br />
<cite>[CSM-NN: Current Source Model Based Logic Circuit Simulation - A Neural Network Approach, ICCD 2019][2]</cite>  <br />
<cite>[Accurate Timing and Noise Analysis of Combinational and Sequential Logic Cells Using CSMs, TVLSI 2011][4]</cite><br />
<cite>[A Current-based Method for Short Circuit Power Calculation under Noisy Input Waveforms, ASP-DAC 2007][5]</cite> <br />
<cite>[Statistical logic cell delay analysis using a current-based model, DAC 2006][6]</cite>  <br />

[1]: http://sportlab.usc.edu/ 
[2]: https://arxiv.org/abs/2002.05291
[3]: https://arxiv.org/abs/2002.05292
[4]: https://ieeexplore.ieee.org/abstract/document/5393095
[5]: https://ieeexplore.ieee.org/abstract/document/4196129
[6]: https://dl.acm.org/doi/abs/10.1145/1146909.1146975

## General notes and software requirements
- The CSM model of standard gates needs to be created before CSM simulation can be run.
- Further explanation about CSM: [link to paper]
- python 2.7 is used for this project. 
- H-SPICE (Synopsys) used for circuit simulation. 
- Characterisation part can only be run on a linux machine with H-SPICE installed. 
- CSM-simulation does not require SPICe and can run on any machine with python2. 
- Circuit netlist need to be in verilog format, and currently the tool only supports INV, NAND2, NOR2 gates.
- Machine learning package *scikit-learn* is required for NN models.

The CSM package includes 5 directories.
- *characterisation*: the section that creates CSM models in the form of Look-Up-Table (LUT) or NN models. 
- *simulation_spice*: a wrapper around spice engine synced with CSM simulation configuration. 
- *simulation_csm*: CSM simulator
- *data*: device libraries and spice templates current source models of different standard cell libraries. 
- *wrapper*: a simple wrapper to generate results, make comparisons and visualization between different models and technologies. 


## Package functionality
### Characterisation

There are 2 ways to call the characterisation tool: 
    
Use the script with arguments (see *shell_command.sh* for example):

    ```sh
    python characterisation.py --gate_name NAND2 --VSTEP 0.05 \
    --LIB_DIR ../modelfiles/PTM_MG/lstp/7nm_LSTP.pm --VDD 0.7 --TEMPERATURE 25"
    ```
    
Or, import the characterisation.py as a module in a top level python file, then use the script below (see *char_top.py* for example): 

    ```sh
    characterisation.main("NAND2", 0.05, "../modelfiles/PTM_MG/lstp/7nm_LSTP.pm", 0.7, 25.0)
    ```

Explanation: 
The characterisation tool create CSM models (LUT) according to user's configuration
input: gate name, resolution of LUT (VSTEP), spice library to use, VDD, temperature
output: CSM model (LUT)
There is another config.py file in the characterisation folder, that is used to change some relatively
non-changing variables. e.g. extra saving options.

During characterisation process, a series of DC and trasient spice simulations were performed on the
gate in question, to record the it's characteristic under different situations, hence creating the
CSM LUT. See reference papers for more details.

Note: the current version of the tool only supports single or two input gates (INV, NAND2, NOR2).

### CSM simulation
There are 2 ways to call the simulation tool: 

    ```sh
    python simulator.py config.py
    ```
    
Or, import the characterisation.py as a module in a top level python file and the use:

    ```sh
    simulator.main("config.py")
    ```

Note: the config file name is arbitrary. 

Explanation: 
The simulation tool uses the CSM model created in previous step to simulate a circuit in gate level.
It does simulation by solving differential equations for the gate in question, using components values
retrieved from LUT.

The config.py file very much like spice .sp file, describes the simulation setup, then the simulation
tool can be called to simulate this setup as described above. User can create many config file ahead 
of time, then call them in a shell script, just as H-spice.
The output of voltage nodes is saved in csv format.

### Spice simulation
The SpiceSim is a class so user should first initialize it and call simulate_hspice() function of it to run the hspice simulation,
For example: 

    ```sh
    ss = SpiceSim("config")
    ss.simulate_hspice()
    ```

Note: the ss and config file name is arbitrary. 

Explanation: 
The SpiceSim first reads out verilog circuit which is chosen by user by modify the CKT variable in config file, 
then it gets the simulation conditions, simulation parameters like tran-time, etc. Also technology and library model is setup.
Output loads and input signals set for simulation from config file and generate spice file with suffix .sp.
    
The SpiceSim also calls verilog2spice function, which is converting verilog format netlist into spice format netlist, 
and return the final outputs of the circuit to make it convenient to add capacitances on them.
    
The config.py file for SpiceSim is same with that for CSM simulation
The output of Hspice simulation is saved in output folder with .out suffix.

### Esim (similarity calculation tool)
The Esim is to calculate the similarity between results of spice and CSM simulation. It is a class so user can call it like this:

    ```sh
    es = Esim("config")
    es.data_extract()
    es.Esim_calculate()
    ```

Note: the es and config file name is arbitrary. 

Explanation: 
The Esim first reads the .out file of spice and extract the data part of it and writes into .wv file by 
function data_extract(), then by calling function Esim_calculate(), it will print out the similarity for
each output nodes between spice and CSM.
    
There is another function called Esim_calculate_without_config(self, wv_1, wv_2, vdd). It can calculate
Esim without config file, given two waveform file and vdd.
    
The config.py file for Esim is same with that for CSM and spice simulation
The output of Hspice simulation is saved in output folder with .out suffix.

### Look Up Tables (LUTs)
User does NOT interact with this folder.
This folder serves as a inventory of all the created CSM models, whether in the form of LUT or NN.
It is the only connection between the characterisation part and simulation part of the tool.
Note that LUT and NN are in the form of python pickle dump file.
There will be a human_readable_LUT folder, if user choose to create it in the characterisation config.py file. In this file, data of LUT will be stored in format that can be imported to Excel.
It can be used for debugging purpose.

### Semiconductor models and technologies: 
User does NOT interact with this folder.
It is used by characterisation process, and can be used for equivalent spice simulation to verify the accuracy of CSM.
The models available on this repo are from <cite>[Arizona State University (ASU) Predictive Technology Model (PTM)][7]</cite>. <br />

[7]: http://ptm.asu.edu/

## TODO list (assigned on April 21st):
- we need to have separate files for functions and classes, 
- Signal is a class for itself, separate it for now in a single file
- simulation-csm and simulation-spice should not be our main
