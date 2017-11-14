from multiprocessing import Pool
import time

def f(x):
    return x[0]*x[1]

if __name__ == '__main__':

    s = set()
    s.add((1, 2))
    s.add((3, 2.1))
    s.add((1.2, 0.9))
    s.add((1.1, 2.2))

    print(s)
    t1 = time.time()
    with Pool(5) as p:
        t = p.map(f, s)

    t2 = time.time()

    print(t2 - t1)
    l = []

    t3 = time.time()
    for v in s:
        l.append(v[0]*v[1])

    print(l)
    t4 = time.time()
    print(t4-t3)
