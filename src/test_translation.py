from test_util import TestClassB, TestClassA
from examiner import FunctionCallExaminer
from data_model import ExtractedClasses, Functions
from class_def import ClassDefGenerator
from func_def import MethodDefGenerator, FunctionDefGenerator

from pycuda import autoinit
import pycuda.driver as cuda
from pycuda.compiler import SourceModule


class TestTranslation:
    def run(self):
        # create the test object
        test_obj = TestClassA(1,2,3, TestClassB(4,5,6))

        # store class info here including member data and method info
        class_reprs = ExtractedClasses()
        class_reprs.extract(test_obj)

        # store function info here
        func_reprs = Functions()

        FunctionCallExaminer.runfunc(do_stuff, test_obj)
        called_functions = FunctionCallExaminer.results()

        class_reprs.add_methods(called_functions)
        func_reprs.add_functions(called_functions)

        cls_def_gen = ClassDefGenerator()

        kernel = cls_def_gen.all_cpp_class_defs(class_reprs)

        fn_def_gen = FunctionDefGenerator()
        kernel += fn_def_gen.all_func_protos(func_reprs) + "\n"
        kernel += fn_def_gen.all_func_defs(func_reprs)

        method_gen = MethodDefGenerator()
        for class_repr in class_reprs.classes.values():
            kernel += method_gen.all_method_defs(class_repr)

        kernel += """
extern "C" {
#include <stdio.h>
__global__ void stuff() {
    TestClassB b = TestClassB(0,0,0);
    TestClassA a = TestClassA(0,0,0,b);
    printf("%d %d %d %d %d %d\\n", a.a, a.b, a.c, a.o.x, a.o.y, a.o.z);
    TestClassA new_a = do_stuff(a);
    printf("%d %d %d %d %d %d\\n", a.a, a.b, a.c, a.o.x, a.o.y, a.o.z);
    printf("%d %d %d %d %d %d\\n", new_a.a, new_a.b, new_a.c, new_a.o.x, new_a.o.y, new_a.o.z);

    TestClassA thing = TestClassA(1,2,3, TestClassB(4, 5, 6));
    printf("%d %d %d %d %d %d\\n", thing.a, thing.b, thing.c, thing.o.x, thing.o.y, thing.o.z);

    thing.increment_all(6);
    printf("%d %d %d %d %d %d\\n", thing.a, thing.b, thing.c, thing.o.x, thing.o.y, thing.o.z);
}
}
        """
        print(kernel)
        mod = SourceModule(kernel, options=["--std=c++11"], no_extern_c=True)
        stuff = mod.get_function("stuff")
        stuff(block=(10,1,1))

def do_stuff(o):
    o.increment_all(1)
    o2 = TestClassA(o.a, o.a + o.b, o.a + o.b + o.c, TestClassB(o.o.x, o.o.x + o.o.y, o.o.x + o.o.y + o.o.z))
    return o2


if __name__ == "__main__":
    TestTranslation().run()