import sys


def my_cat(x):
    for i in x:
        try:
            with open(i, "r") as file:
                for j in file:
                        print j,
        except:
            print "No such file or directory : '%s'" % i


if len(sys.argv) == 1:
    print "You don't specify argumetns"
else:
    my_cat(sys.argv[1:])
