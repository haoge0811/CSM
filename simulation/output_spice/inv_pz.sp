* Eda Yan
* USC - SPORT LAB
.option NOMOD
.global vdd
.param vdd=0.9
.include './gate_inventory_gen.sp'


vhi hi 0 vdd
vlo lo 0 0

XNOT1_1  hi  0  N1    N2    NOT1

* extra load at final output
cL1 N2 0 1e-16

* input signals
VN1 N1 0 pulse(0 0.7 1p 20.0p 20.0p 0.5e-09 1e-09)

* finding zeros and poles
.PZ N2 N1

.tran 1p 1e-09
.op
.print v(N2)
.end