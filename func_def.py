import ast, _ast, inspect

from data_model import primitive_map
from util import indent, dedent

# todo: implement FunctionDefGenerator
class FunctionDefGenerator:
    def __init__(self, all_function_calls, extracted_classes):
        # this is used for reference to determine type information
        self.all_function_calls = all_function_calls
        self.extracted_classes = extracted_classes

    def get_type_label(self, _type, use_refs=False):
        if _type in primitive_map:
            return _type.__name__
        elif use_refs:
            return _type.__name__ + "&"
        else:
            return _type.__name__ + "&&"

    def all_func_protos(self, func_reprs):
        lines = []

        for func_repr in func_reprs.functions.values():
            line = self.create_proto(func_repr) + "\n"
            lines.append(line)

            if func_repr.has_nonprimitive_args():
                line = self.create_proto(func_repr, True) + "\n"
                lines.append(line)
        return "\n".join(lines)

    def create_proto(self, func_repr, use_ref=False):
        if func_repr.return_type is type(None):
            return_type = "void"
        else:
            return_type = func_repr.return_type.__name__

        arg_list = ", ".join(map(
            lambda pair: "{} {}".format(pair[0], pair[1]),
            zip(map(lambda t: self.get_type_label(t, use_ref),
                    func_repr.arg_types), func_repr.args)))
        line = "__device__ {return_type} {name}({arg_list});".format(return_type=return_type,
                                                                     name=func_repr.name,
                                                                     arg_list=arg_list)
        return line

    def all_func_defs(self, func_reprs):
        lines = []
        for func_repr in func_reprs.functions.values():
            func_conv = FunctionConverter(func_repr, self.all_function_calls, self.extracted_classes)
            lines.append(func_conv.convert())

            if func_repr.has_nonprimitive_args():
                func_conv = FunctionConverter(func_repr, self.all_function_calls, self.extracted_classes, True)
                lines.append(func_conv.convert())

        return "\n".join(lines)


class MethodDefGenerator(FunctionDefGenerator):
    def __init__(self, *args):
        super().__init__(*args)

    def all_method_defs(self, class_repr):
        method_outputs = []
        for method_repr in class_repr.methods:
            converter = MethodConverter(class_repr, method_repr, self.all_function_calls, self.extracted_classes.classes.keys())
            method_output = converter.convert()
            method_outputs.append(method_output)
            if method_repr.has_nonprimitive_args():
                converter = MethodConverter(class_repr, method_repr, self.all_function_calls,
                                        self.extracted_classes.classes.keys(), True)
                method_output = converter.convert()
                method_outputs.append(method_output)
        return "\n".join(method_outputs) + "\n"

class FunctionConverter(ast.NodeVisitor):
    def __init__(self, func_repr, all_functions, all_classes, use_refs=False):
        self.func_repr = func_repr
        self.use_refs = use_refs
        # local vars store the types of all the local vars
        self.local_vars = {}
        # function list is used for type reference when functions or methods are called
        self.all_functions = all_functions
        self.all_classes = all_classes
        self.ast = None

    def get_func(self, cls, name):
        found = list(filter(lambda f: f.cls == cls and f.name == name))
        assert len(found) == 1
        return found[0]

    def convert(self):
        print(self.func_repr.func)
        source = inspect.getsource(self.func_repr.func)
        self.ast = ast.parse(source)
        # put args as local vars
        for arg, _type in zip(self.func_repr.args, self.func_repr.arg_types):
            self.local_vars[arg] = _type
        out = self.visit(self.ast)
        return out

    def visit(self, node):
        print("visiting {}".format(node))
        return super().visit(node)

    def visit_Module(self, node):
        return self.visit(node.body[0])

    def visit_Name(self, node):
        return node.id

    def visit_Attribute(self, node):
        return self.visit(node.value) + "." + node.attr

    def visit_Expr(self, node):
        return self.visit(node.value)

    def visit_Assign(self, node):
        target = node.targets[0]
        # assignment into object field
        output = ""
        if isinstance(target, _ast.Attribute):
            output += self.visit(target)

        # assignment into variable
        elif isinstance(target, _ast.Name):
            # assignment into new variable
            # not sure about the type just yet..
            if target.id not in self.local_vars:
                output += "auto "
                self.local_vars[target.id] = None
            output += self.visit(target)

        output += " = " + self.visit(node.value)
        return output

    def visit_Call(self, node):
        return self.visit(node.func) + "(" + ", ".join(map(lambda a: self.visit(a), node.args)) + ")"

    def visit_AugAssign(self, node):
        target = self.visit(node.target)
        return target + " = " + target + self.visit(node.op) + self.visit(node.value)

    def visit_Return(self, node):
        return "return " + self.visit(node.value)

    def visit_Num(self, node):
        return str(node.n)

    def visit_Add(self, node):
        return " + "

    def visit_Sub(self, node):
        return " - "

    def visit_Mult(self, node):
        return " * "

    def visit_Div(self, node):
        return " / "

    def visit_Mod(self, node):
        return " % "

    def visit_LShift(self, node):
        return " << "

    def visit_RShift(self, node):
        return " >> "

    def visit_BitOr(self, node):
        return " | "

    def visit_BitAnd(self, node):
        return " & "

    def visit_BitXor(self, node):
        return " ^ "

    def visit_And(self, node):
        return " && "

    def visit_Or(self, node):
        return " || "

    def visit_Eq(self, node):
        return " == "

    def visit_NotEq(self, node):
        return " != "

    def visit_Lt(self, node):
        return " < "

    def visit_LtE(self, node):
        return " <= "

    def visit_Gt(self, node):
        return " > "

    def visit_GtE(self, node):
        return " >= "

    def visit_BinOp(self, node):
        return self.visit(node.left) + self.visit(node.op) + self.visit(node.right)

    def visit_FunctionDef(self, node):
        arg_list = ", ".join(map(
            lambda pair: "{} {}".format(pair[0], pair[1]),
               zip(map(lambda t: self.get_type_label(t),
                       self.func_repr.arg_types), self.func_repr.args)))

        func_name = self.func_repr.name
        if self.func_repr.return_type == type(None):
            return_type = "void"
        else:
            return_type = self.func_repr.return_type.__name__

        output = "__device__ %s %s(%s) {\n" % (return_type, func_name, arg_list)
        lines = []
        for n in node.body:
            lines.append(indent(1) + self.visit(n) + ";")

        output += "\n".join(lines)
        output += "\n}\n"
        return output

    def get_type_label(self, _type):
        if _type in primitive_map:
            return _type.__name__
        elif self.use_refs:
            return _type.__name__ + "&"
        else:
            return _type.__name__ + "&&"


class MethodConverter(FunctionConverter):
    def __init__(self, class_repr, method_repr, *args):
        super().__init__(method_repr, *args)
        # class_repr tells us field types
        # method repr tells us arg types and return type
        self.class_repr = class_repr
        self.method_repr = method_repr

    def convert(self):
        source = "\n".join(dedent(inspect.getsource(self.func_repr.func)))
        self.ast = ast.parse(source)
        # put args as local vars
        for arg, _type in zip(self.method_repr.args, self.method_repr.arg_types):
            self.local_vars[arg] = _type
        out = self.visit(self.ast)
        return out

    def visit_Name(self, node):
        if node.id == "self":
            return "(*this)"
        else:
            return node.id

    def visit_Assign(self, node):
        target = node.targets[0]
        # assignment into object field
        output = ""
        if isinstance(target, _ast.Attribute) and isinstance(target.value, _ast.Name) and target.value.id == "self":
            if target.attr not in self.class_repr.field_names:
                raise Exception("All fields must be declared in the constructor prior to assignment!")
            output += self.visit(target)

        # assignment into variable
        elif isinstance(target, _ast.Name):
            # assignment into new variable
            # not sure about the type just yet..
            if target.id not in self.local_vars:
                output += "auto "
                self.local_vars[target.id] = None
            output += self.visit(target)

        output += " = " + self.visit(node.value)
        return output


    def visit_FunctionDef(self, node):
        arg_list = ", ".join(map(
            lambda pair: "{} {}".format(pair[0], pair[1]),
            filter(lambda pair: pair[1] != "self",
                   zip(map(lambda t: self.get_type_label(t),
                           self.method_repr.arg_types), self.method_repr.args))))

        if self.method_repr.is_constructor():
            return_type = ""
            method_name = self.class_repr.name
        else:
            method_name = self.method_repr.name
            if self.method_repr.return_type == type(None):
                return_type = "void"
            else:
                return_type = self.method_repr.return_type.__name__
            return_type += " "

        output = "__device__ %s%s::%s(%s) {\n" % (return_type,
                                                  self.class_repr.name,
                                                  method_name,
                                                  arg_list)
        lines = []
        for n in node.body:
            lines.append(indent(1) + self.visit(n) + ";")

        output += "\n".join(lines)
        output += "\n}\n"
        return output


