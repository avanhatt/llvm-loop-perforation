import subprocess
import time
import json

if __name__ == "__main__":
	subprocess.call(['make', 'clean'])
	# collect loop info to JSON file
	make_process = subprocess.Popen(['make', 'tests/matrix_multiply-phis.ll'])
	make_process.wait()
	# perforate with one rate sent through the makefile

	# infojson = json.load(open('loop-info.json', 'r'))
	infojson = json.load(open('tests/matrix_multiply-phis.ll.json', 'r'))

	data = { m : {l : 1 for l in ld } for m,ld in infojson.items() };
	print(data);

	# sequentially take each loop and perforate at rate 2 (all others at rate 1)
	for modulename, loopdict in infojson.items():
		for loopname in loopdict:
			data[modulename][loopname] = 2;

			with open('loop-rates.json', 'w') as file:
				json.dump(data, file, indent=4);

			data[modulename][loopname] = 1;

			# now run all the other stuff.
			make_process = subprocess.Popen(['make', 'tests/matrix_multiply-perforated.ll'])
			make_process.wait()
			# time the execution of the perforated program in the lli interpreter
			start = time.time()
			interp_process = subprocess.Popen(['lli', 'tests/matrix_multiply-perforated.ll'])
			interp_process.wait(timeout=2)
			end = time.time()
			# get the return code for criticality testing
			return_code = interp_process.returncode
			print('Return code: {}'.format(return_code))
			print('Time for perforated loop: {}'.format(end - start))

			raise SystemExit
