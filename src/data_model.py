primitive_map = {int: "i", float: "f", bool: "?"}
built_in_functions = {
    "math": {
        "sin": "sinf",
        "cos": "cosf",
        "tan": "tanf",
        "ceil": "ceilf",
        "floor": "floorf",
        "sqrt": "sqrtf",
        "pow": "powf",
        "log": "logf",
        "log10": "log10f",
        "log1p": "log1pf",
        "log2": "log2f"
    }
}

class Functions:
    def __init__(self):
        self.functions = {}

    def add_functions(self, called_funcs):
        for called_func in filter(lambda f: not f.is_method(), called_funcs):
            self.functions[called_func.name] = FunctionRepresentation(called_func.name, called_func.args,
                                                                      called_func.types, called_func.return_type,
                                                                      called_func.function)

class ExtractedClasses:
    def __init__(self):
        self.classes = {}
        self.type_to_repr = {}

    def _check_real_dependency(self, _type):
        return _type not in primitive_map and _type is not type(None)

    def add_methods(self, called_funcs):
        for called_func in filter(lambda f: f.is_method(), called_funcs):
            method = MethodRepresentation(called_func.cls, called_func.name, called_func.args,
                                          called_func.types, called_func.return_type, called_func.function)
            self.classes[called_func.cls.__name__].add_method(method)

    def extract(self, obj):
        _type = type(obj)
        name = _type.__name__

        if name in self.classes:
            return self.classes[name]

        if _type in primitive_map:
            return _type

        fields = []
        types = []
        raw_type = type(obj)

        for field, value in obj.__dict__.items():
            t = type(value)
            if t not in primitive_map:
                types.append(self.extract(value))
            else:
                types.append(t)
            fields.append(field)

        class_repr = ClassRepresentation(name, raw_type, fields, types)
        self.classes[name] = class_repr
        self.type_to_repr[raw_type] = class_repr
        return class_repr

class ClassRepresentation:
    def __init__(self, name, raw_type, field_names, field_types):
        self.name = name
        self.raw_type = raw_type
        self.field_names = field_names
        self.field_types = field_types
        self.methods = []
        assert len(field_names) == len(field_types)

    def get_format(self):
        fmt = "".join(map(lambda t: t.get_format() if isinstance(t, ClassRepresentation) else primitive_map[t],
                          self.field_types))
        return fmt

    def add_method(self, method):
        self.methods.append(method)

    def __hash__(self):
        return self.name.__hash__()

    def __eq__(self, other):
        return self.name.__eq__(other)


class FunctionRepresentation:
    def __init__(self, name, args, arg_types, return_type, func):
        self.name = name
        self.args = args
        self.arg_types = arg_types
        self.return_type = return_type
        self.func = func

    def has_nonprimitive_args(self):
        return len(list(filter(lambda t: t not in primitive_map, self.arg_types))) > 0

class MethodRepresentation(FunctionRepresentation):
    def __init__(self, cls, *args):
        super().__init__(*args)
        self.cls = cls

    def is_constructor(self):
        return self.name == "__init__"

    def has_nonprimitive_args(self):
        return len(list(filter(lambda t: t not in primitive_map, self.arg_types[1:]))) > 0

    def __repr__(self):
        return "{}.{}".format(self.cls.__name__, self.name)


