from examiner import FunctionCallExaminer
from data_model import ExtractedClasses, Functions
from serialization import ListSerializer

from class_def import ClassDefGenerator
from func_def import FunctionDefGenerator, MethodDefGenerator

from pycuda import autoinit
import pycuda.driver as cuda
from pycuda.compiler import SourceModule
import os
from util import time_func
import numpy

main_func = """
extern "C" {{
#include <stdio.h>
__global__ void map_kernel({in_type} *in, {out_type} *out, int length) {{
    int thread_id = blockIdx.x * blockDim.x + threadIdx.x;
    if (thread_id < length) {{
        {in_type} &in_item = in[thread_id];
        out[thread_id] = {func_name}(in_item);
    }}
}}
}}
"""

class MapperKernel:
    def __init__(self, classes, functions, entry_point):
        self.classes = classes
        self.functions = functions
        self.source_module = None
        self.func = None
        self.entry_point = entry_point
        self.includes = ["builtin.hpp"]

    def _create_includes(self):
        lines = []
        for include in self.includes:
            lines.append("#include \"%s\"" % include)
        return "\n".join(lines) + "\n"

    def _build_kernel(self):
        cls_def_gen = ClassDefGenerator()

        kernel = self._create_includes() + "\n"

        kernel += cls_def_gen.all_cpp_class_defs(self.classes)

        fn_def_gen = FunctionDefGenerator()
        kernel += fn_def_gen.all_func_protos(self.functions) + "\n"
        kernel += fn_def_gen.all_func_defs(self.functions) + "\n"

        method_gen = MethodDefGenerator()
        for class_repr in self.classes.classes.values():
            kernel += method_gen.all_method_defs(class_repr)

        in_type = self.entry_point.types[0].__name__
        out_type = self.entry_point.return_type.__name__
        func_name = self.entry_point.name

        kernel += main_func.format(in_type=in_type, out_type=out_type, func_name=func_name)
        #print(kernel)
        return kernel

    def _build_module(self):
        kernel = time_func("code generator", self._build_kernel)
        current_dir = os.path.dirname(os.path.realpath(__file__))
        self.source_module = SourceModule(kernel, options=["--std=c++11"], no_extern_c=True, include_dirs=[current_dir])
        self.func = self.source_module.get_function("map_kernel")

    def get_func(self):
        self._build_module()
        return self.func


class Mapper:
    def __init__(self, func, _list):
        self.func = func
        self.rest = _list[1:]
        self.candidate_in = _list[0]
        self.candidate_out = None
        self.classes = ExtractedClasses()
        self.candidate_in_repr = self.classes.extract(self.candidate_in)
        self.candidate_out_repr = None

        self.functions = Functions()
        self.in_serializer = ListSerializer(self.candidate_in_repr, self.rest)
        self.out_serializer = None

        self.in_ptr = None
        self.out_ptr = None

        self.mapper_kernel = None

        self.input_bytes_len = None
        self.output_bytes_len = None

    def get_dims(self):
        total_length = len(self.rest)
        block_size = 1024
        grid_size = total_length // block_size + (1 if total_length % block_size > 0 else 0)
        return (block_size, 1, 1), (grid_size, 1)

    def do_first_call(self):
        self.candidate_out = FunctionCallExaminer.runfunc(self.func, self.candidate_in)
        self.candidate_out_repr = self.classes.extract(self.candidate_out)

        called = FunctionCallExaminer.results()
        self.classes.add_methods(called)
        self.functions.add_functions(called)

        self.out_serializer = ListSerializer(self.candidate_out_repr, length=len(self.rest))
        return called[0]

    def serialize_input(self):
        input_bytes = self.in_serializer.to_bytes()
        self.in_ptr = time_func("cuda copy", cuda.to_device, input_bytes)
        self.input_bytes_len = len(input_bytes)

    def serialize_output(self):
        output_bytes_len = ListSerializer.project_size(self.candidate_out_repr, self.candidate_out, len(self.rest))
        self.out_ptr = cuda.mem_alloc(output_bytes_len)
        self.output_bytes_len = output_bytes_len

    def prepare_map(self):
        print("preparing map!!!")
        entry_point = time_func("first_call", self.do_first_call)

        assert len(entry_point.args) == 1 # must be a function with one argument
        assert len(entry_point.types) == 1
        assert entry_point.cls is None # must not be a method

        time_func("serialize input", self.serialize_input)
        time_func("serialize output", self.serialize_output)

        self.mapper_kernel = MapperKernel(self.classes, self.functions, entry_point)

    def perform_map(self):
        func = self.mapper_kernel.get_func()
        length = numpy.int32(len(self.rest))
        block_dim, grid_dim = self.get_dims()

        time_func("run kernel", func, self.in_ptr, self.out_ptr, length, block=block_dim, grid=grid_dim)

    def unpack_results(self):
        result_in_bytes = bytearray(self.input_bytes_len)
        result_out_bytes = bytearray(self.output_bytes_len)

        cuda.memcpy_dtoh(result_in_bytes, self.in_ptr)
        cuda.memcpy_dtoh(result_out_bytes, self.out_ptr)

        # unpack into previous objects
        result_in_list = time_func("in_from_bytes", self.in_serializer.from_bytes, result_in_bytes)
        result_in_list.insert(0, self.candidate_in)

        #unpack into new list since the objects did not exist previously
        result_out_list = time_func("out_create_list", self.out_serializer.create_output_list, result_out_bytes, self.candidate_out)
        result_out_list.insert(0, self.candidate_out)

        return result_in_list, result_out_list

def gpumap(func, _list):
    mapper = Mapper(func, _list)
    mapper.prepare_map()
    mapper.perform_map()
    result_in, result_out = time_func("unpack", mapper.unpack_results)
    return result_out




















