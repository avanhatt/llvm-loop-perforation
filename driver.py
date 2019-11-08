import subprocess
import time

if __name__ == "__main__":
	rate = 4
	# perforate with one rate sent through the makefile
	make_process = subprocess.Popen(['make', 'tests/sum-to-n-perforated.ll', 'RATE={}'.format(rate)])
	make_process.wait()
	# time the execution of the perforated program in the lli interpreter
	start = time.time()
	interp_process = subprocess.Popen(['lli', 'tests/sum-to-n-perforated.ll'])
	interp_process.wait(timeout=2)
	end = time.time()
	# get the return code for criticality testing
	return_code = interp_process.returncode
	print('Return code: {}'.format(return_code))
	print('Time for perforated loop: {}'.format(end - start))
