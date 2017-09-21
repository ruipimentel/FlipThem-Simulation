import numpy as np

t1 = (1, 5)
t2 = (3, 7)

f1 = 4, 6
f2 = 7, 9


def find_intersection(interval_1, interval_2):

    bottom = max(interval_1[0], interval_2[0])
    top = min(interval_1[1], interval_2[1])

    if top >= bottom:
        return bottom, top


print(find_intersection(t1, t2))

print(find_intersection(f1, f2))


# each server has a list of benefit tuples. We need to find times when all of them
l1 = [(1, 3.43), (4.2, 5.46), (6.74, 9.34)]
l2 = [(2.34, 4.1), (4.5, 9.9)]
l3 = [(6.78, 9.1), (9.3, 10.1)]


def list_intersections(list1, list2):
    t = []
    for l in list1:
        for h in list2:
            i = find_intersection(l, h)
            if i is not None:
                t.append(i)
    return t
# print(benefits(l1, l2))


def intersections(lists):
    q1 = lists[0]
    starter = []
    for l in lists[1:]:
        starter = benefits(q1, l)
    # print(starter)

    return starter

print(more([l1, l2, l3]))