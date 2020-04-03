# use this file to control and generate process variaiton for now.
# later let's integrate it into the "platform" (top level wrapper) if needed.

def gen_var(base_lib_dir, variation_1, variation_2, outptu_lib_dir):
    # read base(nominal) library, substitite needed parameters using variation 1, 2 or however many we want

    # generate output library. Pay attention to keep it the same format as before. So we REUSE all our previous code
    # without problem. there is no need to spend unnecessary energy there. Plus the risk of breaking already working code

    # call the characterisation tool with the modified library
    # Note: characterisation tool name the output LUT automatically. the only identifier for process variation is
    # written in library file under the vth_multiplier varible. you can give this variable any name to denote a
    # unique corner.

    # write a config file for simulation. KEEP IT THE SAME FORMAT AS BEFORE.
    # run the config file with our simulator using the newly created process corner LUT.
    # job done.


# if running stand alone
if __name__ == '__main__':
    import argparse
    # use argparser here if wanted.