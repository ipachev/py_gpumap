from time import perf_counter
import os

results_dir = os.path.join(os.getenv("HOME"), ".ivan_results", "{}".format(perf_counter()))
os.makedirs(results_dir)

class Results:
    results = {}
    columns = ["code generator", "serialize closure vars", "serialize input", "first_call", "run kernel", "deserialize", "total"]
    for column in columns:
        results[column] = []

    @staticmethod
    def clear_results():
        for column in Results.columns:
            Results.results[column] = []

    @staticmethod
    def output_results(file_name="output.csv"):
        path = os.path.join(results_dir, file_name)
        print("saving file", path)
        with open(path, "a") as f:
            print("first_call,code_gen,serialize,run,deserialize,total", file=f)
            for code_gen, serialize_closure, serialize_input, first_call, run_kernel, deserialize, total in zip(
                    Results.results[Results.columns[0]], Results.results[Results.columns[1]],
                    Results.results[Results.columns[2]], Results.results[Results.columns[3]],
                    Results.results[Results.columns[4]], Results.results[Results.columns[5]], Results.results[Results.columns[6]]):
                print("{},{},{},{},{},{}".format(first_call, code_gen, serialize_input + serialize_closure, run_kernel,
                                              deserialize,total), file=f)


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
    duration = end_time - start_time
    if name in Results.results:
        Results.results[name].append(duration)
    else:
        print(name, ":", duration)
    return out

def get_time(func, *args, **kwargs):
    start_time = perf_counter()
    func(*args, **kwargs)
    end_time = perf_counter()
    return end_time - start_time