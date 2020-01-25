* Hao Ge <haoge@usc.edu>
* USC - SPORT LAB

.option NOMOD
.global vdd 
.temp $$temp
.param vdd=$$vdd

.include '$$gate_inventory'
.include '$$sweep_table'

vhi hi 0 vdd
vlo lo 0 0 
X0 hi lo in out INV

Vin in 0 DC=sweep_Vin
Vout out 0 DC=sweep_Vout

.dc SWEEP DATA=sweep_DC
.print v(in) v(out) I_Vin=par('I(Vin)') I_mn=par('Id(X0.mn1)') I_mp=par('Id(X0.mp1)') 
.end

