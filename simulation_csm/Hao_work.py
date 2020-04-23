# Hao's addon works.
# you can copy the functions out and put where is suits.
import numpy as np


# needed by adaptive_interpolation
def get_interpolation_params(voltage, V_L, VSTEP):
    # since it's low_idx, we should use floor instead of round
    voltage_low_idx = int(np.floor((voltage - V_L) / VSTEP))
    voltage_low = voltage_low_idx * VSTEP + V_L  # floored voltage value to closest LUT stored voltage value

    # deviation factor for interpolation
    a_voltage = ((voltage - voltage_low) / VSTEP)
    return (voltage_low_idx, a_voltage)
# input LUT, coordinates at each dimension, (lowest_value, resolution) for each dimension.
# number of dimensions can vary, this function recognizes it and interpolate.
###################### IMPORTANT: USE ORDER DICT FOR coordiantes_dict ###################
def adaptive_interpolation(nd_array, coordiantes_dict):
    # coordiantes_dict structure as follows.
    # {"dimension_1": [coordinate_1, lowest_value, resolution],
    # "dimension_2": [coordinate_1, lowest_value, resolution]}
    processed_coordiantes= dict()
    for each_dimension in coordiantes_dict.keys():
        data = coordiantes_dict[each_dimension]
        (low_index, a_factor) = get_interpolation_params(data[0], data[1], data[2])
        processed_coordiantes[each_dimension] = [low_index, a_factor]
    # process complete


    # interpolation algorithm
    number_of_dimensions = len(processed_coordiantes.keys())
    # create 2 base array
    base_index = []
    base_a_factor = []
    for each_dimension in processed_coordiantes.keys():
        base_index.append(processed_coordiantes[each_dimension][0])
        base_a_factor.append(processed_coordiantes[each_dimension][1])
    # base arrays ready

    result = 0
    for corner_number in range(2**number_of_dimensions):
        binary_mask = format(corner_number, '0%db' % number_of_dimensions)

        index_list = [0] * number_of_dimensions # 2 arrays for this corner
        param_list = [0] * number_of_dimensions
        for i in range(len(base_index)):
            index_list[i] = base_index[i] + int(binary_mask[i]) # +2 to strip 0b pre fix
            if (int(binary_mask[i]) == 0):
                param_list[i] = (1 - base_a_factor[i])
            else:
                param_list[i] = base_a_factor[i]
        # corner arrays ready

        partial_val = nd_array
        for each_index in index_list:
            partial_val = partial_val[each_index]
        for each_param in param_list:
            partial_val = partial_val * each_param # cumulative multiplication

        result += partial_val

    return result