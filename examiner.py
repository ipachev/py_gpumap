import sys, inspect

class FunctionCall:
    def __init__(self, cls, name, args, types, function=None):
        self.cls = cls
        self.name = name
        self.args = args
        self.types = types
        self.function = function
        self.return_type = None

    def set_return_type(self, _type):
        self.return_type = _type

    def is_method(self):
        return self.cls is not None

    def __str__(self):
        return str((self.cls, self.name, self.args, self.types, self.return_type, self.function))


class FunctionCallExaminer:
    calls = None
    def __init__(self):
        self.results = []
        self.prev_call = {}

    @classmethod
    def get(cls):
        if FunctionCallExaminer.calls is None:
            FunctionCallExaminer.calls = FunctionCallExaminer()
        return FunctionCallExaminer.calls

    @classmethod
    def runfunc(cls, func, *args):
        FunctionCallExaminer.get().results = []
        sys.settrace(tracefunc)
        ret_val = func(*args)
        sys.settrace(None)
        return ret_val

    @classmethod
    def results(cls):
        return cls.calls.results


    def trace(self, frame, event, arg):
        name = frame.f_code.co_name
        arg_names = frame.f_code.co_varnames[:frame.f_code.co_argcount]
        types = [type(frame.f_locals[var]) for var in arg_names]
        assert len(arg_names) == len(types)
        cls = None
        if len(arg_names) > 0 and arg_names[0] == "self":
            # this is a method
            cls = types[0]

        if event == "call":
            if (cls, name) not in self.prev_call:
                if not cls:
                    func = frame.f_globals[name]
                else:
                    func = next(map(lambda x: x[1], filter(lambda x: x[0] == name,
                                        inspect.getmembers(types[0], lambda t: inspect.isfunction(t)))))
                    print("found {}".format(func))
                call = FunctionCall(cls, name, arg_names, types, func)
                self.results.append(call)
                self.prev_call[(cls, name)] = call
        elif event == "return":
            self.prev_call[(cls, name)].set_return_type(type(arg))



def tracefunc(frame, event, arg):
    FunctionCallExaminer.get().trace(frame, event, arg)
    return tracefunc


from test_util import TestClassA, TestClassB

class RunFunctionCallExaminerTest:
    def test(self):
        FunctionCallExaminer.runfunc(self.do_stuff, TestClassA(1,2,3, TestClassB(4,5,6)))
        results = FunctionCallExaminer.results()

        for result in results:
            print(result)


    def do_stuff(self, o):
        o = TestClassA(o.a, o.a+o.b, o.a+o.b+o.c, TestClassB(o.o.x, o.o.x+o.o.y, o.o.x+o.o.y+o.o.z))
        o.increment_all(11)

if __name__ == "__main__":
    RunFunctionCallExaminerTest().test()
