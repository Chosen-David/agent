import os


class Profile:
    def __init__(self):
        self.near = int(os.environ.get('READ_NEAR', '8'))
        self.budget = 4
        self.forced = 1
        self.dynamic = os.environ.get('READ_DYNAMIC', '0') == '1'
        self.threshold = 0.05

    def tail_dims(self, dim):
        # Assumes rotate_half layout; does not inspect the model instance.
        half = dim // 2
        return list(range(half - 2, half)) + list(range(dim - 2, dim))


class FullRotary:
    def __init__(self, dim=8):
        self.rotary_dim = dim
        self.layout = 'rotate_half'


class PartialRotary:
    def __init__(self, dim=8):
        self.rotary_dim = dim // 2
        self.layout = 'interleaved'
