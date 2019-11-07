# llvm-loop-perforation

An LLVM pass that mangles your loops, on purpose!
It's for LLVM 9.

Build:

    $ cd llvm-loop-perforation
    $ mkdir build
    $ cd build
    $ cmake ..
    $ make
    $ cd ..

Run:

    $ clang -S -Xclang -disable-O0-optnone -emit-llvm foo.c
    $ opt -load build/loop-perf/libLoopPerforationPass.* -loop-perf -S foo.ll
