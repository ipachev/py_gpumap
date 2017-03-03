builtin = """
#include <stdio.h>

template<typename T, typename... Args>
__device__ void print(T first , Args... args) {}

template <class T>
class ListOfLists {
    public:
        int list_length;
        T items[];
};

template <class T>
class List_Ptr {
    public:
        int length;
        T *items;
        __device__ T& operator [](int i) {return items[i];};
};

template<class T>
__device__ int len(List_Ptr<T> &l) {
    return l.length;
}

template <class T>
class List_PtrIterator {
    public:
        int curr_idx;
        List_Ptr<T> &list;
        __device__ List_PtrIterator(List_Ptr<T> &list) : list(list), curr_idx(0) {};
        __device__ T& next();
        __device__ bool has_next();
};

template <class T>
__device__ T& List_PtrIterator<T>::next() {
    T& next_item = this->list.items[this->curr_idx];
    this->curr_idx += 1;
    return next_item;
}

template <class T>
__device__ bool List_PtrIterator<T>::has_next() {
    return this->curr_idx < this->list.length;
}

template <class T>
class List {
    public:
        int length;
        T items[];
        __device__ T& operator [](int i) {return items[i];};
};

template<class T>
__device__ int len(List<T> &l) {
    return l.length;
}

template <class T>
class ListIterator {
    public:
        int curr_idx;
        List<T> &list;
        __device__ ListIterator(List<T> &list) : list(list), curr_idx(0) {};
        __device__ T& next();
        __device__ bool has_next();
};

template <class T>
__device__ T& ListIterator<T>::next() {
    T& next_item = this->list.items[this->curr_idx];
    this->curr_idx += 1;
    return next_item;
}

template <class T>
__device__ bool ListIterator<T>::has_next() {
    return this->curr_idx < this->list.length;
}

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
    this->last = start;
    this->started = false;
}

__device__ int RangeIterator::next() {
    int next = this->last;
    this->last += step;
    return next;
}

__device__ bool RangeIterator::has_next() {
    if (this->last >= this->stop) {
        return false;
    }
    return true;
}
"""