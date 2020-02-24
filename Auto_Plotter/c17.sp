* c17.v spice version created using Eda's tool.
* then manually tweaked by Hao Ge to add input/output condition

.option NOMOD
.global vdd 
.temp 25
.param vdd=0.7

.include './7nm_LSTP.pm'



.subckt NAND2 hi lo in1 in2 out
mp2 (out in2 hi hi) pfet nfin=1.0 l=1.1e-08 
mp1 (out in1 hi hi) pfet nfin=1.0 l=1.1e-08 
mn1 (out in1 n1 lo) nfet nfin=1.0 l=1.1e-08
mn2 (n1  in2 lo lo) nfet nfin=1.0 l=1.1e-08
.ends NAND2


vhi hi 0 vdd
vlo lo 0 0

X0   hi    lo    N1 N3        N10        NAND2
X1    hi    lo    N3 N6        N11        NAND2
X2    hi    lo    N2 N11        N16        NAND2
X3    hi    lo    N11 N7        N19        NAND2
X4    hi    lo    N10 N16        N22        NAND2
X5    hi    lo    N16 N19        N23        NAND2




* input signals
*PULSE (0 vdd 5e-12 50e-12 50e-12 10ns 20ns )
VN1 N1 0     DC vdd
VN2 N2 0     DC 0
VN3 N3 0     DC vdd
VN6 N6 0     DC 0
VN7 N7 0     PULSE (0 vdd 5e-12 50e-12 50e-12 100ns 200ns )


* initial conditions
*.ic N10 0
*.ic N11 0
*.ic N16 0
*.ic N19 0

*.ic N22 0
*.ic N23 0


* added capacitance at final output
cL0 N22 0 1e-16
cL1 N23 0 1e-16

.tran 0.01p 300p
.print v(N22) v(N23)
.end

