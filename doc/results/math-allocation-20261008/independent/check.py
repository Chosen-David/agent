"""Independent exhaustive validation; no producer reference implementation reused."""
import hashlib, importlib.util, itertools, json, math, random, subprocess, sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN = HERE.parent

def exhaustive(menus, budget):
    best = None
    for selection in itertools.product(*menus):
        if sum(option[0] for option in selection) <= budget:
            value = sum(option[1] for option in selection)
            best = value if best is None else min(best, value)
    return best

def sparse(menus, budget):
    states = {0: 0}
    for menu in menus:
        new = {}
        for cost, loss in states.items():
            for extra, penalty in menu:
                total = cost + extra
                if total <= budget:
                    new[total] = min(new.get(total, math.inf), loss + penalty)
        states = new
    return min(states.values()) if states else None

def main():
    raw = json.loads((RUN/'raw.json').read_text())
    spec = importlib.util.spec_from_file_location('producer', RUN/'verify.py')
    producer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(producer)
    feasible = infeasible = 0
    for row in raw['rows']:
        menus, budget = row['menus'], row['budget']
        ref = exhaustive(menus, budget)
        assert sparse(menus, budget) == ref
        actual = row['opt']
        assert (actual[0] if actual is not None else None) == ref
        if actual is None:
            infeasible += 1
        else:
            feasible += 1
            indices = actual[1]
            assert len(indices) == len(menus)
            assert sum(menus[i][j][0] for i,j in enumerate(indices)) <= budget
            assert sum(menus[i][j][1] for i,j in enumerate(indices)) == actual[0]
        for multiplier, reported in row['lower_bounds'].items():
            lam = Fraction(multiplier)
            candidates = [sum(Fraction(c[1])+lam*c[0] for c in selection)-lam*budget for selection in itertools.product(*menus)]
            bound = min(candidates)
            assert bound == Fraction(reported)
            assert ref is None or bound <= ref
    for row in raw['rounding']:
        costs = list(map(Fraction, row['costs']))
        rounded = [math.ceil(c/Fraction(1,2)) for c in costs]
        assert rounded == row['rounded']
        assert sum(costs) == Fraction(row['original_sum'])
        assert (sum(rounded) <= math.floor(Fraction(5,3)/Fraction(1,2))) == row['rounded_feasible']
        assert not row['rounded_feasible'] or sum(costs) <= Fraction(5,3)
    rng = random.Random(87319)
    extra = 0
    for _ in range(80):
        menus = [[(rng.randrange(5), rng.randrange(-8,10)) for _ in range(rng.randrange(1,5))] for _ in range(rng.randrange(0,5))]
        for budget in range(11):
            ref = exhaustive(menus, budget)
            result = producer.dp(menus,budget)
            assert (None if result is None else result[0]) == ref == sparse(menus,budget)
            extra += 1
    # Independent piecewise dual envelope: g=min(5-2λ,4,λ).
    assert min(Fraction(5)-2*Fraction(5,3), Fraction(4), Fraction(5,3)) == Fraction(5,3)
    assert exhaustive([[(0,5),(2,4),(3,0)]],2) == 4
    joint = raw['coupling']
    ref = exhaustive(joint['menus'],joint['budget'])
    minimizers = [js for js in itertools.product(range(2),repeat=2) if sum(joint['menus'][i][j][0] for i,j in enumerate(js)) <= joint['budget'] and sum(joint['menus'][i][j][1] for i,j in enumerate(js)) == ref]
    assert all(joint['joint_loss'][''.join(map(str,js))] == 10 for js in minimizers)
    assert joint['joint_loss']['00'] == 0
    subprocess.run([sys.executable,str(RUN/'verify.py'),'--out',str(HERE/'rerun')],check=True)
    assert (RUN/'raw.json').read_bytes() == (HERE/'rerun/raw.json').read_bytes()
    inspected = ['verify.py','config.json','raw.json','summary.json','environment.json','validation-plan.json']
    report = {'status':'usable-with-scope','scope':'finite exact additive CPU fixtures only; no model/e2e/GPU or formal proof acceptance','raw_rows':len(raw['rows']),'feasible_rows':feasible,'infeasible_rows':infeasible,'rounding_rows':len(raw['rounding']),'additional_reference_cases':extra,'independent_reference':'exhaustive selected-option tuples plus sparse exact-cost recurrence','raw_rerun_identical':True,'sha256':{p:hashlib.sha256((RUN/p).read_bytes()).hexdigest() for p in inspected}}
    (HERE/'checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__ == '__main__':
    main()
