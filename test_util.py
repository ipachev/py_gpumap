class TestClassA:
    def __init__(self, a, b, c, o):
        self.a = a
        self.b = b
        self.c = c
        self.d = 0
        self.e = TestClassC()
        self.o = o

    def increment_all(self, n):
        b = TestClassB(1, 2, n/2)
        r = get_remainder(n, 2)
        self.a += n
        self.b += n
        self.c += n
        self.d += n
        self.o.increment_all(b)
        self.o.increment_all(TestClassB(1, 2, n / 2 + r))


def get_remainder(num, dem):
    return num % dem


class TestClassB:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.q = TestClassC()

    def increment_all(self, n):
        self.x += n.z
        self.y += n.z
        self.z += n.z


class TestClassC:
    pass
