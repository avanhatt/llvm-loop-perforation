.PHONY: pass clean
.PRECIOUS: %-phis.ll

RATE ?= 2

clean:
	rm -f {.,tests,benchmarks/*}/*.{ll,bc,out,json}

pass:
	cd build; make; cd ..

%.ll: %.c
	clang -isystem /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/include -emit-llvm -Xclang -disable-O0-optnone -S $< -o $@

%-phis.ll: %.ll
	opt -mem2reg -S $< -o $@
	opt -load build/loop-perf/libLoopPerforationPass.* -loop-count -S -o /dev/null $@

%-perforated.ll: %-phis.ll
	opt -load build/loop-perf/libLoopPerforationPass.* -loop-perf -S $< -o $@ -rate $(RATE)

%.out: %.ll
	clang -O1 $^ -o $@
