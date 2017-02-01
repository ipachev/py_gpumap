class RangeIterator {
    public:
        int stop;
        int start;
        int step;
        int last;
        __device__ RangeIterator(int, int, int);
        __device__ int next();
        __device__ bool has_next();
};

__device__ RangeIterator::RangeIterator(int start, int stop, int step) {
    this->stop = stop;
    this->start = start;
    this->step = step;
    this->last = start;
}

__device__ int RangeIterator::next() {
    auto val = this->last;
    this->last += step;
    return val;
}

__device__ bool RangeIterator::has_next() {
    if (this->last >= stop) {
        return false;
    }
    return true;
}