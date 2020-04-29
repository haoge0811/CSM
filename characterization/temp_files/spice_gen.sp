* Hao Ge <haoge@usc.edu>
* USC - SPORT LAB

.option NOMOD
.global vdd 
.temp 125.0
.param vdd=0.5

.include './gate_inventory_gen.sp'
.include './sweep_table.inc'

vhi hi 0 vdd
vlo lo 0 0 
X0 hi lo in out INV

* to make the first data point of tran useful, start from 1 vstep lower. 
.param Vlow_start='-0.25-0.05'
.param delta_v='0.75-Vlow_start'
.param tran_step='5e-13*0.05/(delta_v*20)'
.param t_delay='1*tran_step'
.param t_tot='(1*t_delay)+5e-13'

Vin in 0 DC=sweep_vin
Vout out 0 PULSE (Vlow_start 0.75 t_delay 5e-13 5e-13 10ns 20ns)

.tran tran_step t_tot SWEEP DATA=sweep_CO
.print v(in) v(out) I_Vin=par('I(Vin)') I_mn=par('Id(X0.mn1)') I_mp=par('Id(X0.mp1)') 
.end