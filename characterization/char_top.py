# Author: haoge <haoge@usc.edu> at USC SPORT Lab

# this file shows another method of calling the characterisation tool. i.e. import as python module

import characterisation

#characterisation.main("INV", 0.05, "../modelfiles/PTM_MG/hp/7nm_HP.pm", 0.7, 25.0)
#characterisation.main("NAND2", 0.05, "../modelfiles/PTM_MG/hp/7nm_HP.pm", 0.7, 25.0)
#characterisation.main("NOR2", 0.05, "../modelfiles/PTM_MG/hp/7nm_HP.pm", 0.7, 25.0)

#characterisation.main("INV", 0.05, "../modelfiles/PTM_MG/lstp/7nm_LSTP.pm", 0.7, 25.0)
characterisation.main("NAND2", 0.05, "../modelfiles/PTM_MG/lstp/7nm_LSTP.pm", 0.7, 25.0)
#characterisation.main("NOR2", 0.05, "../modelfiles/PTM_MG/lstp/7nm_LSTP.pm", 0.7, 25.0)