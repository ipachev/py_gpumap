def indent(n):
    return 4 * " " * n

def dedent(body):
    lines = body.split("\n")
    out_lines = map(lambda l: l[4:], lines)
    return list(out_lines)