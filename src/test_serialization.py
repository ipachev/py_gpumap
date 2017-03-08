from serialization import ListSerializer
from data_model import ExtractedClasses
from class_def import ClassDefGenerator

import random
from copy import deepcopy

from pycuda import autoinit
import pycuda.driver as cuda
from pycuda.compiler import SourceModule

class TestClassA:
    def __init__(self, a, b, c, o):
        self.a = a
        self.b = b
        self.c = c
        self.d = 0
        self.o = o

class TestClassB:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.q = TestClassC(1)

class TestClassC:
    def __init__(self, i):
        self.i = i

class TestSerialization:
    def test_serialize_deserialize_object(self):
        class_reprs = ExtractedClasses()

        items = [TestClassA(random.randint(0, 100), random.randint(100, 200), random.randint(200, 300),
                            TestClassB(random.randint(0, 100), random.randint(100, 200), random.randint(200, 300)))
                 for _ in range(1000)]

        duplicate_items = deepcopy(items)

        candidate_item = items[0]
        class_repr = class_reprs.extract(candidate_item)
        serializer = ListSerializer(class_repr, items)

        bytes = serializer.to_bytes()

        new_items = serializer.from_bytes(bytes) # unpack back into same list
        assert new_items is items

        assert len(duplicate_items) == len(new_items)
        for i1, i2 in zip(duplicate_items, new_items):
            assert i1.a == i2.a
            assert i1.b == i2.b
            assert i1.c == i2.c
            assert i1.d == i2.d
            assert i1.o.x == i2.o.x
            assert i1.o.y == i2.o.y
            assert i1.o.z == i2.o.z
            assert i1.o.q.i == i2.o.q.i

        print("passed object to_bytes test")

        serializer2 = ListSerializer(class_repr, length=len(items))

        output_list = serializer2.create_output_list(bytes, candidate_item)
        assert output_list is not items

        assert len(duplicate_items) == len(output_list)
        for i1, i2 in zip(duplicate_items, output_list):
            assert i1.a == i2.a
            assert i1.b == i2.b
            assert i1.c == i2.c
            assert i1.d == i2.d
            assert i1.o.x == i2.o.x
            assert i1.o.y == i2.o.y
            assert i1.o.z == i2.o.z
            assert i1.o.q.i == i2.o.q.i

        print("passed object create_output_list test")

    def test_serialize_deserialize_primitives(self):
        class_reprs = ExtractedClasses()

        items = [random.randint(0, 1024) for _ in range(1000)]

        duplicate_items = deepcopy(items)

        candidate_item = items[0]

        class_repr = class_reprs.extract(candidate_item)
        serializer = ListSerializer(class_repr, items)

        bytes = serializer.to_bytes()

        new_items = serializer.from_bytes(bytes)

        assert len(duplicate_items) == len(new_items)
        for i1, i2 in zip(duplicate_items, new_items):
            assert i1 == i2

        print("passed primitive to_bytes test")

        serializer2 = ListSerializer(class_repr, length=len(items))
        output_list = serializer2.create_output_list(bytes, candidate_item)
        assert output_list is not items

        assert len(duplicate_items) == len(output_list)
        for i1, i2 in zip(duplicate_items, output_list):
            assert i1 == i2

        print("passed primitive create_output_list test")

    def test_gpu(self):
        class_reprs = ExtractedClasses()
        items = [TestClassA(random.randint(0, 100), random.randint(100, 200), random.randint(200, 300),
                            TestClassB(random.randint(0, 100), random.randint(100, 200), random.randint(200, 300)))
                 for _ in range(1000)]

        candidate_item = items[0]
        class_repr = class_reprs.extract(candidate_item)

        serializer = ListSerializer(class_repr, items)
        bytes = serializer.to_bytes()

        cls_def_gen = ClassDefGenerator()
        from builtin import builtin

        kernel = builtin + cls_def_gen.all_cpp_class_defs(class_reprs) + """
extern "C" {
__global__ void test(List<TestClassA> *things) {
  List<TestClassA> &things_ref = *things;
  int val = things_ref[threadIdx.x].a;
  int val2 = things_ref[threadIdx.x].b;
  int val3 = things_ref[threadIdx.x].o.x;
  things_ref[threadIdx.x].o.x = val * val2 * val3;
}
}
"""
        mod = SourceModule(kernel, options=["--std=c++11"], no_extern_c=True)
        stuff = mod.get_function("test")

        list_ptr = cuda.to_device(bytes)
        new_bytes = bytearray(len(bytes))
        stuff(list_ptr, block=(len(items), 1, 1))
        cuda.memcpy_dtoh(new_bytes, list_ptr)

        deserializer = ListSerializer(class_repr, length=len(items))
        new_list = deserializer.create_output_list(new_bytes, candidate_item)

        for item, new_item in zip(items, new_list):
            assert item.a == new_item.a
            assert item.b == new_item.b
            assert item.c == new_item.c
            assert item.o.x * item.a * item.b == new_item.o.x
            assert item.o.y == new_item.o.y
            assert item.o.z == new_item.o.z

        print("GPUTest done!")


if __name__ == "__main__":
    t = TestSerialization()
    t.test_serialize_deserialize_object()
    t.test_serialize_deserialize_primitives()
    t.test_gpu()