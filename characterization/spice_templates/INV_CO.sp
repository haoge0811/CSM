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

* to make the first data point of tran useful, start from 1 vstep lower. 
.param Vlow_start='$$v_l-$$vstep'
.param delta_v='$$v_h-Vlow_start'
.param tran_step='$$t_rise*$$vstep/(delta_v*$$sp_extend_res)'
.param t_delay='1*tran_step'
.param t_tot='(1*t_delay)+$$t_rise'

Vin in 0 DC=sweep_vin
Vout out 0 PULSE (Vlow_start $$v_h t_delay $$t_rise $$t_rise 10ns 20ns)

.tran tran_step t_tot SWEEP DATA=sweep_CO
.print v(in) v(out) I_Vin=par('I(Vin)') I_mn=par('Id(X0.mn1)') I_mp=par('Id(X0.mp1)') 
.end