"""Independent arithmetic examples and failure boundaries for round-two entries."""
from fractions import Fraction as F
import math
import unittest

class FoundationMathTests(unittest.TestCase):
    def test_residual_and_finite_perturbation(self):
        residual=0.001;condition=1000
        actual=1/math.sqrt(2)
        bound=condition*residual/math.sqrt(1+1e-6)
        self.assertLessEqual(actual,bound)
        self.assertGreater(actual,.7)
        # A=diag(1, 0.1), E=diag(0,-0.01), b=(0,1), e=0
        x=10.;changed=1/.09
        error=abs(changed-x)/x
        finite=10*.01/(1-10*.01)
        self.assertAlmostEqual(error,finite)
        self.assertGreater(error,10*.01)

    def test_reynolds_projection_and_nonconvex_failure(self):
        def project(x): return ((x[0]+x[1])/2,)*2
        self.assertEqual(project((2,6)),(4,4))
        self.assertEqual(project(project((2,6))),project((2,6)))
        self.assertNotIn(project((1,0)),[(1,0),(0,1)])
        # S=[[1,2],[0,-1]] satisfies S^2=I but is not orthogonal.
        def S(x): return (x[0]+2*x[1],-x[1])
        x=(2,3);self.assertEqual(S(S(x)),x)
        P=lambda x: ((x[0]+S(x)[0])/2,(x[1]+S(x)[1])/2)
        self.assertEqual(P(P(x)),P(x))
        self.assertNotEqual(P((0,1))[0],P((1,0))[1])
        biased=lambda x: (.75*x[0]+.25*x[1],.25*x[0]+.75*x[1])
        self.assertNotEqual(biased(biased((1,0))),biased((1,0)))

    def test_dual_certificate_and_nonconvex_stationary_point(self):
        g=lambda lam:lam-lam*lam/4
        for lam in range(11):
            for x in (1,1.01,2,10): self.assertLessEqual(g(lam),x*x)
        self.assertEqual(g(2),1)
        self.assertAlmostEqual(1.01**2-g(2),.0201)
        f=lambda x:x**4-x*x
        self.assertLess(f(1/math.sqrt(2)),f(0))
        # Numerical local minimization of L has value >= inf L; upper estimate
        # is not automatically a valid primal lower bound.
        self.assertGreater(3**2+2*(1-3),1)

    def test_noether_energy_and_discretization(self):
        q=F(3,2);v=F(-2,3);gamma=F(1,5);h=F(1,10)
        self.assertEqual(q*v+v*(-q),0)
        self.assertEqual(q*v+v*(-q-gamma*v),-gamma*v*v)
        H=(q*q+v*v)/2
        Hnext=((q+h*v)**2+(v-h*q)**2)/2
        self.assertEqual(Hnext,(1+h*h)*H)

    def test_joint_error_improves_uniform_bound_without_converse(self):
        eta=3*.025;gap=.12
        self.assertGreater(gap,math.sqrt(2)*eta)
        self.assertLess(gap,2*eta)
        e=(eta/math.sqrt(2),-eta/math.sqrt(2))
        self.assertAlmostEqual(math.hypot(*e),eta)
        self.assertAlmostEqual(e[0]-e[1],math.sqrt(2)*eta)
        epsilon=.1
        self.assertGreater(epsilon-(-epsilon),math.sqrt(2)*epsilon)

if __name__=='__main__': unittest.main()
