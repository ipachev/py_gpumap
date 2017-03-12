from mapper import gpumap
from random import randint
from pickle import dumps, loads
from util import get_time, Results

class TestSort:
    def prepare(self, size):
        self.lists = [[randint(0, 1000000) for _ in range(size)] for _ in range(1000)]
        pickle_str = dumps(self.lists)
        self.lists2 = loads(pickle_str)
        self.sorted = [sorted(l) for l in self.lists]

    def warmup(self):
        self.prepare(256)
        gpumap(bubblesort, self.lists)
        list(map(bubblesort, self.lists2))
        Results.clear_results()

    def run(self):
        with open("bubble_out.csv", "w") as f:
            print("list_size,num_lists,gpu,cpu",file=f)
            size = 2
            while size <= 8192:
                self.prepare(size)
                gpu = get_time(gpumap, bubblesort, self.lists)
                cpu = get_time(list, map(bubblesort, self.lists2))

                for l1, l2, l3 in zip(self.lists, self.lists2, self.sorted):
                    for i1, i2, i3 in zip(l1, l2, l3):
                        assert i1 == i2 == i3

                print("{},{},{},{}".format(size, 1000, gpu, cpu), file=f)
                f.flush()

                Results.output_results("bubblesort", "results-%d.csv" % size)
                size *= 2

def bubblesort(lst):
    for i in range(len(lst)):
        for j in range(i+1, len(lst)):
            if lst[j] < lst[i]:
                temp = lst[j]
                lst[j] = lst[i]
                lst[i] = temp

if __name__ == "__main__":
    t = TestSort()
    t.warmup()
    t.run()