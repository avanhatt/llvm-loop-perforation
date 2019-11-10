.PHONY: pass clean benchmark benchmarks %-loop-info
.PRECIOUS: %-phis.ll


LOOP_PERF_DIR := $(realpath $(dir $(lastword $(MAKEFILE_LIST))))
BUILTDIR := $(LOOP_PERF_DIR)/build

RATE ?= 2

clean:
	rm -f {.,tests,benchmarks/*}/*.{ll,bc,out,json}

pass:
	cd $(BUILTDIR); make; cd $(LOOP_PERF_DIR)

%.ll: %.c
	clang -emit-llvm -Xclang -disable-O0-optnone -S $< -o $@

%-phis.ll: %.ll
	opt -mem2reg -S $< -o $@

%-loop-info: %-phis.ll
	opt -load $(BUILTDIR)/loop-perf/libLoopPerforationPass.* -loop-count -S -o /dev/null $<

%-perforated.ll: %-phis.ll pass
	opt -load $(BUILTDIR)/loop-perf/libLoopPerforationPass.* -loop-perf -S $< -o $@ -rate $(RATE)

%.out: %.ll
	clang -O1 $^ -o $@

BENCHMARK_DIR := benchmarks
BENCHMARKS := blackscholes sobel

BENCHMARK_PATHS := $(addprefix $(BENCHMARK_DIR)/,$(BENCHMARKS))

STANDARD_EXC := $(addsuffix .out,$(SRC))
PERFORATED_EXC := $(addsuffix -perforated.out,$(SRC))

benchmark:
	$(MAKE) $(STANDARD_EXC)                # Make standard executable
	$(MAKE) $(PERFORATED_EXC)              # Make perforated executable
	./$(STANDARD_EXC) $(STANDARD_ARGS)     # Run standard
	$(RUN_AFTER_STANDARD)
	./$(PERFORATED_EXC) $(PERFORATED_ARGS) # Run perforated
	$(RUN_AFTER_PERFORATED)

benchmarks:
	for b in $(BENCHMARK_PATHS); do \
		make -C $${b} benchmark ; \
	done