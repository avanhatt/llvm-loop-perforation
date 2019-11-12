SRC := streamcluster

STANDARD_ARGS := 2 5 1 10 10 5 none output-standard.txt 1
PERFORATED_ARGS := 2 5 1 10 10 5 none output-perforated.txt 1

LDFLAGS := -lpthread
CFLAGS := -DENABLE_THREADS

include ../../Makefile
.DEFAULT_GOAL := benchmark