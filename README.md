# Transparently gpu-accelerated batch operations on lists of homogeneous python objects!

This is part of the work I did for my thesis.
I'm trying to create a gpu-accelerated map function that works with relatively simple functions and objects.
The goal is to allow programmers to create a list of homogenous, arbitrarily nested simple python objects and apply a function to each element in the list!

This depends on pycuda and numpy!

## Guide:

### Map:

* `from mapper import gpumap`
* define a non-lambda function f
* create a list L of objects
* `result_list = gpumap(f, L)``

### Filter:

* `from filterer import gpufilter`
* define a non-lambda function f that returns a boolean describing whether or not to include an item
* create a list L of objects
* `filtered_list = gpufilter(f, L)`

## Limitations:

* Functions must have the same arg types and return type every time they are called
* Returning None is not (yet) supported
* Multiple objects in the input list must not contain references to the same objects
* Objects can only contain other objects, floats, or ints.
* Assignments into an existing variable must be of the same type!
* Strings, lists, and dicts are not yet supported
* The only types of for loops are `for ... in range(...)`or `for ... in <list>`
* Lists can only be passed in as closure variables or as the input list.
* Most built-in funcitons are not implemented
* The input lists and closure lists must not contain references to the same objects.

I currently don't make use of CUDA thread-level dynamic allocation because it's slow when all threads compete for allocations. However, it's possible to implement a good lockless parallel dynamic allocation scheme and that would make it easier to implement a lot more language feautres!

We can also make it so that functions dont need the same arg types and objects dont need the same field types using C++ templates in the generated code!


## Supported Language Features

* function calls
* method calls
* constructor calls
* augmented assignment
* boolean operations
* if statements
* while loops
* for i in range(...) loops
* for item in \<list\> loops
* break and continue
* mathematical operators except `**` (use math.pow)
* comparison operators on integers, floats, and booleans
* unary operators !, -, +, ~
* turnary expression (`a if b else c`)
* mathematical functions such as sqrt, log, etc
* including lists, objects, or primitives as closure variables on the function passed to gpumap is possible
* probably some more stuff i'm leaving out


## How does it work?

Suppose you have a function f, a list L, and L' = map(f, L)

1.  C++ class definitions are created for the python objects' class by inspecting an object's fields
2.  Apply f to L[0] to produce L'[0] and inspect the call using python's self-debugging functionality, taking note of all methods and functions called as well as their return types and arg types.
3.  C++ method and function definitions are created after inspecting the call f(L[0])
4.  All of the elements in L[1:] are inspected and serialized into their corresponding C++ class structures and copied to the gpu
5.  Each gpu thread calls the translated f function on its corresponding element in L[1:] to produce L'[1:]
6.  The gpu-serialized versions of L[1:] and L'[1:] are copied back to the host and are unpacked into normal python objects
7.  L[0] and L'[0] are tacked onto the beginning of the deserialized lists
8.  ????? Profit

## Warning:

This is not very refined but it does seem to work for limited types of python syntax and simple objects!
It also seems to give a decent performance boost when it actually works!

## More info:
http://digitalcommons.calpoly.edu/theses/1704/
