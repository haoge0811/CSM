# considering what Saeed suggested last week, 
# i think the best way to achieve "all in one" style control and auto run, 
# while still keep the locality and modularity of the code
# is to write a very top level wrapper file. that controls and calls all the sub-module

# according to Saeed's envision, it should

# job 1. 
# call OOP_circuit_simulator in simulation folder
# could be os.sys("python OOP_circuit_simulator config.py")

# job 2.
# translate CSM_config file to spice .sp file
# call CSM OOP_simulator and run it, call spice and run equivalent.


# job 3
# compare them (maybe use auto plotter)


# extra possible function
# before job1, let's say job 0
# this wrapper file check the OOP_circuit_simulator config.py file, see if the LUT
# user asks exist, if not, call characterisaion tool to create it.