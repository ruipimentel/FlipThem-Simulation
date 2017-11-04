# import multiprocessing
# import time
#
# # def worker(j):
# #     if j == 3:
# #         time.sleep(1)
# #     print("Worker:" + str(j))
# #
# #
# # pool = multiprocessing.Pool(processes=4)
# # t = pool.map(worker, range(10))
# #
# # print("hellooooooo")
#
# s = {(1,3), (1,4), (2, 6)}
#
# l = []
#
# def add(t):
#     if t == (1, 3):
#         time.sleep(8)
#     l.append(t[0])
#     print(t[0] + t[1])
#
#
# pool = multiprocessing.Pool()
# pool.map(add, s)
#
#
# pool.close()
# pool.join()
#
#
# print(l)
#
# print("finished")
from multiprocessing import Process, Queue


def computeCopyNum(queue, val):
    queue.put(val) # can also put a tuple of thread-id and value if we would like to

procs=list()

queue = Queue()
for i in range(1, 10):
    p = Process(target=computeCopyNum, args=(queue, i))
    procs.append(p)
    p.start()

for _ in procs:
    val = queue.get()
    print(val)
    # do whatever with val

for p in procs:
    p.join()
