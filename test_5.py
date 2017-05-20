def list_squared(x):
    return [i*i for i in x]


def list_second_item(x):
    return [x[i] for i in xrange(len(x)) if i % 2 != 0]


def list_squared_2(x):
    return [x[i]**2 for i in xrange(1, len(x), 2) if x[i] % 2 == 0]
