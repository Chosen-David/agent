import operator


def moving_average(values, window):
    """Return all full consecutive-window means; positive integer window required.
    A window longer than the input returns []; never mutate values.
    """
    if isinstance(window, bool):
        raise TypeError("window must be a positive integer")
    window = operator.index(window)
    if window <= 0:
        raise ValueError("window must be positive")
    return [sum(values[i:i + window]) / window
            for i in range(len(values) - window + 1)]
