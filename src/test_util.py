class TestClassA:
    def __init__(self, a, b, c, o):
        self.a = a
        self.b = b
        self.c = c
        self.d = 0
        self.e = TestClassC(1)
        self.o = o

    def increment_all(self, n):
        b = TestClassB(1, 2, n//2)
        r = get_remainder(n, 2)
        self.a += n
        self.b += n
        self.c += n
        self.d += n
        q = 0
        for i in range(99):
            q += i
            while q < 150:
                q += 1

        self.o.increment_all(b)
        self.o.increment_all(TestClassB(1, 2, n // 2 + r))


class TestClassShallow:
    def __init__(self, a,b,c,d,e,f,g,h,i,j):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e
        self.f = f
        self.g = g
        self.h = h
        self.i = i
        self.j = j

    def increment_all(self, n):
        self.a += 1
        self.b += 1
        self.c += 1
        self.d += 1
        self.e += 1
        self.f += 1
        self.g += 1
        self.h += 1
        self.i += 1
        self.j += 1


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
