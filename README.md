# Transparently gpu-accelerated batch operations on lists of homogeneous python objects!


This is part of the work I'm doing for my thesis.
I'm trying to create a gpu-acclerated map function that works with relatively simple functions and objects.
The goal is to allow programmers to create a list of homogenous, arbitrarily nested simple python objects and apply a function to each element in the list!

This depends on pycuda!

## How does it work?
Suppose you have a function f, a list L, and L' = map(f, L)
1. C++ class definitions are created for the python objects' class by inspecting an object's fields
2. Apply f to L[0] to produce L'[0] and inspect the call using python's self-debugging functionality, taking note of all methods and functions called as well as their return types and arg types.
3. C++ method and function definitions are created after inspecting the call f(L[0])
4. All of the elements in L[1:] are inspected and serialized into their corresponding C++ class structures and copied to the gpu
5. Each gpu thread calls the translated f function on its corresponding element in L[1:] to produce L'[1:]
6. The gpu-serialized versions of L[1:] and L'[1:] are copied back to the host and are unpacked into normal python objects
7. L[0] and L'[0] are tacked onto the beginning of the deserialized lists
8. ????? Profit

## Warning:
This is unfinished!!!!!!
The python->cuda translator is working but(de)serialization is not yet working!
The performance of this probably won't be too great, but I'm sure there's a lot of optimizations to be made!
