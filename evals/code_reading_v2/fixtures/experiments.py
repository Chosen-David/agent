"""Experiment utility; not called by runtime engine."""
from config import Profile


def make_trial():
    p = Profile()
    p.dynamic = True
    p.near = 16
    return p


def calibrate(far_keys, rank, ops):
    # keys[T,Hkv,D]. No mean subtraction or query fitting.
    bases = []
    for h in range(far_keys.shape[1]):
        _, _, vt = ops.svd(far_keys[:, h], full_matrices=False)
        bases.append(vt[:rank].T)
    return ops.stack(bases)
