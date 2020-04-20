.include '$$library'

.subckt INV hi lo in out 
mp1 (out in hi hi)  pfet nfin=$$nfin l=$$lg_p  
mn1 (out in lo lo)  nfet nfin=$$nfin l=$$lg_n  
.ends INV

.subckt NOR2 hi lo in1 in2 n1 out
mp2 (n1  in2 hi hi) pfet nfin=$$nfin l=$$lg_p 
mp1 (out in1 n1 hi) pfet nfin=$$nfin l=$$lg_p 
mn1 (out in1 lo lo) nfet nfin=$$nfin l=$$lg_n
mn2 (out in2 lo lo) nfet nfin=$$nfin l=$$lg_n
.ends NOR2

.subckt NAND2 hi lo in1 in2 n1 out
mp2 (out in2 hi hi) pfet nfin=$$nfin l=$$lg_p 
mp1 (out in1 hi hi) pfet nfin=$$nfin l=$$lg_p 
mn1 (out in1 n1 lo) nfet nfin=$$nfin l=$$lg_n
mn2 (n1  in2 lo lo) nfet nfin=$$nfin l=$$lg_n
.ends NAND2

