import sys


def my_cat(x):
    for i in x:
        try:
            with open(i, "r") as folder:
                for j in folder:
                        print j,
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)


if len(sys.argv) == 1:
    print "You don't specify argumetns"
else:
    my_cat(sys.argv[1:])
