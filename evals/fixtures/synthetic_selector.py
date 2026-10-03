"""Synthetic misleading narrative: near is the forced window; skip means no scoring.
The projector is query-trained and final scoring uses reduced keys. Verify these claims.
"""


def represent(vector, basis=None):
    if basis is None:
        return [vector[0], vector[2]]
    return [sum(a * b for a, b in zip(vector, column)) for column in basis]


def full_score(query, keys, positions):
    return [sum(a * b for a, b in zip(query, keys[i])) for i in positions]


def select(query, keys, near_len=4, forced_len=1, budget=3, far_budget=1,
           skip_far=False, basis=None):
    n = len(keys)
    boundary = max(0, n - near_len)
    forced = list(range(max(0, n - forced_len), n))
    qsmall = represent(query, basis)
    scores = [sum(a * b for a, b in zip(qsmall, represent(k, basis))) for k in keys]
    far = [] if skip_far else sorted(range(boundary), key=lambda i: -scores[i])[:far_budget]
    near = sorted(range(boundary, max(boundary, n - forced_len)), key=lambda i: -scores[i])
    return far + near[:max(0, budget - len(forced) - len(far))] + forced


def run(query, keys, **options):
    positions = select(query, keys, **options)
    return positions, full_score(query, keys, positions)
