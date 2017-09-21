def interval_intersection(interval_1, interval_2):
    """
    :param interval_1: A tuple representing an interval of time
    :param interval_2: A tuple representing an interval of time
    :return:
    """
    bottom = max(interval_1[0], interval_2[0])
    top = min(interval_1[1], interval_2[1])

    if top >= bottom:
        return bottom, top


def list_intersection(list1, list2):
    """
    :param list1: List of 2-tuples, each 2-tuple representing an interval
    :param list2: List of 2-tuples, each 2-tuple representing an interval
    :return:
    """
    t = []
    for l in list1:
        for h in list2:
            i = interval_intersection(l, h)
            if i is not None:
                t.append(i)
    return t


def intersection(lists):
    """
    :param lists: List of list of 2-tuples, each 2-tuple representing an interval
    :return:
    """
    if len(lists) == 1:
        return lists[0]
    q1 = lists[0]
    starter = []
    for l in lists[1:]:
        starter = list_intersection(q1, l)

    print(starter)
    return starter



