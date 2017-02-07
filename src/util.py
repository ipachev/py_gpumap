from time import perf_counter

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
    print(name + " :", end_time - start_time)
    return out