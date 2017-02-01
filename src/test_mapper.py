
import mapper
from test_util import TestClassA, TestClassB

import random
import pickle
import math

from util import time_func


class TestMapper:
    def __init__(self):
        self.items = [TestClassA(random.randint(0,30), random.randint(0,30), random.randint(0,30),
                      TestClassB(random.randint(0,30), random.randint(0,30), random.randint(0,30)))
                      for _ in range(1000)]


    def test_map(self):
        items_copy = pickle.loads(pickle.dumps(self.items))
        out_list = time_func("GPUMAP", mapper.gpumap, thing, self.items)

        for i, (initial, modified, out) in enumerate(zip(items_copy, self.items, out_list)):
            assert initial.a + 10000 == modified.a
            assert initial.b + 10000 == modified.b
            assert initial.c + 10000 == modified.c
            assert initial.d + 10000 == modified.d
            assert initial.o.x + 10000 == modified.o.x
            assert initial.o.y + 10000 == modified.o.y
            assert initial.o.z + 10000 == modified.o.z

            assert modified.a + 10000 == out.a
            assert modified.a + modified.b + 10000 == out.b
            assert modified.a + modified.b + modified.c + 10000 == out.c
            assert modified.o.x + 10000 == out.o.x
            assert modified.o.x + modified.o.y + 10000 == out.o.y
            assert modified.o.x + modified.o.y + modified.o.z + 10000 == out.o.z

        out_list2 = time_func("normal map", list, map(thing, items_copy))

    def test_map_primitives(self):
        print("primitives:")
        items = [random.randint(0, 30) for _ in range(10000)]
        out_list = time_func("GPUMAP", mapper.gpumap, primitive_thing, items)
        out_list2 = time_func("normal map", list, map(primitive_thing, items))


def primitive_thing(n):

    i = 0
    while i < 1000:
        n += 1
        i += 1

    a = n
    i = 0
    while i < 1000:
        a += 1
        i += 1

    return a


def thing(a):
    upper = 20000
    step = 2
    x = math.floor(step)
    for i in range(0, upper, step):
        a.increment_all(1)
    b = TestClassA(a.a, a.a + a.b, a.a + a.b + a.c, TestClassB(a.o.x, a.o.x + a.o.y, a.o.x + a.o.y + a.o.z))
    for i in range(10000):
        b.increment_all(1)
    return b

if __name__ == "__main__":
    tm = time_func("init objects", TestMapper)

    tm.test_map()
    #tm.test_map_primitives()