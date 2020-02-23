.include 'C:\Users\GE\Desktop\USC\CSM\pycharm\CSM_dev\characterisation/../modelfiles/PTM_MG/lstp/7nm_LSTP.pm'

.subckt INV hi lo in out 
mp1 (out in hi hi)  pfet nfin=1.0 l=1.1e-08  
mn1 (out in lo lo)  nfet nfin=1.0 l=1.1e-08  
.ends INV

.subckt NOR2 hi lo in1 in2 n1 out
mp2 (n1  in2 hi hi) pfet nfin=1.0 l=1.1e-08 
mp1 (out in1 n1 hi) pfet nfin=1.0 l=1.1e-08 
mn1 (out in1 lo lo) nfet nfin=1.0 l=1.1e-08
mn2 (out in2 lo lo) nfet nfin=1.0 l=1.1e-08
.ends NOR2

.subckt NAND2 hi lo in1 in2 n1 out
mp2 (out in2 hi hi) pfet nfin=1.0 l=1.1e-08 
mp1 (out in1 hi hi) pfet nfin=1.0 l=1.1e-08 
mn1 (out in1 n1 lo) nfet nfin=1.0 l=1.1e-08
mn2 (n1  in2 lo lo) nfet nfin=1.0 l=1.1e-08
.ends NAND2

