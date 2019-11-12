import sys
import numpy as np
from scipy.special import erf

def string_to_matrix(s):
	m = np.empty((3,3))
	for i, row in enumerate(s.split("\n")):
		if not row:
			continue
		for j, element in enumerate(row.split(' ')):
			if not element:
				continue
			m[i, j] = float(element)
	return m

def error_function(perforated, variance):
	return erf(abs(perforated)/variance)

def error(standard_fn, perforated_fn):
	standard = get_contents(standard_fn)
	perforated = get_contents(perforated_fn)
	standard = string_to_matrix(standard)
	perforated = string_to_matrix(perforated)
	names_and_norms = [('l2', 2), ('froebenius', 'fro')]
	variances = [1, 10, 100]
	return {'%s_%d' % (name, variance):
	  error_function(np.linalg.norm(standard - perforated, ord=norm), variance)
	  for name, norm in names_and_norms for variance in variances}

def get_contents(fn):
	with open(fn, 'r') as f:
		return f.read()

def main():
	standard_fn = sys.argv[1] if len(sys.argv) > 2 else 'standard.txt'
	perforated_fn = sys.argv[2] if len(sys.argv) > 2 else 'perforated.txt'
	print(error(standard_fn, perforated_fn))

if __name__ == '__main__':
	main()