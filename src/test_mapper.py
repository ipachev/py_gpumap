
import mapper
from test_util import TestClassA, TestClassB

import random
import pickle

from util import time_func



class TestMapper:
    def __init__(self):
        self.items = []
        for i in range(10000000):
            item = TestClassA(random.randint(0, 3), random.randint(3, 7), random.randint(7, 11),
                             TestClassB(random.randint(0, 3), random.randint(3, 7), random.randint(7, 11)))
            self.items.append(item)

    def test_map(self):
        items_copy = pickle.loads(pickle.dumps(self.items))
        out_list = time_func("GPUMAP", mapper.gpumap, thing, self.items)


        for i, (initial, modified, out) in enumerate(zip(items_copy, self.items, out_list)):
            assert initial.a + 1000 == modified.a
            assert initial.b + 1000 == modified.b
            assert initial.c + 1000 == modified.c
            assert initial.d + 1000 == modified.d
            assert initial.o.x + 1000 == modified.o.x
            assert initial.o.y + 1000 == modified.o.y
            assert initial.o.z + 1000 == modified.o.z

            assert modified.a + 1000 == out.a
            assert modified.a + modified.b + 1000 == out.b
            assert modified.a + modified.b + modified.c + 1000 == out.c
            assert modified.o.x + 1000 == out.o.x
            assert modified.o.x + modified.o.y + 1000 == out.o.y
            assert modified.o.x + modified.o.y + modified.o.z + 1000 == out.o.z

        out_list2 = time_func("normal map", map, thing, items_copy)

    def test_map_primitives(self):
        print("primitives:")
        items = [random.randint(0, 10) for _ in range(1000)]
        out_list = time_func("GPUMAP", mapper.gpumap, primitive_thing, items)
        out_list2 = time_func("normal map", map, thing, items)


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
    i = 0
    while i < 1000:
        a.increment_all(1)
        i += 1
    b = TestClassA(a.a, a.a + a.b, a.a + a.b + a.c, TestClassB(a.o.x, a.o.x + a.o.y, a.o.x + a.o.y + a.o.z))
    i = 0
    while i < 1000:
        b.increment_all(1)
        i += 1
    return b

if __name__ == "__main__":
    tm = time_func("init objects", TestMapper)

    tm.test_map()
    #tm.test_map_primitives()