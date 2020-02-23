* M. Saeed Abrishami
* USC - SPORT LAB
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

X0 hi 0	A	B	1	    NAND2
X1 hi 0	A	1   2	    NAND2
X2 hi 0	1	B	3	    NAND2
X3 hi 0	2	3	4	    NAND2
X4 hi 0 4	Cin	5 	    NAND2
X5 hi 0	4	5	6	    NAND2
X6 hi 0	5	Cin	7	    NAND2
X7 hi 0	5	1	Cout	NAND2
X8 hi 0	6	7	S	    NAND2

* dummy NAND at the end for loading
Xdumb1 hi 0 S    hi netd1 NAND2
Xdumb2 hi 0 Cout hi netd2 NAND2

* extra load at each net
cL1 1 0 1e-15
cL2 2 0 1e-15
cL3 3 0 1e-15
cL4 4 0 1e-15
cL5 5 0 1e-15
cL6 6 0 1e-15
cL7 7 0 1e-15
cL8 S 0 1e-15
cL9 Cout 0 1e-15

VA A 0     PULSE (0 vdd 5e-12 50e-12 50e-12 10ns 20ns )
VB B 0     PULSE (0 vdd 5e-12 50e-12 50e-12 10ns 20ns )
VCin Cin 0 PULSE (vdd 0 5e-12 50e-12 50e-12 10ns 20ns )

* specify initila conditions
.ic 1 0
.ic 2 0
.ic 3 0
.ic 4 0
.ic 5 0
.ic 6 0
.ic 7 0
.ic S 0
.ic Cout 0
.ic netd1 0
.ic netd2 0




.tran 0.01p 300p
.op
.print v(S) v(Cout) v(1) v(2)
.end

