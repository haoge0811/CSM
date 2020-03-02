Introduction and structure of codes:
The CSM simulator has 2 main parts, characterisation and simulation.

The CSM model of standard gates needs to be created before CSM simulation can be run.
Further explanation about CSM: [link to paper]

When user opens the CSM package, there will be 4 folders.
1. characterisation -- the section that creates CSM models in the form of Look-Up-Table (LUT) or Neuron-Network (NN)
2. LUT_bin -- where characterised CSM model (LUT and NN) is stored
3. modelfiles -- spice model libraries, we use PTM in our case
4. simulation -- the tool that perform circuit simulation using CSM models (LUT and NN) created

Explanation and usage:
1. characterisation



2. LUT_bin
This folder serves as a inventory of all the created CSM models, whether in the form of LUT or NN. It is the only
connection between the characterisation part and simulation part of the tool.
Note that LUT and NN are in the form of python pickle dump file.

3. modelfiles
This folder does not directly interact with user, it is used by characterisation process, and can be used for equivalent
spice simulation to verify the accuracy of CSM.

4. simulation