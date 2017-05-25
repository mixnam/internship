def my_range(x, y=0, s=1):
    if not y:
        while y < x:
            yield y
            y += s
    else:
        while x < y:
            yield x
            x += s
