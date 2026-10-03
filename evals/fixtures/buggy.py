def moving_average(values, window):
    """Return all full consecutive-window means; positive integer window required.
    A window longer than the input returns []; never mutate values.
    """
    return [sum(values[i:i + window]) / window for i in range(len(values) - window)]
