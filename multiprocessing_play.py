import multiprocessing
import time

# def worker(j):
#     if j == 3:
#         time.sleep(1)
#     print("Worker:" + str(j))
#
#
# pool = multiprocessing.Pool(processes=4)
# t = pool.map(worker, range(10))
#
# print("hellooooooo")

s = {(1,3), (1,4), (2, 6000093221)}


def add(t):
    if t == (1,3):
        time.sleep(8)
    print(t[0] + t[1])


pool = multiprocessing.Pool()
pool.map(add, s)


print("finished")