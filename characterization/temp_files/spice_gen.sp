* Hao Ge <haoge@usc.edu>
* USC - SPORT LAB

.option NOMOD
.global vdd 
.temp 25.0
.param vdd=0.7

.include './gate_inventory_gen.sp'
.include './sweep_table.inc'

vhi hi 0 vdd
vlo lo 0 0
X0 hi lo nA nB n1 out NAND2

VA   nA  0 DC=sweep_VA
VB   nB  0 DC=sweep_VB 
Vn1  n1  0 DC=sweep_Vn1
Vout out 0 DC=sweep_Vout

.dc SWEEP DATA=sweep_DC
.print v(nA) v(nB) v(n1) v(out) I_Vna=par('I(VA)') I_Vnb=par('I(VB)') I_n1=par('Id(X0.mn2)-Is(X0.mn1)') I_mn=par('Id(X0.mn1)') I_mp=par('Id(X0.mp1)+Id(X0.mp2)') 
*.print v(nA) v(nB) v(n1) v(out) I_Vna=par('I(VA)') I_Vnb=par('I(VB)') I_n1=par('Id(X0.mp2)-Is(X0.mp1)') I_mn=par('Id(X0.mn1)+Id(X0.mn2)') I_mp=par('Id(X0.mp1)') 
.end

