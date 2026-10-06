"""Independent exact-arithmetic checks for the two task instances."""
from fractions import Fraction as F
import math
import json

A = (F(1), F(1,10000))
b = (F(1), F(1,10000))
xhat = (F(1), F(3))
x = tuple(bi/ai for ai,bi in zip(A,b))
r = tuple(ai*hi-bi for ai,hi,bi in zip(A,xhat,b))
error = tuple(hi-xi for hi,xi in zip(xhat,x))
assert x == (1,1) and r == (0,F(1,5000)) and error == (0,2)
assert max(map(abs,r)) < F(1,1000)
assert tuple(ri/ai for ri,ai in zip(r,A)) == error
norm2 = lambda v: math.sqrt(sum(float(t*t) for t in v))
kappa = max(A)/min(A)
rrel = norm2(r)/norm2(b)
frel = norm2(error)/norm2(x)
assert frel <= float(kappa)*rrel
assert max(map(abs,error)) == kappa*max(map(abs,r))
component_residual = [abs(ri/bi) for ri,bi in zip(r,b)]
assert component_residual == [0,2]

candidate = F(21,10)
multiplier = F(4)
g = lambda lam: 2*lam-lam*lam/4
L = lambda y,lam: y*y+lam*(2-y)
upper = candidate*candidate
lower = g(multiplier)
assert candidate >= 2 and multiplier >= 0
assert lower == 4 and L(F(2),multiplier) == lower
assert upper-lower == F(41,100)
assert 2*F(2)-multiplier == 0
assert multiplier*(2-F(2)) == 0
assert 2*candidate-multiplier != 0
assert multiplier*(2-candidate) != 0
# Completing the square is the proof; this finite sweep checks its implementation.
for i in range(-100,101):
 y=F(i,10)
 assert L(y,multiplier) == (y-multiplier/2)**2+g(multiplier)
 if y >= 2:
  assert y*y >= 4
# Failure case: a trial value L(0,4)=8 is NOT the infimum or a lower bound on p*=4.
assert L(F(0),multiplier) == 8 and L(F(0),multiplier) > 4
print(json.dumps({
 'linear': {'exact_solution':list(map(str,x)), 'residual':list(map(str,r)),
 'residual_norm_2':norm2(r), 'residual_norm_2_below_0.001':True,
 'error_norm_2':norm2(error), 'relative_forward_error_2':frel,
 'relative_residual_2':rrel, 'condition_number_2':int(kappa),
 'relative_forward_error_bound_2':float(kappa)*rrel,
 'absolute_forward_error_bound_2':float(kappa)*norm2(r),
 'componentwise_rhs_relative_residual':list(map(str,component_residual)),
 'relative_error_0.001_sufficient_residual_threshold':0.001*norm2(b)/float(kappa)},
 'optimization': {'candidate':str(candidate),'upper':str(upper),'dual_multiplier':str(multiplier),
 'certified_lower':str(lower),'exact_objective_gap':str(upper-lower),
 'relative_objective_gap':str((upper-lower)/lower), 'distance_to_optimizer':str(candidate-2),
 'invalid_trial_lower_bound':str(L(F(0),multiplier))},
 'checks':'all assertions passed; finite checks are not a general formal proof'
},indent=2))
