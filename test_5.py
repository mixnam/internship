list_squared = lambda x : [i*i for i in x]

list_second_item = lambda x : [x[i] for i in xrange(len(x)) if i%2 != 0]

list_squared_2 = lambda x : [pow(x[i],2) for i in xrange(len(x)) if i%2 == 0 and x[i]%2 == 0 and x[i] != 0]
