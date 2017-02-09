import sys
from types import BuiltinFunctionType

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
        self.top_level_func = None

    @staticmethod
    def runfunc(func, *args):
        FunctionCallExaminer.calls = FunctionCallExaminer()
        FunctionCallExaminer.calls.top_level_func = func
        sys.settrace(tracefunc)
        ret_val = func(*args)
        sys.settrace(None)
        return ret_val

    @staticmethod
    def results():
        return FunctionCallExaminer.calls.results

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
                if is_method:
                    func = getattr(curr_obj, name)
                else:
                    try:
                        func = frame.f_globals[name]
                    except:
                        # hack to make spark work
                        func = self.top_level_func

                if not isinstance(func, BuiltinFunctionType):
                    arg_names = list(frame.f_code.co_varnames[:frame.f_code.co_argcount])
                    types = [type(frame.f_locals[var]) for var in arg_names]
                    print("found {}".format(func))
                    call = FunctionCall(cls, name, arg_names, types, func)
                    self.results.append(call)
                    self.prev_call[(cls, name)] = call
                else:
                    print("found builtin function {}".format(func))
        elif event == "return":
            if (cls, name) in self.prev_call:
                prev_call = self.prev_call[(cls, name)]
                if not prev_call.return_type:
                    prev_call.set_return_type(type(arg))



def tracefunc(frame, event, arg):
    trace = FunctionCallExaminer.calls.trace
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
