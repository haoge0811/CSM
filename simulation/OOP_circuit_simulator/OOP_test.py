class net:
    def __init__(self, initail_voltage):
        self.voltage = initail_voltage

class logic_gate:
    def __init__(self):
        self.attribute = 6


    def change_net_voltage(self, net_instance, new_voltage, dict):
        net_instance.voltage = new_voltage
        dict = new_voltage


# tring area
net0 = net(0)
random_input_variable = 5.5
'''
#dict = {"value" : 5, "another_value": 100}
print net0.voltage
#print random_input_variable

gate0 = logic_gate()
print gate0.attribute
gate0.change_net_voltage(net0,1.2, gate0.attribute)

print net0.voltage
#print random_input_variable
print gate0.attribute
'''
dict = dict()
gate0 = logic_gate()
gate1 = logic_gate()

dict["key"] = gate0

#print dict["key"]

gate1.something = gate0

#print gate1.something

gate1.something.attribute = 3

print gate0.attribute

gate0.attribute = 8

print gate1.something.attribute

list = [gate0, gate1]
print list[0].attribute

print gate0.attribute