import ast, _ast, inspect, itertools

from data_model import primitive_map, built_in_functions
from util import indent, dedent


def get_type_label(_type, use_refs=False):
    name = _type if isinstance(_type, str) else "List_Ptr<%s>" % _type[1].__name__ if isinstance(_type, tuple) else _type.__name__
    if _type in primitive_map:
        return name
    elif use_refs:
        return name + "&"
    else:
        return name + "&&"


class FunctionDefGenerator:
    def all_func_protos(self, func_reprs):
        lines = []
        for func_repr in func_reprs.functions.values():
            ref_lists = itertools.product([True, False], repeat=len(list(filter(lambda a: a not in primitive_map, func_repr.arg_types))))
            for ref_list in ref_lists:
                iter_ref_list = iter(ref_list)
                whole_ref_list = [False if t in primitive_map else next(iter_ref_list) for t in func_repr.arg_types]
                line = self.create_proto(func_repr, whole_ref_list) + "\n"
                lines.append(line)

        return "\n".join(lines)

    def create_proto(self, func_repr, refs):
        if func_repr.return_type is type(None):
            return_type = "void"
        else:
            return_type = func_repr.return_type.__name__

        arg_list = ", ".join(map(
            lambda pair: "{} {}".format(pair[0], pair[1]),
            zip(map(lambda t: get_type_label(t[0], t[1]),
                    zip(func_repr.arg_types, refs)), func_repr.args)))
        line = "__device__ {return_type} {name}({arg_list});".format(return_type=return_type,
                                                                     name=func_repr.name,
                                                                     arg_list=arg_list)
        return line

    def all_func_defs(self, func_reprs):
        lines = []
        for func_repr in func_reprs.functions.values():
            ref_lists = itertools.product([True, False], repeat=len(list(
                filter(lambda a: a not in primitive_map, func_repr.arg_types))))
            for ref_list in ref_lists:
                iter_ref_list = iter(ref_list)
                whole_ref_list = [False if t in primitive_map else next(iter_ref_list) for t in func_repr.arg_types]
                func_conv = FunctionConverter(func_repr, refs=whole_ref_list)
                lines.append(func_conv.convert())

        return "\n".join(lines)


class MethodDefGenerator(FunctionDefGenerator):
    def __init__(self):
        super().__init__()

    def all_method_defs(self, class_repr):
        method_outputs = []
        for method_repr in class_repr.methods:
            ref_lists = itertools.product([True, False], repeat=len(list(
                filter(lambda a: a not in primitive_map, method_repr.arg_types[1:]))))
            for ref_list in ref_lists:
                iter_ref_list = iter(ref_list)
                whole_ref_list = [True] + [False if t in primitive_map else next(iter_ref_list) for t in method_repr.arg_types[1:]]
                converter = MethodConverter(class_repr, method_repr, refs=whole_ref_list)
                method_output = converter.convert()
                method_outputs.append(method_output)
        return "\n".join(method_outputs) + "\n"

class FunctionConverter(ast.NodeVisitor):
    def __init__(self, func_repr, refs=None):
        self.func_repr = func_repr
        self.refs = refs if refs else [False for _ in func_repr.arg_types]
        # local vars store the types of all the local vars
        self.local_vars = {}
        self.ast = None
        self.indent_level = 0
        self.iter_counter = 0
        self.func_defined = False

    def increase_indent(self):
        self.indent_level += 1

    def decrease_indent(self):
        self.indent_level -= 1

    def indent(self):
        return indent(self.indent_level)

    def convert(self):
        source = inspect.getsource(self.func_repr.func)

        #hack to remove indentation
        while source[0] == " ":
            source = dedent(source)
        self.ast = ast.parse(source)

        # put args as local vars
        for arg, _type in zip(self.func_repr.args, self.func_repr.arg_types):
            print("adding type", _type)
            self.local_vars[arg] = _type
        out = self.visit(self.ast)
        return out

    def visit_Module(self, node):
        return self.visit(node.body[0])

    def visit_Name(self, node):
        return node.id

    def visit_Attribute(self, node):
        return self.visit(node.value) + "." + node.attr

    def visit_Expr(self, node):
        return self.visit(node.value)

    def visit_Yield(self, node):
        raise SyntaxError("GPUMAP: generators not supported")

    def visit_YieldFrom(self, node):
        raise SyntaxError("GPUMAP: generators not supported")

    def visit_Lambda(self, node):
        raise SyntaxError("GPUMAP: lambdas not supported")

    def visit_Bytes(self, node):
        raise SyntaxError("GPUMAP: bytes not supported")

    def visit_Set(self, node):
        raise SyntaxError("GPUMAP: set not supported")

    def visit_Dict(self, node):
        raise SyntaxError("GPUMAP: dict not supported")

    def visit_Ellipsis(self, node):
        raise SyntaxError("GPUMAP: ellipsis not supported")

    def visit_List(self, node):
        raise SyntaxError("GPUMAP: list declaration not supported")

    def visit_Tuple(self, node):
        raise SyntaxError("GPUMAP: tuple declaration not supported")

    def visit_Starred(self, node):
        raise SyntaxError("GPUMAP: star notation not supported")

    def visit_Import(self, node):
        raise SyntaxError("GPUMAP: import not supported in function body")

    def visit_ImportFrom(self, node):
        raise SyntaxError("GPUMAP: import not supported in function body")

    def visit_Assign(self, node):
        if len(node.targets) > 1:
            raise SyntaxError("GPUMAP: multiple assignment not supported")

        target_types = map(lambda target: type(target), node.targets)
        if tuple in target_types or list in target_types:
            raise SyntaxError("GPUMAP: No unpacking allowed")


        target = node.targets[0]
        # assignment into object field
        output = ""

        value = self.visit(node.value)

        # assignment into variable
        if isinstance(target, _ast.Name):
            # assignment into new variable
            # not sure about the type just yet..

            # see if it's a primitive
            if target.id not in self.local_vars:
                # binops and boolops return primitives
                if isinstance(node.value, _ast.Num) or isinstance(node.value, _ast.Compare) or isinstance(node.value, _ast.BinOp) \
                        or isinstance(node.value, _ast.BoolOp) or isinstance(node.value, _ast.NameConstant):
                    output += "auto "

                # check if referenced list contains primitives
                elif isinstance(node.value, _ast.Subscript):
                    list_name = value[:value.find("[")]
                    try:
                        idx = self.func_repr.args.index(list_name)
                        t = self.func_repr.arg_types[idx]
                        item_type = t[t.find("<") + 1: t.find(">")]
                        if item_type in map(lambda t: t.__name__, primitive_map.keys()):
                            output += "auto "
                        else:
                            output += "auto&& "
                    except:
                        raise RuntimeError("THIS SHOULD NEVER HAPPEN")
                else:
                    # check if it's an existing variable
                    try:
                        idx = self.func_repr.args.index(value)
                        t = self.func_repr.arg_types[idx]
                        if t in primitive_map:
                            output += "auto "
                        else:
                            output += "auto&& "
                    except ValueError:
                        output += "auto&& "
                self.local_vars[target.id] = None
        output += self.visit(target)
        output += " = " + value
        return output

    def visit_Call(self, node):
        if node.keywords:
            raise SyntaxError("GPUMAP: keywords not supported")

        name = self.visit(node.func)
        split_name = name.split(".")
        found = True
        func = built_in_functions
        for piece in split_name:
            if piece not in func:
                found = False
            else:
                func = func[piece]
        if found and isinstance(func, str):
            name = func

        return name + "(" + ", ".join(map(lambda a: self.visit(a), node.args)) + ")"

    def visit_Subscript(self, node):
        return self.visit(node.value) + self.visit(node.slice)

    def visit_Is(self, node):
        raise SyntaxError("GPUMAP: is is not supported")

    def visit_IsNot(self, node):
        raise SyntaxError("GPUMAP: is not is not supported")

    def visit_In(self, node):
        raise SyntaxError("GPUMAP: in is not supported")

    def visit_NotIn(self, node):
        raise SyntaxError("GPUMAP: not in is not supported")

    def visit_Index(self, node):
        return "[" + self.visit(node.value) + "]"

    def visit_Slice(self, node):
        raise SyntaxError("GPUMAP: list slice not supported")

    def visit_ExtSlice(self, node):
        raise SyntaxError("GPUMAP: list slice not supported")

    def visit_ListComp(self, node):
        raise SyntaxError("GPUMAP: list comp not supported")

    def visit_SetComp(self, node):
        raise SyntaxError("GPUMAP: set comp not supported")

    def visit_GeneratorExp(self, node):
        raise SyntaxError("GPUMAP: generator exp not supported")

    def visit_DictComp(self, node):
        raise SyntaxError("GPUMAP: dict comp not supported")

    def visit_Raise(self, node):
        raise SyntaxError("GPUMAP: raising exceptions not supported")

    def visit_Assert(self, node):
        raise SyntaxError("GPUMAP: assert not supported")

    def visit_Delete(self, node):
        raise SyntaxError("GPUMAP: delete not supported")

    def visit_Try(self, node):
        raise SyntaxError("GPUMAP: try not supported")

    def visit_With(self, node):
        raise SyntaxError("GPUMAP: with not supported")

    def visit_Global(self, node):
        raise SyntaxError("GPUMAP: global not supported")

    def visit_Nonlocal(self, node):
        raise SyntaxError("GPUMAP: nonlocal not supported")

    def visit_ClassDef(self, node):
        raise SyntaxError("GPUMAP: class def not supported in function body")

    def visit_AsyncFunctionDef(self, node):
        raise SyntaxError("GPUMAP: async function def not supported")

    def visit_Await(self, node):
        raise SyntaxError("GPUMAP: await not supported")

    def visit_AsyncFor(self, node):
        raise SyntaxError("GPUMAP: async for not supported")

    def visit_AsyncWith(self, node):
        raise SyntaxError("GPUMAP: async with not supported")

    def visit_AugAssign(self, node):
        target = self.visit(node.target)
        return target + " = " + target + self.visit(node.op) + self.visit(node.value)

    def visit_Return(self, node):
        return "return" + ((" " + self.visit(node.value)) if node.value else "")

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

    def visit_FloorDiv(self, node):
        return " / "

    def visit_Mod(self, node):
        return " % "

    def visit_MatMult(self, node):
        raise SyntaxError("GPUMAP: matrix multiply operator not supported")

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

    def visit_BoolOp(self, node):
        output = self.visit(node.values[0])
        for value in node.values[1:]:
            output += self.visit(node.op) + self.visit(value)
        output = "(" + output + ")"
        return output

    def visit_Pass(self, node):
        return ""

    def visit_Str(self, node):
        return "\"{str}\"".format(str=node.s)

    def visit_BinOp(self, node):
        if isinstance(node.op, _ast.Pow):
            return "pow(" + self.visit(node.left) + ", " + self.visit(node.right) + ")"
        output = "(" + self.visit(node.left) + self.visit(node.op) + self.visit(node.right) + ")"
        if isinstance(node.op, _ast.FloorDiv):
            output = "int" + output
        return output

    def visit_UnaryOp(self, node):
        return "(" + self.visit(node.op) + self.visit(node.operand) + ")"

    def visit_UAdd(self, node):
        return "+"

    def visit_USub(self, node):
        return "-"

    def visit_Not(self, node):
        return "!"

    def visit_Invert(self, node):
        return "~"

    def visit_NameConstant(self, node):
        if node.value == True:
            return "true"
        elif node.value == False:
            return "false"
        else:
            return "null"

    def visit_IfExp(self, node):
        return "(" + self.visit(node.test) + " ? " + self.visit(node.body) + " : " + self.visit(node.orelse) + ")"

    def semicolon(self, stmt):
        if not isinstance(stmt, _ast.If) and not isinstance(stmt, _ast.While) and not isinstance(stmt, _ast.For):
            return ";"
        else:
            return ""

    def visit_Break(self, node):
        return "break"

    def visit_Continue(self, node):
        return "continue"

    def visit_Compare(self, node):
        output = self.visit(node.left) + self.visit(node.ops[0]) + self.visit(node.comparators[0])
        last_comp = node.comparators[0]

        for op, comp in zip(node.ops[1:], node.comparators[1:]):
            output += " && " + self.visit(last_comp) + self.visit(op) + self.visit(comp)
            last_comp = comp
        return "(" + output + ")"

    def visit_While(self, node):
        lines = []
        lines.append("while (%s) {" % self.visit(node.test))
        self.increase_indent()
        for stmt in node.body:
            lines.append(self.indent() + self.visit(stmt) + self.semicolon(stmt))
        self.decrease_indent()
        lines.append(self.indent() + "}")
        return "\n".join(lines)

    def visit_For(self, node):
        if isinstance(node.target, _ast.Name):
            target = node.target.id
            if isinstance(node.iter, _ast.Call) and isinstance(node.iter.func, _ast.Name):
                if node.iter.func.id == "range":
                    return self.for_range(node, target)
                else:
                    raise SyntaxError("GPUMAP: Only for ... in range(...) is supported!")

            elif isinstance(node.iter, _ast.Name):
                if node.iter.id in self.local_vars:
                    var_type = self.local_vars[node.iter.id]
                    if isinstance(var_type, str) and var_type.startswith("List<"):
                        list_type = var_type[var_type.find("<") + 1: var_type.rfind(">")]
                        return self.for_list(node, list_type, target)
                    elif isinstance(var_type, str) and var_type.startswith("List_Ptr<"):
                        list_type = var_type[var_type.find("<") + 1: var_type.rfind(">")]
                        return self.for_list(node, list_type, target, ptr=True)
                    else:
                        raise SyntaxError("GPUMAP: cannot iterate over a non-list type")
                else:
                    raise SyntaxError("GPUMAP: no such variable found: " + node.iter.id)
        else:
            raise SyntaxError("GPUMAP: Only one variable can be assigned in a for loop!")



    def for_list(self, node, list_type, target, ptr=False):
        lines = []
        self.iter_counter += 1
        this_iterator = "__iterator_%d" % self.iter_counter
        iter = "List_PtrIterator" if ptr else "ListIterator"
        lines.append("auto %s = %s<%s>(%s);" % (this_iterator, iter, list_type, node.iter.id))
        lines.append(
            self.indent() +
            "while ({iter}.has_next()) {{".format(list_type=list_type,
                                                  target=target,
                                                  iter=this_iterator))
        self.increase_indent()
        lines.append(self.indent() + "{} &{} = {}.next();".format(list_type, target, this_iterator))
        for stmt in node.body:
            lines.append(self.indent() + self.visit(stmt) + self.semicolon(stmt))
        self.decrease_indent()
        lines.append(self.indent() + "}")
        return "\n".join(lines)

    def for_range(self, node, target):
        lines = []
        self.iter_counter += 1
        this_iterator = "__iterator_%d" % self.iter_counter


        start = "0"
        step = "1"
        args_len = len(node.iter.args)
        if args_len == 1:
            stop = self.visit(node.iter.args[0])
        elif args_len == 2:
            start = self.visit(node.iter.args[0])
            stop = self.visit(node.iter.args[1])
        elif args_len == 3:
            start = self.visit(node.iter.args[0])
            stop = self.visit(node.iter.args[1])
            step = self.visit(node.iter.args[2])
        else:
            raise SyntaxError("GPUMAP: bad usage of range")

        arg_str = ", ".join((start, stop, step))
        lines.append("auto %s = RangeIterator(%s);" % (this_iterator, arg_str))
        lines.append(
            self.indent() + "while({iter}.has_next()) {{".format(target=target, iter=this_iterator))
        self.increase_indent()
        lines.append(self.indent() + "int {} = {}.next();".format(target, this_iterator))
        for stmt in node.body:
            lines.append(self.indent() + self.visit(stmt) + self.semicolon(stmt))
        self.decrease_indent()
        lines.append(self.indent() + "}")
        return "\n".join(lines)

    def visit_If(self, node):
        lines = []
        lines.append("if (%s) {" % self.visit(node.test))
        self.increase_indent()
        for stmt in node.body:
            line = self.indent() + self.visit(stmt) + self.semicolon(stmt)
            lines.append(line)
        self.decrease_indent()
        if node.orelse:
            lines.append(self.indent() + "} else {")
            self.increase_indent()
            for stmt in node.orelse:
                lines.append(self.indent() + self.visit(stmt) + self.semicolon(stmt))
            self.decrease_indent()
        lines.append(self.indent() + "}")
        return "\n".join(lines)

    def visit_FunctionDef(self, node):
        if self.func_defined:
            raise SyntaxError("GPUMAP: function definition not supported in function body")

        self.func_defined = True
        arg_list = ", ".join(map(
            lambda pair: "{} {}".format(pair[0], pair[1]),
               zip(map(lambda t: get_type_label(t[0], t[1]),
                       zip(self.func_repr.arg_types, self.refs)), self.func_repr.args)))

        func_name = self.func_repr.name
        if self.func_repr.return_type == type(None):
            return_type = "void"
        else:
            return_type = self.func_repr.return_type.__name__

        lines = []
        lines.append("__device__ %s %s(%s) {" % (return_type, func_name, arg_list))
        self.increase_indent()
        for n in node.body:
            lines.append(self.indent() + self.visit(n) + self.semicolon(n))
        self.decrease_indent()
        lines.append("}\n")
        return "\n".join(lines)


class MethodConverter(FunctionConverter):
    def __init__(self, class_repr, method_repr, *args, **kwargs):
        super().__init__(method_repr, *args, **kwargs)
        # class_repr tells us field types
        # method repr tells us arg types and return type
        self.class_repr = class_repr
        self.method_repr = method_repr

    def convert(self):
        source = dedent(inspect.getsource(self.func_repr.func))
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
        if len(node.targets) > 1:
            raise SyntaxError("GPUMAP: multiple assignment not supported")

        target_types = map(lambda target: type(target), node.targets)
        if tuple in target_types or list in target_types:
            raise SyntaxError("GPUMAP: No unpacking allowed")

        target = node.targets[0]
        value = self.visit(node.value)
        # assignment into object field
        output = ""
        if isinstance(target, _ast.Attribute) and isinstance(target.value, _ast.Name) and target.value.id == "self":
            if target.attr not in self.class_repr.field_names:
                raise SyntaxError("GPUMAP: All fields must be declared and assigned in the constructor prior to re-assignment!")
        # assignment into variable
        elif isinstance(target, _ast.Name):
            # assignment into new variable
            # not sure about the type just yet..

            # see if it's a primitive
            # see if it's a primitive
            if target.id not in self.local_vars:
                if isinstance(node.value, _ast.Attribute) and isinstance(node.value.value, _ast.Name) and node.value.value.id == "self":
                    try:
                        idx = self.class_repr.field_names.index(node.value.attr)
                        t = self.class_repr.field_types[idx]
                        if t in primitive_map:
                            output += "auto "
                        else:
                            output += "auto&& "
                    except ValueError:
                        raise RuntimeError("SHOULD NEVER HAPPEN!!!")

                # binops and boolops return primitives
                elif isinstance(node.value, _ast.Num) or isinstance(node.value, _ast.Compare) or isinstance(node.value,
                                                                                                          _ast.BinOp) \
                        or isinstance(node.value, _ast.BoolOp) or isinstance(node.value, _ast.NameConstant):
                    output += "auto "

                # check if referenced list contains primitives
                elif isinstance(node.value, _ast.Subscript):
                    list_name = value[:value.find("[")]
                    try:
                        idx = self.func_repr.args.index(list_name)
                        t = self.func_repr.arg_types[idx]
                        item_type = t[t.find("<") + 1: t.find(">")]
                        if item_type in map(lambda t: t.__name__, primitive_map.keys()):
                            output += "auto "
                        else:
                            output += "auto&& "
                    except:
                        raise RuntimeError("THIS SHOULD NEVER HAPPEN")
                else:
                    # check if it's an existing variable
                    try:
                        idx = self.func_repr.args.index(value)
                        t = self.func_repr.arg_types[idx]
                        if t in primitive_map:
                            output += "auto "
                        else:
                            output += "auto&& "
                    except ValueError:
                        output += "auto&& "
                self.local_vars[target.id] = None
        output += self.visit(target)
        output += " = " + value
        return output


    def visit_FunctionDef(self, node):
        if self.func_defined:
            raise SyntaxError("GPUMAP: function definition not supported in function body")

        self.func_defined = True
        arg_list = ", ".join(map(
            lambda pair: "{} {}".format(pair[0], pair[1]),
            filter(lambda pair: pair[1] != "self",
                   zip(map(lambda t: get_type_label(t[0], t[1]),
                           zip(self.method_repr.arg_types, self.refs)), self.method_repr.args))))

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

        lines = []
        lines.append("__device__ %s%s::%s(%s) {" % (return_type,
                                                  self.class_repr.name,
                                                  method_name,
                                                  arg_list))
        self.increase_indent()
        for n in node.body:
            lines.append(self.indent() + self.visit(n) + ";")
        self.decrease_indent()
        lines.append("}\n")
        return "\n".join(lines)


