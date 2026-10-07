def measure(n):
    if type(n) is not int or n < 0: raise ValueError("nonnegative integer required")
    return sum(i*i for i in range(n))
