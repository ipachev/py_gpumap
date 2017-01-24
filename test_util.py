class TestClassA:
    def __init__(self, a, b, c, o):
        self.a = a
        self.b = b
        self.c = c
        self.d = 0
        self.e = TestClassC()
        self.o = o

    def increment_all(self, n):
        burrito = TestClassB(1, 2, n)
        self.a += n
        self.b += n
        self.c += n
        self.d += n
        self.o.increment_all(burrito.z)


class TestClassB:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.q = TestClassC()

    def increment_all(self, n):
        self.x += n
        self.y += n
        self.z += n


class TestClassC:
    pass
