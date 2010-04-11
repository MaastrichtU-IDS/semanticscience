clearVariables
logFile glycam91.log
addPath ../../contrib/glycam
alias a alias
a lp loadamberprep
a ap loadamberparams

parm91 = ap parm91X.dat
gly = ap glycam_93.dat


lp 23ma.prep
lp 26ma.prep
lp 2ma.prep
lp 346mb.prep
lp 34nn.prep
lp 36ma.prep
lp 36mb.prep
lp 3lb.prep
lp 3ma.prep
lp 3mb.prep
lp 3no.prep
lp 46nn.prep
lp 46no.prep
lp 4lb.prep
lp 4ma.prep
lp 4nn.prep
lp 4no.prep
lp 6lb.prep
lp 6ma.prep
lp 6mb.prep
lp 6no.prep
lp fb.prep
lp ga.prep
lp gb.prep
lp la.prep
lp lb.prep
lp ma.prep
lp mb.prep
lp nlk.prep
lp nln.prep
lp nn.prep
lp no.prep
lp ols.prep
lp olt.prep
lp ome.prep

x = {	23M       26A       2MA       34N       36A       
	36B       3LB       3MA       3MB       3NO       
	46N       4LB       4MA       4NN       4NO       
	6LB       6MA       6MB       6NO       FB        
	GA        GB        LA        LB        MA        
	MB        NLK       NLN       NN        NO        
	OLS       OLT       OME       TMB       
}

x = { MA OME }
set x restype saccharide

#
#  fix head residues
#
set OME    head      null
set OME.1  connect0  null

#
#  fix tail residues
#
set FB     tail      null
set FB.1   connect1  null
set GA     tail      null
set GA.1   connect1  null
set GB     tail      null
set GB.1   connect1  null
set LA     tail      null
set LA.1   connect1  null
set LB     tail      null
set LB.1   connect1  null
set MA     tail      null
set MA.1   connect1  null
set MB     tail      null
set MB.1   connect1  null
set NN     tail      null
set NN.1   connect1  null
set NO     tail      null
set NO.1   connect1  null

quit
