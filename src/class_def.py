from util import indent

from data_model import primitive_map, ClassRepresentation, convert_float

from collections import defaultdict
import itertools


class ClassDefGenerator:

    def all_cpp_class_defs(self, extracted_classes):
        output_list = []
        for class_repr in extracted_classes.classes.values():
            output_list.append("class {name};".format(name=class_repr.name))

        for class_repr in extracted_classes.classes.values():
            output_list.append(self.cpp_class_def(class_repr))
        return "\n".join(output_list) + "\n"

    def cpp_class_def(self, class_repr):
        output = "class %s {\n" % class_repr.name
        output += indent(1) + "public:\n"

        for arg, _type in zip(class_repr.field_names, class_repr.field_types):
            if isinstance(_type, ClassRepresentation):
                name = _type.name
            else:
                name = convert_float(_type).__name__
            output += indent(2) + "{type} {arg};\n".format(arg=arg, type=name)

        output += indent(2) + "__device__ %s(){};\n" % class_repr.name

        methods = self.methods(class_repr)
        output +=  methods + ("\n" if methods != "" else "")

        output += "};\n"
        return output

    def get_type_label(self, _type, use_refs):
        if _type in primitive_map:
            return _type.__name__
        elif use_refs:
            return _type.__name__ + "&"
        else:
            return _type.__name__ + "&&"

    def methods(self, class_repr):
        protos = []
        for method in class_repr.methods:
            ref_lists = itertools.product([True, False], repeat=len(list(
                filter(lambda a: a not in primitive_map, method.arg_types[1:]))))
            for ref_list in ref_lists:
                iter_ref_list = iter(ref_list)
                whole_ref_list = [True] + [False if t in primitive_map else next(iter_ref_list) for t in method.arg_types[1:]]
                print(method.cls, method.name, whole_ref_list)
                protos.append(self.method(class_repr, method, refs=whole_ref_list))
        return "\n".join(protos)

    def method(self, class_repr, method_repr, refs):
        lines = []
        arg_list = ", ".join(map(
            lambda pair: "{} {}".format(pair[0], pair[1]),
            filter(lambda pair: pair[1] != "self",
                   zip(map(lambda t: self.get_type_label(t[0], t[1]),
                           zip(method_repr.arg_types, refs)), method_repr.args))))
        if method_repr.is_constructor():
            lines.append("__device__ {class_name} ({args});".format(class_name=class_repr.name, args=arg_list))
        else:
            return_type = "void" if method_repr.return_type == type(None) else method_repr.return_type.__name__
            lines.append("__device__ {return_type} {method_name} ({args});".format(
                return_type=return_type,
                method_name=method_repr.name,
                args=arg_list))
        return "\n".join(map(lambda l: indent(2) + l, lines))
