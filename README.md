# llvm-loop-perforation

An LLVM pass that mangles your loops, on purpose! More background and detail in [this blog post][6120].

We use LLVM 9.0.

To build the LLVM passes:

    $ make pass

To run the driver with an existing benchmark or test:

    $ python3 driver.py <test_directory>

This will produce a final, perforated LLVM IR file as:

    $ <test_directory>/<source>-perforated.ll

And executable as:

    $ <test_directory>/perforated.out

To define a new test or benchmark, place the source code inside a directory alongside an implementation of `error.py`. If your application requires input files, place them in the same directory and define them as arguments in a `Makefile`.

[6120]: https://www.cs.cornell.edu/courses/cs6120/2019fa/blog/loop-perforation/
