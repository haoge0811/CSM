* Eda Yan
* USC - SPORT LAB
.option NOMOD
.global vdd
.temp 25.0
.param vdd=0.7

.include '../modelfiles/PTM_MG/lstp/7nm_LSTP.pm'


vhi hi 0 vdd
vlo lo 0 0

NAND2_1  hi  0  N1 N3    N10    NAND2
NAND2_2  hi  0  N3 N6    N11    NAND2
NAND2_3  hi  0  N2 N11    N16    NAND2
NAND2_4  hi  0  N11 N7    N19    NAND2
NAND2_5  hi  0  N10 N16    N22    NAND2
NAND2_6  hi  0  N16 N19    N23    NAND2

* extra load at final output
cL1 N22 0 1e-16
cL1 N23 0 1e-16

* input signals
VN1 N1 0 0.7
VN2 N2 0 0.0
VN3 N3 0 0.7
VN7 N7 0 pwl 0ps 0 5p 0 50.0p 0.7 150.0p 0.7
VN6 N6 0 pwl 0ps 0.7 20.0p 0.7 30.0p 0 150.0p 0


.tran 10.0f 150.0p
.op
.print v(N1) v(N2) v(N3) v(N7) v(N6) v(N22) v(N23) 
.end