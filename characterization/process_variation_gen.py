# text session just for info storage



def gen_var(base_lib_dir, variation_1, variation_2, output_lib_dir):
    # read base(nominal) library, substitite needed parameters using variation 1, 2 or however many we want
    generate_from_template(template_directory = base_lib_dir,
                           output_directory   = output_lib_dir,
                           replace = {"$$P_name": "exp",
                                      "$$var1": variation_1,
                                      "$$var2": variation_2})



    # call the characterisation tool with the modified library
    # Note: characterisation tool name the output LUT automatically. the only identifier for process variation is
    # written in library file under the vth_multiplier varible. you can give this variable any name to denote a
    # unique corner.
    characterisation.main("INV", 0.05, output_lib_dir, 0.7, 25.0)
    # output name will be
    # FINFET_7nm_HP_INV_VL-0.14_VH0.84_VSTEP0.1_Pexp_V0.7_T25.0
    # note the "Pexp" session denotes this is the experimental LUT for process variation

    # write a config file for simulation. KEEP IT THE SAME FORMAT AS BEFORE.
    # run the config file with our simulator using the newly created process corner LUT.
    # job done.


# if running stand alone
if __name__ == '__main__':
    import argparse
    # use argparser here if wanted.