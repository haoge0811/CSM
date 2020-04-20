.include '$$library'

.subckt INV hi lo in out
mp1 (out in hi hi)  pmos w=$$w_p     l=$$lg_p 
mn1 (out in lo lo)  nmos w=$$w_n     l=$$lg_n
.ends INV

.subckt NOR2 hi lo in1 in2 n1 out
mp2 (n1  in2 hi hi) pmos w='2*$$w_p' l=$$lg_p
mp1 (out in1 n1 hi) pmos w='2*$$w_p' l=$$lg_p
mn1 (out in1 lo lo) nmos w=$$w_n     l=$$lg_n
mn2 (out in2 lo lo) nmos w=$$w_n     l=$$lg_n
.ends NOR2

.subckt NAND2 hi lo in1 in2 n1 out
mp2 (out in2 hi hi) pmos w=$$w_p     l=$$lg_p
mp1 (out in1 hi hi) pmos w=$$w_p     l=$$lg_p
mn1 (out in1 n1 lo) nmos w='2*$$w_n' l=$$lg_n
mn2 (n1  in2 lo lo) nmos w='2*$$w_n' l=$$lg_n
.ends NAND2

