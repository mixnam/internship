def my_zip(x, y):
    return [(x[i], y[i]) for i in xrange(min(len(x), len(y)))]
