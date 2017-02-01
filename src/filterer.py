import mapper

class Filterer:
    def __init__(self, func, _list):
        self.func = func
        self.list = _list

    def filter(self):
        results = mapper.gpumap(self.func, self.list)
        out_list = filter(lambda r: r[0] is True, zip(results, self.list))
        return out_list

def gpufilter(func, _list):
    return Filterer(func, _list).filter()
