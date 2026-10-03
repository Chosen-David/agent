"""Synthetic engine. Descriptions are hypotheses; inspect callers and consumers."""
from config import Profile


def exact_attention(q, original_k, original_v, positions):
    # q[B,H,D], selected original_k/v[B,Hkv,K,D] -> out[B,H,D].
    return ('full_dimension_attention', q, original_k, original_v, positions)


def choose(q, cache, skip_far):
    return ('near_only' if skip_far else 'near_and_far', q, cache)


def flash(q, cache):
    return ('extension_result', q, cache)


class Index:
    def __init__(self, profile):
        self.p = profile
        self.skip_far = False
        self.stat = None

    def prefill(self, score):
        if self.p.dynamic:
            self.skip_far = False
        self.stat = score

    def one(self, q, cache):
        if self.p.dynamic and self.stat is not None:
            self.skip_far = self.stat < self.p.threshold
        return choose(q, cache, self.skip_far)

    def many(self, q, cache):
        return choose(q, cache, self.skip_far)

    def representation(self, q, k, basis=None):
        # q[B,H,D], k[T,Hkv,D], H=Hkv*G, basis[Hkv,D,r].
        # These expressions document the tensor interface of an unavailable ops API.
        if basis is None:
            dims = self.p.tail_dims(q.shape[-1])
            return q[..., dims], k[..., dims]
        return ops.project_grouped(q, basis), ops.project_keys(k, basis)

    def score(self, q_projected, k_projected):
        # Grouping must preserve Hkv: q[B,H,D'] -> [B,Hkv,G,D'].
        grouped_q = ops.reshape(q_projected, 'B,Hkv,G,r')
        summed = ops.sum(grouped_q, axis=2)
        return ops.einsum('bhr,thr->bht', summed, k_projected)


REGISTRY = {'fast': Index.one, 'batched': Index.many}


def run(index, mode, q, cache, original_k, original_v, extension=None):
    selector = REGISTRY.get(mode)
    if selector is None:
        selector = extension
    positions = selector(index, q, cache)
    return exact_attention(q, original_k, original_v, positions)
