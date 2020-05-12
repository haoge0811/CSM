.include '/home/home2/visiting/mitsushij/workspace/CSM/simulation/../data/modelfiles/PTM_MOSFET/16nm_LP.pm'

.subckt INV hi lo in out
mp1 (out in hi hi)  pmos w=3.2e-08     l=1.6e-08 
mn1 (out in lo lo)  nmos w=1.6e-08     l=1.6e-08
.ends INV

.subckt NOR2 hi lo in1 in2 out
mp2 (n1  in2 hi hi) pmos w='2*3.2e-08' l=1.6e-08
mp1 (out in1 n1 hi) pmos w='2*3.2e-08' l=1.6e-08
mn1 (out in1 lo lo) nmos w=1.6e-08     l=1.6e-08
mn2 (out in2 lo lo) nmos w=1.6e-08     l=1.6e-08
.ends NOR2

.subckt NAND2 hi lo in1 in2 out
mp2 (out in2 hi hi) pmos w=3.2e-08     l=1.6e-08
mp1 (out in1 hi hi) pmos w=3.2e-08     l=1.6e-08
mn1 (out in1 n1 lo) nmos w='2*1.6e-08' l=1.6e-08
mn2 (n1  in2 lo lo) nmos w='2*1.6e-08' l=1.6e-08
.ends NAND2

