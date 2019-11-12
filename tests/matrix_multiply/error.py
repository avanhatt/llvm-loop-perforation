import sys
import numpy as np
from scipy.special import erf

names_and_norms = [('l2', 2), ('froebenius', 'fro')]
variances = [1, 10, 100]
names_and_args = [('%s_%d' % (name, variance), norm, variance)
  for name, norm in names_and_norms for variance in variances]
error_names = [name for name, _, _ in names_and_args]

def string_to_matrix(s):
	return np.asarray([[float(e) for e in l.split()] for l in s.strip().split('\n')])

def error_function(perforated, variance):
	return erf(abs(perforated)/variance)

def error(standard_fn, perforated_fn):
	standard = get_contents(standard_fn)
	perforated = get_contents(perforated_fn)
	standard = string_to_matrix(standard)
	perforated = string_to_matrix(perforated)

	# max error if sizes differ
	if standard.shape != perforated.shape:
		return {name: 1.0 for name in error_names}

	return {name:
	  error_function(np.linalg.norm(standard - perforated, ord=norm), variance)
	  for name, norm, variance in names_and_args}

def get_contents(fn):
	with open(fn, 'r') as f:
		return f.read()

def main():
	standard_fn = sys.argv[1] if len(sys.argv) > 2 else 'standard.txt'
	perforated_fn = sys.argv[2] if len(sys.argv) > 2 else 'perforated.txt'
	print(error(standard_fn, perforated_fn))

if __name__ == '__main__':
	main()