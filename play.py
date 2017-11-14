import timeit

s = """
d = {}
att = (1,2,3,4,5,6,7,8,9,10)
for a in att:
    d[a] = {}
"""

print(timeit.timeit(stmt=s, number=10000))


s = """
d = {}
att = (1,2,3,4,5,6,7,8,9,10)
d.update(dict.fromkeys(att, {}))
"""

print(timeit.timeit(stmt=s,  number=10000))
