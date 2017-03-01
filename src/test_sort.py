from mapper import gpumap
from random import randint
from pickle import dumps, loads
from util import time_func


class TestSort:
    def __init__(self):
        self.lists = [[randint(0, 1000000) for _ in range(1000)] for _ in range(1000)]
        pickle_str = dumps(self.lists)
        self.lists2 = loads(pickle_str)
        self.lists3 = loads(pickle_str)
        self.lists4 = loads(pickle_str)
        self.sorted = []
        for l in self.lists:
            self.sorted.append(sorted(l))

    def run(self):
        time_func("shell gpu", gpumap, shellsort, self.lists)
        time_func("shell cpu", list, map(shellsort, self.lists2))

        time_func("bubble gpu", gpumap, bubblesort, self.lists3)
        time_func("bubble cpu", list, map(bubblesort, self.lists4))

        for l1, l2, l3, l4, l5, i in zip(self.lists, self.lists2, self.lists3, self.lists4, self.sorted, range(len(self.lists))):
            for i1, i2, i3, i4, i5 in zip(l1, l2, l3, l4, l5):
                    assert i1 == i2 == i3 == i4 == i5


def shellsort(items):
    gap = len(items) // 2
    # loop over the gaps
    while gap > 0:
        # do the insertion sort
        for i in range(gap, len(items)):
            val = items[i]
            j = i
            while j >= gap and items[j - gap] > val:
                items[j] = items[j - gap]
                j -= gap
            items[j] = val
        gap //= 2

def bubblesort(lst):
    for i in range(len(lst)):
        for j in range(i+1, len(lst)):
            if lst[j] < lst[i]:
                temp = lst[j]
                lst[j] = lst[i]
                lst[i] = temp


if __name__ == "__main__":
    TestSort().run()