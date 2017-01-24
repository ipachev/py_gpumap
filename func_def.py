import ast, _ast, inspect

from data_model import primitive_map
from util import indent, dedent

# todo: implement FunctionDefGenerator
class FunctionDefGenerator:
    pass

class MethodDefGenerator(FunctionDefGenerator):
    def __init__(self, all_function_calls, extracted_classes):
        # this is used for reference to determine type information
        self.all_function_calls = all_function_calls
        self.extracted_classes = extracted_classes

    def generate(self, class_repr):
        method_outputs = []
        for method_repr in class_repr.methods:
            converter = MethodConverter(class_repr, method_repr, self.all_function_calls, self.extracted_classes.classes.keys())
            method_output = converter.convert()
            method_outputs.append(method_output)

            converter = MethodConverter(class_repr, method_repr, self.all_function_calls,
                                        self.extracted_classes.classes.keys(), True)
            method_output = converter.convert()
            if method_output:
                method_outputs.append(method_output)
        return "\n".join(method_outputs) + "\n"

# todo: migrate function functionality into FunctionConverter instead of MethodConverter

class FunctionConverter(ast.NodeVisitor):
    pass

class MethodConverter(FunctionConverter):
    def __init__(self, class_repr, method_repr, all_functions, all_classes, use_refs=False):
        # class_repr tells us field types
        # method repr tells us arg types and return type
        self.class_repr = class_repr
        self.method_repr = method_repr
        self.use_refs = use_refs
        # local vars store the types of all the local vars
        self.local_vars = {}
        # function list is used for type reference when functions or methods are called
        self.all_functions = all_functions
        self.all_classes = all_classes
        source = "\n".join(dedent(inspect.getsource(self.method_repr.func)))
        self.ast = ast.parse(source)

    def get_func(self, cls, name):
        found = list(filter(lambda f: f.cls == cls and f.name == name))
        assert len(found) == 1
        return found[0]

    def convert(self):
        # if we are not using refs (always generate), otherwise only generate if there are args that are non primitive
        if not self.use_refs or len(list(filter(lambda arg: arg not in primitive_map,
                                                self.method_repr.arg_types[1:]))) > 0:
            # put args as local vars
            for arg, _type in zip(self.method_repr.args, self.method_repr.arg_types):
                self.local_vars[arg] = _type
            out = self.visit(self.ast)
            return out
        return None

    def visit_Module(self, node):
        return self.visit(node.body[0])

    def visit_Name(self, node):
        if node.id == "self":
            return "(*this)"
        else:
            return node.id

    def visit_Attribute(self, node):
        return self.visit(node.value) + "." + node.attr

    def visit_Expr(self, node):
        return self.visit(node.value)

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

    def visit_FunctionDef(self, node):
        arg_list = ", ".join(map(
            lambda pair: "{} {}".format(pair[0], pair[1]),
            filter(lambda pair: pair[1] != "self",
                   zip(map(lambda t: t.__name__ if t in primitive_map or not self.use_refs else "%s&" % t.__name__,
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


