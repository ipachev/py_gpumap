from mapper import gpumap
from random import randint
from pickle import dumps, loads
from util import time_func, Results
1
class TestSort:
    def __init__(self):
        self.lists = [[randint(0, 1000000) for _ in range(1000)] for _ in range(1000)]
        pickle_str = dumps(self.lists)
        self.lists2 = loads(pickle_str)
        self.sorted = [sorted(l) for l in self.lists]

    def run(self):
        time_func("bubble gpu", gpumap, bubblesort, self.lists)
        time_func("bubble cpu", list, map(bubblesort, self.lists2))

        for l1, l2, l3 in zip(self.lists, self.lists2, self.sorted):
            for i1, i2, i3 in zip(l1, l2, l3):
                assert i1 == i2 == i3

        Results.output_results("bubblesort", "output.csv")

def bubblesort(lst):
    for i in range(len(lst)):
        for j in range(i+1, len(lst)):
            if lst[j] < lst[i]:
                temp = lst[j]
                lst[j] = lst[i]
                lst[i] = temp

if __name__ == "__main__":
    TestSort().run()