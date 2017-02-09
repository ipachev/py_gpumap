from pycuda import autoinit
import pycuda.driver as cuda
from pycuda.compiler import SourceModule

from data_model import ExtractedClasses
from class_def import ClassDefGenerator
from serialization import ListSerializer, ItemSerializer
from builtin import builtin

from test_util import TestClassB

b = TestClassB(5.0, 3.0, 10)

l = [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0]
classes = ExtractedClasses()
class_repr = classes.extract(l[0])
serializer = ListSerializer(class_repr, l)


bs = serializer.to_bytes()
ptr = cuda.to_device(bs)

class_repr = classes.extract(b)
item_serializer = ItemSerializer(class_repr, b)
bs2 = item_serializer.to_bytes()
print(bs2)
ptr2 = cuda.to_device(bs2)

kernel = builtin + ClassDefGenerator().all_cpp_class_defs(classes) + """
extern "C"{
__global__ void kern(List<double> *doubles, TestClassB *b) {
    printf("%lf %lf %lf %lf %lf %lf %lf %lf %lf %lf\\n", doubles->items[0], doubles->items[1], doubles->items[2], doubles->items[3], doubles->items[4], doubles->items[5], doubles->items[6], doubles->items[7], doubles->items[8], doubles->items[9]);
    printf("%lf %lf %d\\n", b->x, b->y, b->z);
    printf("%p %p %p\\n", &b->x, &b->y, &b->z);
}
}
"""
#print(kernel)
mod = SourceModule(kernel, options=["--std=c++11"], no_extern_c=True)
kern = mod.get_function("kern")

kern(ptr, ptr2, block=(5,1,1), grid=(1,1))

