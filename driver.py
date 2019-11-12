import subprocess
import time, sys
import json
from collections import defaultdict
import copy
import os
import importlib
import argparse
import re


if __name__ == "__main__":
	## USAGE AND SUCH
	parser = argparse.ArgumentParser(description="Driver program to compile perforated loops, collect results, and choose a point on the frontier")
	# `tests/matrix_multiply` is the default target.
	parser.add_argument('target', nargs='?', default='tests/matrix_multiply')
	parser.add_argument('-t', '--timeout', default=5, type=int)
	parser.add_argument('-e', '--max-error', default=0.5, type=float, help="the tolerance below which we will throw out loops")
	parser.add_argument('--rates', nargs='+', type=int, required=False, default=[2,3,5])
	parser.add_argument('--error_filter', type=str, required=False, default='.*')

	args = parser.parse_args();

	print(args)

	target = args.target
	TIMEOUT = args.timeout
	RATES = args.rates

	loop_info_path = os.path.join(target, 'loop-info.json')
	loop_rates_path = os.path.join(target, 'loop-rates.json')
	results_path = os.path.join(target, 'results.json')
	error_path = os.path.join(target, 'error')

	####################### NOW WE BEGIN ########################3
	subprocess.call(['make', 'clean'])

	# collect loop info to JSON file
	make_process = subprocess.Popen(['make', 'loop-info', 'TARGET={}'.format(target)])
	make_process.wait()

	infojson = json.load(open(loop_info_path, 'r'))

	# import the error module
	sys.path.append(target)
	mod = importlib.import_module("error")
	exp = re.compile(args.error_filter)
	filtered_error_names = set(n for n in mod.error_names if exp.fullmatch(n))

	def test_perforation(rate_parameters) :
		with open(loop_rates_path, 'w') as file:
			json.dump(rate_parameters, file, indent=4);

		# Let's create the dictionary where we collect statistics...
		R = {}

		# now run all the other stuff.
		make_process = subprocess.Popen(['make', 'perforated', 'TARGET={}'.format(target)])
		make_process.wait()
		# time the execution of the perforated program in the lli interpreter

		try:
			start = time.time()
			interp_process = subprocess.Popen(['make', 'perforated-run', 'TARGET={}'.format(target)])
			interp_process.wait(timeout=TIMEOUT)
			end = time.time()
			# get the return code for criticality testing
			R['return_code'] = interp_process.returncode
			R['time'] = end - start
			if interp_process.returncode != 0:
				raise ValueError

			standard = '{}/standard.txt'.format(target)
			perforated ='{}/perforated.txt'.format(target)
			errors = {n: e for n, e in mod.error(standard, perforated).items() if n in filtered_error_names}

			print("errors: ", errors)
			R['errors'] = errors

		except subprocess.TimeoutExpired:
			R['time'] = float('inf')
			R['return_code'] = float('nan')
			R['errors'] = {error_name: 1.0
			  for error_name in filtered_error_names}

		except ValueError:
			# set all errors to the max value if the program
			# has a non-zero return code
			R['errors'] = {error_name: 1.0
			  for error_name in filtered_error_names}

		return R;

	# make the standard version
	make_process = subprocess.call(['make', 'standard', 'TARGET={}'.format(target)])

	# run the standard version
	run_process = subprocess.Popen(['make', 'standard-run', 'TARGET={}'.format(target)])
	run_process.wait(timeout=TIMEOUT)

	if run_process.returncode:
		print("Standard run must succeed, failed with return code: {}".format(run_process.returncode))
		exit(1)

	############# now run perforated versions #############

	# initialize rate parameters to 1.
	rate_params = { m : { f: {l : 1 for l in ld } for f,ld in fd.items()} for m,fd in infojson.items() };
	# rate_parameters = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: 1))

	results = {}	# results dictionary: {loop rate dict, jsonified} => statistic => value.


	# sequentially take each loop and perforate at rate 2 (all others at rate 1)
	for modulename, functdict in infojson.items():
		for funcname, loopdict in functdict.items():
			for loopname in loopdict:
				for r in RATES:
					rate_params[modulename][funcname][loopname] = r;
					results[json.dumps(rate_params)] = test_perforation(rate_params) # build, and test perforation
					rate_params[modulename][funcname][loopname] = 1 # reset the current loop to 1.


				# print('Return code: {}'.format(return_code))
				# print('Time for perforated loop: {}'.format(end - start))


	def flatten(d, prefix="", target={}):
		for k,v in d.items():
			if isinstance(v, dict):
				flatten(v, prefix+";", target);
			else:
				target[prefix+k] = v;

		return target;

	# assume that same structure for d1, d2. Save in d1
	def joint_rec_iter(d1,d2, f):
		for k,v1 in d1.items():
			v2 = d2[k]
			if isinstance(v1, dict) and isinstance(v2, dict):
				joint_rec_iter(v1,v2, f)
			else:
				d1[k] = f(v1, v2)

	# we now have a collection of {result => indent}.
	# In this case, it's a bunch of loops. Merge them together.

	def good_enough( R ):
		return R['return_code'] == 0 and any(e < args.max_error for n,e in R['errors'].items())

	# get the maximum perf rate on each loop.
	def join( perf_rates ):
		# initialize to bottom
		rslt = { m : { f: {l : 1 for l in ld } for f,ld in fd.items()} for m,fd in infojson.items() };

		for sss in perf_rates:
			data = json.loads(sss);
			joint_rec_iter(rslt, data, max);

			# for m, fd in infojson.items():
			# 	for f, ld in fd.items():
			# 		for l, v in ld.items():
		return rslt


	print("All Results collected")
	print(json.dumps(dict(results), indent=4));
	with open(results_path, 'w') as file:
		json.dump(dict(results), file, indent=4);

	# filter by good enough and then take join of data
	good = { key : data for key, data in results.items() if good_enough(data) }
	print("GOOD", json.dumps(good, indent=4));
	joined = join(good.keys())
	print("JOINED", joined)


	# dump final
	RSLT = test_perforation(joined);
	print("THE JOINED RESULT perfs @ ["+",".join(map(str,flatten(joined).values()))+"]", json.dumps(RSLT, indent=4));
	if(RSLT['return_code'] != 0):
		raise RuntimeError("The Joined result produces an error");
