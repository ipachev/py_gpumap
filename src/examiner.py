import sys, inspect
from util import time_func

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

from util import time_func

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
        print("running func")
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
        is_method = "self" in frame.f_locals
        curr_obj = None
        if is_method:
            curr_obj = frame.f_locals["self"]
            cls = type(curr_obj)
        else:
            cls = None

        if event == "call":
            if (cls, name) not in self.prev_call:
                arg_names = frame.f_code.co_varnames[:frame.f_code.co_argcount]
                types = [type(frame.f_locals[var]) for var in arg_names]
                if is_method:
                    func = getattr(curr_obj, name)
                else:
                    func = frame.f_globals[name]

                print("found {}".format(func))
                call = FunctionCall(cls, name, arg_names, types, func)
                self.results.append(call)
                self.prev_call[(cls, name)] = call
        elif event == "return":
            prev_call = self.prev_call[(cls, name)]
            if not prev_call.return_type:
                prev_call.set_return_type(type(arg))



def tracefunc(frame, event, arg):
    trace = FunctionCallExaminer.get().trace
    #time_func("trace_func", trace, frame, event, arg)
    trace(frame, event, arg)
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
