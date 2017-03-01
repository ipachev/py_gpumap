
import mapper
from test_util import TestClassA, TestClassB, TestClassC

import random
import pickle
import math

from util import time_func


def sum(l):
    s = 0
    for i in range(len(l)):
        l[i].b += 10
        s += l[i].a
    return s


def do_sum(l):
    return sum(l)

class TestMapper:
    def __init__(self):
        self.items = [TestClassA(random.randint(0,30), random.randint(0,30), random.randint(0,30),
                      TestClassB(random.randint(0,30), random.randint(0,30), random.randint(0,30)))
                      for _ in range(1000)]

    class TestClassD:
        def __init__(self, thing):
            self.thing = thing

    def test_list_of_list(self):
        print("\n\nLIST OF LIST TEST:\n")
        pickle_str = pickle.dumps(self.items)
        items = [pickle.loads(pickle_str) for _ in range(10)]
        items_duplicate = [pickle.loads(pickle_str) for _ in range(10)]
        items_duplicate2 = [pickle.loads(pickle_str) for _ in range(10)]

        gpu_output = time_func("gpu", mapper.gpumap, do_sum, items)
        cpu_output = time_func("cpu", list, map(do_sum, items_duplicate))

        for l1, l2, l3 in zip(items, items_duplicate, items_duplicate2):
            for gpu, cpu, orig in zip(l1, l2, l3):
                assert gpu.b == cpu.b
                assert gpu.b == orig.b + 10

        for gpu, cpu in zip(gpu_output, cpu_output):
            assert gpu == cpu


    def test_foreach(self):
        foreach_items = pickle.loads(pickle.dumps(self.items))
        print("\n\nFOREACH TEST:\n")
        a_list = [TestClassC(i + 1) for i in range(2000)]
        b_list = [TestClassC(1) for i in range(1000)]
        something = TestMapper.TestClassD(True)
        another_something = TestMapper.TestClassD(True)
        def a_func(a):
            step = 2.3
            a_list[100].i = 1234  # bad practice. all threads will try to set this...
            if something.thing:
                x = int(math.floor(step))
                for i in range(0, a_list[1999].i, x):
                    a.increment_all(1)
            b = TestClassA(a.a, a.a + a.b, a.a + a.b + a.c, TestClassB(a.o.x, a.o.x + a.o.y, a.o.x + a.o.y + a.o.z))
            for c in b_list:
                b.increment_all(c.i)
            another_something.thing = False  # bad practice all threads will try to set this

        mapper.gpumap(a_func, foreach_items)

    def test_map(self):


        a_list = [TestClassC(i+1) for i in range(2000)]
        b_list = [TestClassC(1) for i in range(1000)]
        something = TestMapper.TestClassD(True)
        another_something = TestMapper.TestClassD(True)


        def thing(a):
            step = 2.3
            a_list[100].i = 1234 # bad practice. all threads will try to set this...
            if something.thing:
                x = int(math.floor(step))
                for i in range(0, a_list[1999].i, x):
                    a.increment_all(1)
            b = TestClassA(a.a, a.a + a.b, a.a + a.b + a.c, TestClassB(a.o.x, a.o.x + a.o.y, a.o.x + a.o.y + a.o.z))
            for c in b_list:
                b.increment_all(c.i)
            another_something.thing = False # bad practice all threads will try to set this
            c = test_func(b)
            return c


        print("\n\nMAP TEST:\n")
        items_copy = pickle.loads(pickle.dumps(self.items))
        items_copy2 = pickle.loads(pickle.dumps(self.items))
        out_list = time_func("GPUMAP", mapper.gpumap, thing, self.items)
        out_list2 = time_func("normal map", list, map(thing, items_copy2))
        assert a_list[100].i == 1234
        assert another_something.thing == False
        assert len(items_copy) == len(self.items) == len(out_list) == len(out_list2)
        for i, (initial, modified, out, out2) in enumerate(zip(items_copy, self.items, out_list, out_list2)):
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

            assert out.a == out2.a
            assert out.b == out2.b
            assert out.c == out2.c
            assert out.o.x == out2.o.x
            assert out.o.y == out.o.y
            assert out.o.z == out2.o.z


    def test_map_primitives(self):
        print("\n\nPRIMITIVE MAP TEST:\n")
        print("primitives:")

        def primitive_thing(n):
            for i in range(1000):
                n += 1
            a = n
            for i in range(1000):
                a += 1

            return a

        items = [random.randint(0, 30) for _ in range(10000)]
        out_list = time_func("GPUMAP", mapper.gpumap, primitive_thing, items)
        out_list2 = time_func("normal map", list, map(primitive_thing, items))
        out_list3 = list(map(primitive_thing, items))
        assert len(items) == len(out_list) == len(out_list2) == len(out_list3)
        for i1, i2, i3 in zip(out_list, out_list2, out_list3):
            assert i1 == i2 == i3

def test_func(b):
    return b

if __name__ == "__main__":
    tm = time_func("init objects", TestMapper)
    tm.test_list_of_list()
    tm.test_foreach()
    tm.test_map()
    tm.test_map_primitives()