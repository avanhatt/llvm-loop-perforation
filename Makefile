.PHONY: pass clean benchmark benchmarks %-loop-info
.PRECIOUS: %-phis.ll

LOOP_PERF_DIR := $(realpath $(dir $(lastword $(MAKEFILE_LIST))))

-include $(TARGET)/Makefile

BUILD_DIR := $(LOOP_PERF_DIR)/build
BENCHMARK_DIR := $(LOOP_PERF_DIR)/benchmarks

clean:
	rm -f {.,tests,benchmarks/*}/*.{ll,bc,out,json,standard.txt,perforated.txt}

pass:
	cd $(BUILD_DIR); make; cd $(LOOP_PERF_DIR)

%.ll: %.c
	clang $(CFLAGS) -emit-llvm -Xclang -disable-O0-optnone -S $< -o $@

%.ll: %.cpp
	clang $(CFLAGS) -emit-llvm -Xclang -disable-O0-optnone -S $< -o $@

%-phis.ll: %.ll
	opt -mem2reg -S $< -o $@

%-loop-info: %-phis.ll pass
	opt -load $(BUILD_DIR)/loop-perf/libLoopPerforationPass.* -loop-count -info $*-loop-info.json -S -o /dev/null $<

%-perforated.ll: %-phis.ll pass
	opt -load $(BUILD_DIR)/loop-perf/libLoopPerforationPass.* -loop-perf -rates $*-loop-rates.json -S $< -o $@

%.out: %.ll
	clang $(CFLAGS) $(LDFLAGS) -O1 $^ -o $@

# Driver things

TARGET_SRC = $(wildcard $(TARGET)/*.c)
TARGET_STANDARD_EXC := $(TARGET)/standard.out
TARGET_STANDARD_OUTPUT := $(TARGET)/standard.txt

TARGET_PHIS_LL := $(TARGET_SRC:.c=-phis.ll)

loop-info: $(TARGET_PHIS_LL)
	opt -load $(BUILD_DIR)/loop-perf/libLoopPerforationPass.* -loop-count -info  $(TARGET)/loop-info.json -S -o /dev/null $<

standard:
	clang $(CFLAGS) $(LDFLAGS) -O1 $(TARGET_SRC) -o $(TARGET_STANDARD_EXC)

standard-run:
	$(TARGET_STANDARD_EXC) $(STANDARD_ARGS) > $(TARGET_STANDARD_OUTPUT)
	$(RUN_AFTER_STANDARD)

TARGET_PERF_LL := $(TARGET_SRC:.c=-perforated.ll)
TARGET_PERF_EXC := $(TARGET)/perforated.out
TARGET_PERF_OUTPUT := $(TARGET)/perforated.txt

perforated:
	opt -load $(BUILD_DIR)/loop-perf/libLoopPerforationPass.* -loop-perf -rates $(TARGET)/loop-rates.json -S $(TARGET_PHIS_LL) -o $(TARGET_PERF_LL)
	clang $(CFLAGS) $(LDFLAGS) -O1 $(TARGET_PERF_LL) -o $(TARGET_PERF_EXC)

perforated-run:
	$(TARGET_PERF_EXC) $(PERFORATED_ARGS) > $(TARGET_PERF_OUTPUT)
	$(RUN_AFTER_PERFORATED)

# Benchmark things

benchmark: loop-info standard standard-run perforated perforated-run


