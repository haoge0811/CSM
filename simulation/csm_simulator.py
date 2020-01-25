# Author: haoge <haoge@usc.edu> at USC SPORT Lab

from functions import *

# actual csm simulation. differential equations
def csm_simulate(GATE_NAME, LUT_and_boundary, signal, initial_conditions, outfile, CL,  t_step, t_tot):
    csm_outfile = open(outfile, "w") # write csm output(result) to a file

    if (GATE_NAME == "INV"):
        print "t_ps\tVin_csm\tVout_csm\t"
        csm_outfile.write("#time Vin_csm Vout_csm\n")

        for step_number in range(int(t_tot / t_step)):
            t = step_number * t_step
            t_ps = t * 1e12  # just for readability

            # initial condition at time step 0
            if (step_number == 0):
                Vin = signal.get_val(0)
                Vout = initial_conditions["Vout"]

                print t_ps, "\t", np.round(Vin,6), "\t", np.round(Vout,6), "\t"
                csm_outfile.write(str(t) + " " + str(np.round(Vin, 6)) + " " + str(np.round(Vout, 6)) + "\n")

            # actual simulation
            else:
                d_Vin = signal.get_val(t) - Vin
                Vin = signal.get_val(t)

                # interpolation
                r = read_LUT(LUT_and_boundary = LUT_and_boundary,
                             GATE_NAME = GATE_NAME,
                             voltages_now = {"Vin": Vin, "Vout": Vout})

                # the actual diffrential equation for circuit simulation, plus minus sign checked.
                # diff eq for INV
                d_Vout = (r["CM"] * d_Vin - r["I_out_DC"] * t_step) / (CL + r["CO"] + r["CM"])
                Vout += d_Vout  # record and accumulate

                # now its the new value for this time step
                print t_ps, "\t", np.round(Vin,6), "\t", np.round(Vout,6), "\t"
                csm_outfile.write(str(t) + " " + str(np.round(Vin, 6)) + " " + str(np.round(Vout, 6)) + "\n")

    elif (GATE_NAME == "NAND2") or (GATE_NAME == "NOR2"):
        signal_1 = signal["Vna"]
        signal_2 = signal["Vnb"]
        print "t_ps\t Vna_csm\t Vnb_csm\t Vn1_csm\t Vout_csm\t"
        csm_outfile.write("#time Vna_csm Vnb_csm Vn1_csm Vout_csm\n")

        for step_number in range(int(t_tot / t_step)):
            t = step_number * t_step
            t_ps = t * 1e12  # just for readability

            if (step_number == 0):
                Vna = signal_1.get_val(0)
                Vnb = signal_2.get_val(0)
                Vn1 = initial_conditions["Vn1"]
                Vout = initial_conditions["Vout"]

                print t_ps, "\t", np.round(Vna,6), "\t", np.round(Vnb,6), "\t", np.round(Vn1,6), "\t", np.round(Vout,6), "\t"
                csm_outfile.write(str(t) + " " + str(np.round(Vna, 6)) + " " + str(np.round(Vnb, 6)) + " " + str(
                    np.round(Vn1, 6)) + " " + str(np.round(Vout, 6)) + "\n")

            else:
                d_Vna = signal_1.get_val(t) - Vna
                Vna = signal_1.get_val(t)

                d_Vnb = signal_2.get_val(t) - Vnb
                Vnb = signal_2.get_val(t)

                # interpolation LUT to retrive value
                r = read_LUT(LUT_and_boundary = LUT_and_boundary,
                             GATE_NAME = GATE_NAME,
                             voltages_now = {"Vna": Vna, "Vnb": Vnb, "Vn1": Vn1, "Vout": Vout})

                # the actual diffrential equation for circuit simulation, plus minus sign checked.
                # 1
                d_Vout = (r["CM_A"] * d_Vna + r["CM_B"] * d_Vnb - r["I_out_DC"] * t_step) / (
                            CL + r["CO"] + r["CM_A"] + r["CM_B"])
                # 2
                d_Vn1 = ((-r["I_inter_DC"]) * t_step) / r["CINT"]

                Vout += d_Vout  # record and accumulate
                Vn1 += d_Vn1

                # its update value for current time step now
                print t_ps, "\t", np.round(Vna,6), "\t", np.round(Vnb,6), "\t", np.round(Vn1,6), "\t", np.round(Vout,6), "\t"
                # print ("\n DEBUG CM_A=%s, d_Vna=%s CM_B=%s, d_Vnb=%s, I_out_DC=%s, CO=%s ..... CINT=%s, I_inter_DC=%s" % (str(r["CM_A"]), str(d_Vna), str(r["CM_B"]), str(d_Vnb), str(r["I_out_DC"]), str(r["CO"]), str(r["CINT"]), str(r["I_inter_DC"])  ))
                csm_outfile.write(str(t) + " " + str(np.round(Vna, 6)) + " " + str(np.round(Vnb, 6)) + " " + str(
                    np.round(Vn1, 6)) + " " + str(np.round(Vout, 6)) + "\n")

    else:
        print "Cannot do csm simulation, Invalid or not yet implemented gate name."
    csm_outfile.close()


# CSM simulator NN version (this is a container or a wrapper for saeed's NN, so it fits nicely with existing code)
def csm_simulate_NN(GATE_NAME, NN_model, LUT_and_boundary, signal, initial_conditions, outfile, CL,  t_step, t_tot):
    csm_outfile = open(outfile, "w") # write csm output(result) to a file

    if (GATE_NAME == "INV"):
        print "t_ps\tVin_csm\tVout_csm\t"
        csm_outfile.write("#time Vin_csm Vout_csm\n")

        for step_number in range(int(t_tot / t_step)):
            t = step_number * t_step
            t_ps = t * 1e12  # just for readability

            # initial condition at time step 0
            if (step_number == 0):
                Vin = signal.get_val(0)
                Vout = initial_conditions["Vout"]

                print t_ps, "\t", np.round(Vin,6), "\t", np.round(Vout,6), "\t"
                csm_outfile.write(str(t) + " " + str(np.round(Vin, 6)) + " " + str(np.round(Vout, 6)) + "\n")

            # actual simulation
            else:
                d_Vin = signal.get_val(t) - Vin
                Vin = signal.get_val(t)

                # interpolation, still read LUT for all values other than current.
                r = read_LUT(LUT_and_boundary = LUT_and_boundary,
                             GATE_NAME = GATE_NAME,
                             voltages_now = {"Vin": Vin, "Vout": Vout})


                # this is where NN differs from LUT
                # here instead read_LUT, we ask_NN
                XX = np.ndarray((1, 2))
                XX[0, 0] = Vin
                XX[0, 1] = Vout
                NN_result = (NN_model["reg"].predict(XX)[0]*NN_model["std"])+NN_model["mean"]
                # we are going to overwrite the  I_out_DC field of LUT reading with NN reading.
                # later on, we probably do it all with NN
                r["I_out_DC"] = NN_result



                # the actual diffrential equation for circuit simulation, plus minus sign checked.
                # diff eq for INV
                d_Vout = (r["CM"] * d_Vin - r["I_out_DC"] * t_step) / (CL + r["CO"] + r["CM"])
                Vout += d_Vout  # record and accumulate

                # now its the new value for this time step
                print t_ps, "\t", np.round(Vin,6), "\t", np.round(Vout,6), "\t"
                csm_outfile.write(str(t) + " " + str(np.round(Vin, 6)) + " " + str(np.round(Vout, 6)) + "\n")

    elif (GATE_NAME == "NAND2") or (GATE_NAME == "NOR2"):
        signal_1 = signal["Vna"]
        signal_2 = signal["Vnb"]
        print "t_ps\t Vna_csm\t Vnb_csm\t Vn1_csm\t Vout_csm\t"
        csm_outfile.write("#time Vna_csm Vnb_csm Vn1_csm Vout_csm\n")

        for step_number in range(int(t_tot / t_step)):
            t = step_number * t_step
            t_ps = t * 1e12  # just for readability

            if (step_number == 0):
                Vna = signal_1.get_val(0)
                Vnb = signal_2.get_val(0)
                Vn1 = initial_conditions["Vn1"]
                Vout = initial_conditions["Vout"]

                print t_ps, "\t", np.round(Vna,6), "\t", np.round(Vnb,6), "\t", np.round(Vn1,6), "\t", np.round(Vout,6), "\t"
                csm_outfile.write(str(t) + " " + str(np.round(Vna, 6)) + " " + str(np.round(Vnb, 6)) + " " + str(
                    np.round(Vn1, 6)) + " " + str(np.round(Vout, 6)) + "\n")

            else:
                d_Vna = signal_1.get_val(t) - Vna
                Vna = signal_1.get_val(t)

                d_Vnb = signal_2.get_val(t) - Vnb
                Vnb = signal_2.get_val(t)

                # interpolation LUT to retrive value
                r = read_LUT(LUT_and_boundary = LUT_and_boundary,
                             GATE_NAME = GATE_NAME,
                             voltages_now = {"Vna": Vna, "Vnb": Vnb, "Vn1": Vn1, "Vout": Vout})



                # this is where NN differs from LUT
                # here instead read_LUT, we ask_NN
                # The order is: [Vna, Vnb, Vn1, Vout]
                XX = np.ndarray((1, 4))
                XX[0, 0] = Vna
                XX[0, 1] = Vnb
                XX[0, 2] = Vn1
                XX[0, 3] = Vout
                NN_result = (NN_model["reg"].predict(XX)[0]*NN_model["std"])+NN_model["mean"]
                # we are going to overwrite the  I_out_DC field of LUT reading with NN reading.
                # later on, we probably do it all with NN
                r["I_out_DC"] = NN_result



                # the actual diffrential equation for circuit simulation, plus minus sign checked.
                # 1
                d_Vout = (r["CM_A"] * d_Vna + r["CM_B"] * d_Vnb - r["I_out_DC"] * t_step) / (
                            CL + r["CO"] + r["CM_A"] + r["CM_B"])
                # 2
                d_Vn1 = ((-r["I_inter_DC"]) * t_step) / r["CINT"]

                Vout += d_Vout  # record and accumulate
                Vn1 += d_Vn1

                # its update value for current time step now
                print t_ps, "\t", np.round(Vna,6), "\t", np.round(Vnb,6), "\t", np.round(Vn1,6), "\t", np.round(Vout,6), "\t"
                # print ("\n DEBUG CM_A=%s, d_Vna=%s CM_B=%s, d_Vnb=%s, I_out_DC=%s, CO=%s ..... CINT=%s, I_inter_DC=%s" % (str(r["CM_A"]), str(d_Vna), str(r["CM_B"]), str(d_Vnb), str(r["I_out_DC"]), str(r["CO"]), str(r["CINT"]), str(r["I_inter_DC"])  ))
                csm_outfile.write(str(t) + " " + str(np.round(Vna, 6)) + " " + str(np.round(Vnb, 6)) + " " + str(
                    np.round(Vn1, 6)) + " " + str(np.round(Vout, 6)) + "\n")

    else:
        print "Cannot do csm simulation, Invalid or not yet implemented gate name."
    csm_outfile.close()