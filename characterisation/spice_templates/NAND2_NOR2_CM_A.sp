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
X0 hi lo nA nB n1 out $$gate_name

* to make the first data point of tran useful, start from 1 vstep lower. 
.param Vlow_start='$$v_l-$$vstep'
.param delta_v='$$v_h-Vlow_start'
.param tran_step='$$t_rise*$$vstep/(delta_v*$$sp_extend_res)'
.param t_delay='1*tran_step'
.param t_tot='(1*t_delay)+$$t_rise'

VA   nA  0 PULSE (Vlow_start $$v_h t_delay $$t_rise $$t_rise 10ns 20ns)
VB   nB  0 DC=sweep_VB 
Vn1  n1  0 DC=sweep_Vn1
Vout out 0 DC=sweep_Vout

.tran tran_step t_tot SWEEP DATA=sweep_CM_A
$$print_NAND2.print v(nA) v(nB) v(n1) v(out) I_Vna=par('I(VA)') I_Vnb=par('I(VB)') I_n1=par('Id(X0.mn2)-Is(X0.mn1)') I_mn=par('Id(X0.mn1)') I_mp=par('Id(X0.mp1)+Id(X0.mp2)') 
$$print_NOR2.print v(nA) v(nB) v(n1) v(out) I_Vna=par('I(VA)') I_Vnb=par('I(VB)') I_n1=par('Id(X0.mp2)-Is(X0.mp1)') I_mn=par('Id(X0.mn1)+Id(X0.mn2)') I_mp=par('Id(X0.mp1)') 
.end

