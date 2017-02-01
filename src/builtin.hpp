#include <stdio.h>

class RangeIterator {
    public:
        int stop;
        int start;
        int step;
        int last;
        bool started;
        __device__ RangeIterator(int, int, int);
        __device__ int next();
        __device__ bool has_next();
};

__device__ RangeIterator::RangeIterator(int start, int stop, int step) {
    this->stop = stop;
    this->start = start;
    this->step = step;
    this->last = start - step;
    this->started = false;
}

__device__ int RangeIterator::next() {
    this->last += step;
    return this->last;
}

__device__ bool RangeIterator::has_next() {
    if (this->last + step >= this->stop) {
        return false;
    }
    return true;
}