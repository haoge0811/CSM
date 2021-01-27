# Author: haoge <haoge@usc.edu> at USC SPORT Lab

# this file shows another method of calling the characterisation tool. i.e. import as python module
'''
import characterisation

#characterisation.main("INV", 0.05, "../modelfiles/PTM_MG/hp/7nm_HP.pm", 0.7, 25.0)
#characterisation.main("NAND2", 0.05, "../modelfiles/PTM_MG/hp/7nm_HP.pm", 0.7, 25.0)
#characterisation.main("NOR2", 0.05, "../modelfiles/PTM_MG/hp/7nm_HP.pm", 0.7, 25.0)

#characterisation.main("INV", 0.05, "../modelfiles/PTM_MG/lstp/7nm_LSTP.pm", 0.7, 25.0)
characterisation.main("NAND2", 0.05, "../modelfiles/PTM_MG/lstp/7nm_LSTP.pm", 0.7, 25.0)
#characterisation.main("NOR2", 0.05, "../modelfiles/PTM_MG/lstp/7nm_LSTP.pm", 0.7, 25.0)
'''
# import char_with_integrate_PVT

# char_with_integrate_PVT.main("INV", 0.05, "../data/modelfiles/PTM_MG/lstp/7nm_LSTP.pm", 0.5, 0.9, 0.05, -25.0, 125.0, 25.0)
#char_with_integrate_PVT.main("NAND2", 0.05, "../data/modelfiles/PTM_MG/lstp/7nm_LSTP.pm", 0.5, 0.9, 0.05, -25.0, 125.0, 25.0)
#char_with_integrate_PVT.main("NOR2", 0.05, "../data/modelfiles/PTM_MG/lstp/7nm_LSTP.pm", 0.5, 0.9, 0.05, -25.0, 125.0, 25.0)

import characterisation

characterisation.main("INV", 0.05, "../data/modelfiles/PTM_MOSFET/16nm_HP.pm", 0.7, -25.0)
characterisation.main("INV", 0.05, "../data/modelfiles/PTM_MOSFET/16nm_HP.pm", 0.7, 0.0)
characterisation.main("INV", 0.05, "../data/modelfiles/PTM_MOSFET/16nm_HP.pm", 0.7, 25.0)
characterisation.main("INV", 0.05, "../data/modelfiles/PTM_MOSFET/16nm_HP.pm", 0.7, 50.0)
characterisation.main("INV", 0.05, "../data/modelfiles/PTM_MOSFET/16nm_HP.pm", 0.7, 75.0)
characterisation.main("INV", 0.05, "../data/modelfiles/PTM_MOSFET/16nm_HP.pm", 0.7, 100.0)