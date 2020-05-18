* Eda Yan
* USC - SPORT LAB
.option NOMOD
.global vdd
.param vdd=0.7
.include './gate_inventory_gen.sp'


vhi hi 0 vdd
vlo lo 0 0

XNOT1_1  hi  0  N1    N2    NOT1

* extra load at final output
cL1 N2 0 1e-16

* input signals
VN1 N1 0 pwl 0ps 0 10.0p 0 50.0p 0.7 100.0p 0.7


.tran 100.0f 100.0p
.op
.print v(N2) 
.end