from fractions import Fraction as F
from itertools import permutations
from math import sqrt, isclose
import json
from pathlib import Path
out = Path('/tmp/knowledge-forward-e')
x = (F(1,2),F(1,3),F(1,6))
orbit = list(permutations(x))
avg = tuple(sum(p[i] for p in orbit)/len(orbit) for i in range(3))
f = lambda z: sum(t*t for t in z)
assert avg == (F(1,3),)*3
assert f(avg) == F(1,3) < f(x) == F(7,18)
assert f((F(1),F(0),F(0))) == 1
assert avg not in [(F(1),F(0),F(0)),(F(0),F(1),F(0)),(F(0),F(0),F(1))]
h,q,v = F(1,5),F(1),F(0)
energy=lambda q,v: (q*q+v*v)/2
H0=energy(q,v)
q1,v1=q+h*v,v-h*q
assert (q1,v1)==(1,F(-1,5))
assert energy(q1,v1)==F(13,25)
for _ in range(20):
 H=energy(q,v)
 q,v=q+h*v,v-h*q
 assert energy(q,v)==(1+h*h)*H
assert energy(q,v)==H0*(1+h*h)**20
eta=2*.04
threshold=sqrt(2)*eta
gap=.13
assert gap<2*eta and gap>threshold
# Tight two-score perturbation: K=[.065,0], q=2;
# E=K-Khat=[a/2,-a/2] has row spectral norm .04.
a=eta/sqrt(2)
s=[.13,0.]
e=[a,-a]
shat=[s[i]-e[i] for i in range(2)]
assert isclose(sqrt(sum((z/2)**2 for z in e)),.04)
assert isclose(shat[0]-shat[1],gap-threshold)
assert shat[0]>shat[1]
# Entrywise information alone allows a reversal, but violates joint budget.
coordinate_only=[s[0]-.08,s[1]+.08]
assert coordinate_only[0]<coordinate_only[1]
assert sqrt(.08**2+.08**2)>.08
# Equality threshold permits a tie under the joint budget.
tie=[threshold-a,a]
assert isclose(tie[0],tie[1])
results={
 'status':'all assertions passed',
 'orbit_average':[str(t) for t in avg],
 'objective_before':str(f(x)), 'objective_after':str(f(avg)),
 'one_hot_objective':1,'average_one_hot_feasible':False,
 'q1':str(q1),'v1':str(v1),'H0':str(H0),'H1':str(energy(q1,v1)),
 'relative_energy_growth':str((energy(q1,v1)-H0)/H0),
 'H20':float(energy(q,v)),
 'eta':eta,'basic_threshold':2*eta,'joint_threshold':threshold,
 'guaranteed_cross_boundary_gap':gap-threshold,
 'tight_example_K':[.065,0.], 'tight_example_K_minus_Khat':[z/2 for z in e],
 'tight_example_scores_after':shat,
 'coordinate_only_reversal':coordinate_only,
 'equality_tie':tie
}
(out/'computations.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
