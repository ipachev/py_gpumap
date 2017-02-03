class TestClassA:
    def __init__(self, a, b, c, o):
        self.a = a
        self.b = b
        self.c = c
        self.d = 0
        self.q = 0
        for i in range(99):
            self.q += 1
        self.e = TestClassC(1)
        self.o = o

    def increment_all(self, n):
        b = TestClassB(1, 2, n // 2)
        r = get_remainder(n, 2)
        self.a += n
        self.b += n
        self.c += n
        self.d += n
        self.o.increment_all(b)
        self.o.increment_all(TestClassB(1, 2, n // 2 + r))


def get_remainder(num, dem):
    if dem == 0:
        return -1
    elif num == 0:
        return 0
    elif num > 0:
        while num > 0:
            num -= dem
        return dem + num
    else:
        return -1


class TestClassB:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.q = TestClassC(1)

    def increment_all(self, b):
        self.x += b.z
        self.y += b.z
        self.z += b.z


class TestClassC:
    def __init__(self, i):
        self.i = i
