.PHONY: pass clean benchmark benchmarks
.PRECIOUS: %-phis.ll


LOOP_PERF_DIR := $(realpath $(dir $(lastword $(MAKEFILE_LIST))))
BUILD_DIR := $(LOOP_PERF_DIR)/build
BENCHMARK_DIR := $(LOOP_PERF_DIR)/benchmarks

RATE ?= 2

clean:
	rm -f {.,tests,benchmarks/*}/*.{ll,bc,out}

pass:
	cd $(BUILD_DIR); make; cd $(LOOP_PERF_DIR)

%.ll: %.c
	clang -emit-llvm -Xclang -disable-O0-optnone -S $< -o $@

%.ll: %.cpp
	clang -emit-llvm -Xclang -disable-O0-optnone -S $< -o $@

%-phis.ll: %.ll
	opt -mem2reg -S $< -o $@

%-perforated.ll: %-phis.ll pass
	opt -load $(BUILD_DIR)/loop-perf/libLoopPerforationPass.* -loop-perf -S $< -o $@ -rate $(RATE)

%.out: %.ll
	clang -O1 $^ -o $@

BENCHMARKS := $(shell ls $(BENCHMARK_DIR))
BENCHMARK_PATHS := $(addprefix $(BENCHMARK_DIR)/,$(BENCHMARKS))

benchmarks:
	for b in $(BENCHMARK_PATHS); do \
		make -C $${b} benchmark ; \
	done

# The following code runs per benchmark, based on variables set in each
STANDARD_EXC := $(addsuffix .out,$(SRC))
PERFORATED_EXC := $(addsuffix -perforated.out,$(SRC))

benchmark:
	$(MAKE) $(STANDARD_EXC)                # Make standard executable
	$(MAKE) $(PERFORATED_EXC)              # Make perforated executable
	./$(STANDARD_EXC) $(STANDARD_ARGS)     # Run standard
	$(RUN_AFTER_STANDARD)
	./$(PERFORATED_EXC) $(PERFORATED_ARGS) # Run perforated
	$(RUN_AFTER_PERFORATED)