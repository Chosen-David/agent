"""A tiny executable selector/full-value consumer; all data are synthetic."""
from array import array


def encode(rows):
    if not rows or any(len(row) != 4 for row in rows):
        raise ValueError('expected nonempty [T,4] values')
    return [array('f', row) for row in rows]


def select(values, projected=False):
    # Reduced representation is for index scoring only.
    reduced = [list(row[2:]) for row in values]
    if projected:
        reduced = [[row[0] + row[2], row[1] - row[3]] for row in values]
    scores = [sum(row) for row in reduced]
    position = max(range(len(scores)), key=scores.__getitem__)
    return position, reduced


def consume(values, position):
    # The final consumer preserves original width and float32 conversion.
    return list(values[position])


def run(rows, mode='default', extension=None):
    values = encode(rows)
    if mode in ('default', 'projected'):
        position, reduced = select(values, projected=mode == 'projected')
    elif extension is not None:
        position, reduced = extension(values)
    else:
        raise LookupError('unknown mode needs caller extension')
    return dict(output=consume(values, position), selected=position,
                reduced_shape=[len(reduced), len(reduced[0])],
                full_shape=[len(values), len(values[0])], dtype=values[0].typecode)
