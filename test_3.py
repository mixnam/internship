def my_range(x, y=0, s=1):
    while y < x:
        yield y
        y += s
