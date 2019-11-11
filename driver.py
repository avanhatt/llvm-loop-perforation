import subprocess
import time, sys
import json
from collections import defaultdict

if __name__ == "__main__":
	# `tests/matrix_multiply` is the default target.
	target = sys.argv[1] if len(sys.argv) > 1 else 'tests/matrix_multiply';

	subprocess.call(['make', 'clean'])
	# collect loop info to JSON file
	make_process = subprocess.Popen(['make', '{}-loop-info'.format(target)])
	make_process.wait()
	# perforate with one rate sent through the makefile

	infojson = json.load(open('loop-info.json', 'r'))
	#infojson = json.load(open('tests/{}-phis.ll.json', 'r'))

	data = { m : { f: {l : 1 for l in ld } for f,ld in fd.items()} for m,fd in infojson.items() };

	# create results dictionary: {loop rate dict, jsonified} => statistic => value.
	results = {}

	# sequentially take each loop and perforate at rate 2 (all others at rate 1)
	for modulename, functdict in infojson.items():
		for funcname, loopdict in functdict.items():
			if funcname == 'main': continue
			for loopname in loopdict:
				data[modulename][funcname][loopname] = 2;

				with open('loop-rates.json', 'w') as file:
					json.dump(data, file, indent=4);




				# Let's create the dictionary where we collect statistics...
				R = {}

				# now run all the other stuff.
				make_process = subprocess.Popen(['make', '{}-perforated.ll'.format(target)])
				make_process.wait()
				# time the execution of the perforated program in the lli interpreter

				try:
					start = time.time()
					interp_process = subprocess.Popen(['lli', '{}-perforated.ll'.format(target)])
					interp_process.wait(timeout=2)
					end = time.time()
					# get the return code for criticality testing
					R['return_code'] = interp_process.returncode
					R['time'] = end - start
				except subprocess.TimeoutExpired:
					R['time'] = float('inf')
					R['return_code'] = float('nan')

				# put all statistics in the right place:
				results[json.dumps(data)] = R

				# reset the current loop to 1.
				data[modulename][funcname][loopname] = 1;

				# print('Return code: {}'.format(return_code))
				# print('Time for perforated loop: {}'.format(end - start))

	print(json.dumps(dict(results), indent=4));
	with open('results.json', 'w') as file:
		json.dump(dict(results), file, indent=4);
