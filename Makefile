.PHONY: pass
.PRECIOUS: %-phis.ll

pass:
	cd build; make; cd ..

%.ll: %.c
	clang -emit-llvm -Xclang -disable-O0-optnone -S $< -o $@

%-phis.ll: %.ll
	opt -mem2reg -S $< -o $@

%-perforated.ll: %-phis.ll pass
	opt -load build/loop-perf/libLoopPerforationPass.* -loop-perf -S $< -o $@