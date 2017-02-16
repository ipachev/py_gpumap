from time import perf_counter
import os
from collections import defaultdict

results_dir = os.path.join(os.getenv("HOME"), ".ivan_results", "{}".format(perf_counter()))
os.makedirs(results_dir)

class Results:
    results = defaultdict(list)
    columns = ["code generator", "serialize closure vars", "serialize input", "first_call", "run kernel", "deserialize"]

    @staticmethod
    def clear_results():
        Results.results = defaultdict(list)

    @staticmethod
    def output_results():
        with open(os.path.join(results_dir), "output.csv") as f:
            print("first_call,code_gen,serialize,run,deserialize", file=f)
            for code_gen, serialize_closure, serialize_input, first_call, run_kernel, deserialize in zip(
                    Results.results[Results.columns[0]], Results.results[Results.columns[1]],
                    Results.results[Results.columns[2]], Results.results[Results.columns[3]],
                    Results.results[Results.columns[4]], Results.results[Results.columns[5]]):
                print("{},{},{},{},{}".format(first_call, code_gen, serialize_input + serialize_closure, run_kernel,
                                              deserialize), file=f)


def indent(n):
    return 4 * " " * n

def dedent(body):
    lines = body.split("\n")
    out_lines = map(lambda l: l[4:], lines)
    return "\n".join(out_lines)

def time_func(name, func, *args, **kwargs):
    start_time = perf_counter()
    out = func(*args, **kwargs)
    end_time = perf_counter()
    Results.results[name].append(end_time - start_time)
    return out

def get_time(func, *args, **kwargs):
    start_time = perf_counter()
    func(*args, **kwargs)
    end_time = perf_counter()
    return end_time - start_time