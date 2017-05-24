def my_range(x, y=0, s=1):
    if y == 0:
        while y < x:
            yield y
            y += s
    else:
        while x < y:
            yield x
            x += s
