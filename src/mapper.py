from examiner import FunctionCallExaminer
from data_model import ExtractedClasses, Functions, ClassRepresentation
from serialization import ListSerializer, ItemSerializer
from util import time_func
from class_def import ClassDefGenerator
from func_def import FunctionDefGenerator, MethodDefGenerator

from pycuda import autoinit
import pycuda.driver as cuda
from pycuda.compiler import SourceModule
import os
import numpy
from operator import itemgetter

from builtin import builtin


_main_func = """
extern "C" {{
#include <stdio.h>
__global__ void map_kernel(List<{in_type}> *in, List<{out_type}> *out, int length{closure_params}) {{
    int thread_id = blockIdx.x * blockDim.x + threadIdx.x;
    if (thread_id < length) {{
        {in_type} &in_item = in->items[thread_id];
        out->items[thread_id] = {func_name}(in_item{closure_args});
    }}
}}
}}
"""


class MapperKernel:
    def __init__(self, classes, functions, entry_point, list_classes, closure_vars):
        self.classes = classes
        self.functions = functions
        self.source_module = None
        self.func = None
        self.entry_point = entry_point
        self.includes = [builtin]
        self.list_classes = set(list_classes)
        self.closure_vars = closure_vars

    def _create_includes(self):
        items = []
        for include in self.includes:
            items.append(include)
        return "\n".join(items)

    def create_closure_params(self):
        if self.closure_vars:
            params = []
            for name, class_repr, is_list in self.closure_vars:
                type_name = class_repr.name if isinstance(class_repr, ClassRepresentation) else class_repr.__name__
                if is_list:
                    param = "List<{type}> *{var_name}".format(type=type_name, var_name=name)
                else:
                    param = "{type} *{var_name}".format(type=type_name, var_name=name)
                params.append(param)
            return ", " + ", ".join(params)
        else:
            return ""

    def create_closure_args(self):
        args = ", ".join(map(lambda v: "*" + v[0], self.closure_vars))
        return ", " + args if args else ""

    def _build_kernel(self):
        cls_def_gen = ClassDefGenerator()

        kernel = self._create_includes() + "\n"

        kernel += cls_def_gen.all_cpp_class_defs(self.classes)

        func_repr = self.functions.functions[self.entry_point.name]
        for name, class_repr, is_list in self.closure_vars:
            type_name = class_repr.name if isinstance(class_repr, ClassRepresentation) else class_repr.__name__
            if is_list:
                func_repr.arg_types.append("List<{type_name}>".format(type_name=type_name))
            else:
                func_repr.arg_types.append("{type_name}".format(type_name=type_name))
            func_repr.args.append(name)

        fn_def_gen = FunctionDefGenerator()
        kernel += fn_def_gen.all_func_protos(self.functions) + "\n"
        kernel += fn_def_gen.all_func_defs(self.functions) + "\n"

        method_gen = MethodDefGenerator()
        for class_repr in self.classes.classes.values():
            kernel += method_gen.all_method_defs(class_repr)

        in_type = self.entry_point.types[0].__name__
        out_type = self.entry_point.return_type.__name__
        func_name = self.entry_point.name

        closure_params = self.create_closure_params()
        closure_args = self.create_closure_args()

        kernel += _main_func.format(in_type=in_type, out_type=out_type,
                                    func_name=func_name, closure_params=closure_params, closure_args=closure_args)
        #print(kernel)
        return kernel

    def _build_module(self):
        kernel = time_func("code generator", self._build_kernel)
        options = []
        options.append("--std=c++11")
        options.append("-Wno-deprecated-gpu-targets")
        self.source_module = SourceModule(kernel, options=options, no_extern_c=True)
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

        self.closure_vars = None

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

    @staticmethod
    def get_closure_binding(func):
        if func.__closure__:
            return zip(func.__code__.co_freevars, map(lambda c: c.cell_contents, func.__closure__))
        else:
            return iter(())

    def prepare_closure_vars(self):
        self.closure_vars = []
        for name, obj in self.get_closure_binding(self.func):
            print("added ", name, "to closure")
            if isinstance(obj, list):
                class_repr = self.classes.extract(obj[0])
                serializer = ListSerializer(class_repr, obj)
                is_list = True
            else:
                class_repr = self.classes.extract(obj)
                serializer = ItemSerializer(class_repr, obj)
                is_list = False

            data = serializer.to_bytes()
            data_len = len(data)
            ptr = cuda.to_device(data)
            self.closure_vars.append((name, serializer, ptr, data_len, class_repr, is_list))

    def prepare_kernel(self, entry_point):
        list_types = [self.candidate_in_repr, self.candidate_out_repr]
        list_types.extend(map(itemgetter(4), self.closure_vars))
        closure_var_names = list(map(lambda x: (x[0], x[4], x[5]), self.closure_vars))
        return MapperKernel(self.classes, self.functions, entry_point, list_types, closure_var_names)

    def prepare_map(self):
        print("preparing map!!!")
        entry_point = time_func("first_call", self.do_first_call)

        assert len(entry_point.args) == 1 # must be a function with one argument
        assert len(entry_point.types) == 1
        assert entry_point.cls is None # must not be a method

        time_func("serialize input", self.serialize_input)
        time_func("serialize output", self.serialize_output)

        time_func("prepare closure vars", self.prepare_closure_vars)
        self.mapper_kernel = self.prepare_kernel(entry_point)

    def perform_map(self):
        func = self.mapper_kernel.get_func()
        length = numpy.int32(len(self.rest))
        block_dim, grid_dim = self.get_dims()
        closure_args = list(map(itemgetter(2), self.closure_vars))
        time_func("run kernel", func, self.in_ptr, self.out_ptr, length, *closure_args, block=block_dim, grid=grid_dim)

    def deserialize_closure_vars(self):
        for name, serializer, ptr, data_len, class_repr, is_list in self.closure_vars:
            incoming_bytes = bytearray(data_len)
            cuda.memcpy_dtoh(incoming_bytes, ptr)
            serializer.from_bytes(incoming_bytes)

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

        time_func("deserialize closure vars", self.deserialize_closure_vars)

        return result_in_list, result_out_list


def gpumap(func, _list):
    mapper = Mapper(func, _list)
    mapper.prepare_map()
    mapper.perform_map()
    result_in, result_out = time_func("unpack", mapper.unpack_results)
    return result_out




















