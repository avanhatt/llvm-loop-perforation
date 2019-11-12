.PHONY: pass clean benchmark benchmarks %-loop-info
.PRECIOUS: %-phis.ll


LOOP_PERF_DIR := $(realpath $(dir $(lastword $(MAKEFILE_LIST))))
BUILD_DIR := $(LOOP_PERF_DIR)/build
BENCHMARK_DIR := $(LOOP_PERF_DIR)/benchmarks

RATE ?= 2

clean:
	rm -f {.,tests,benchmarks/*}/*.{ll,bc,out,json}

pass:
	cd $(BUILD_DIR); make; cd $(LOOP_PERF_DIR)

%.ll: %.c
	clang $(CFLAGS) -emit-llvm -Xclang -disable-O0-optnone -S $< -o $@

%.ll: %.cpp
	clang $(CFLAGS) -emit-llvm -Xclang -disable-O0-optnone -S $< -o $@

%-phis.ll: %.ll
	opt -mem2reg -S $< -o $@

%-loop-info: %-phis.ll
	opt -load $(BUILD_DIR)/loop-perf/libLoopPerforationPass.* -loop-count -S -o /dev/null $<

%-perforated.ll: %-phis.ll pass
	opt -load $(BUILD_DIR)/loop-perf/libLoopPerforationPass.* -loop-perf -S $< -o $@ -rate $(RATE)

%.out: %.ll
	clang $(CFLAGS) $(LDFLAGS) -O1 $^ -o $@

# Driver things

DRIVER_SRC_EXT ?= .c
DRIVER_SRC := $(DRIVER_DIR)/*$(DRIVER_SRC_EXT)

standard:
	clang $(CFLAGS) $(LDFLAGS) -O1 $(DRIVER_SRC) -o $(DRIVER_DIR)/standard.out

standard-run:
	$(DRIVER_DIR)/standard.out $(STANDARD_ARGS) > $(DRIVER_DIR)/$@.txt
	$(RUN_AFTER_STANDARD)

DRIVER_SRC_PERF := $(DRIVER_SRC:.c=-perforated.ll)

perforated:
	$(MAKE) $(DRIVER_SRC_PERF)
	clang $(CFLAGS) $(LDFLAGS) -O1 $(DRIVER_SRC_PERF) -o $(DRIVER_DIR)/perforated.out

perforated-run:
	$(DRIVER_DIR)/perforated.out $(PERFORATED_ARGS)
	$(RUN_AFTER_PERFORATED) > $(DRIVER_DIR)/$@.txt

# Benchmark things

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