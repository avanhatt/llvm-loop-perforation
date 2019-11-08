import subprocess
import time

if __name__ == "__main__":
	rate = 4
	# perforate with one rate sent through the makefile
	make_process = subprocess.Popen(['make', 'tests/sum-to-n-perforated.ll', 'RATE={}'.format(rate)])
	make_process.wait()
	# run with lli interpreter
	t1 = time.time()
	interp_process = subprocess.Popen(['lli', 'tests/sum-to-n-perforated.ll'])
	interp_process.wait(timeout=2)
	t2 = time.time()
	print('Time for perforated loop: {}'.format(t2 - t1))
