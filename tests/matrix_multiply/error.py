import sys
sys.path.append('../..')
from error_utils import *

names_and_norms = [('l2', 2), ('froebenius', 'fro')]
variances = [1, 100, 10000, 1000000]
names_and_args = [('%s_%d' % (name, variance), norm, variance)
  for name, norm in names_and_norms for variance in variances]
error_names = [name for name, _, _ in names_and_args]

def error(standard_fn, perforated_fn):
	standard = string_to_matrix(get_contents(standard_fn))
	perforated = string_to_matrix(get_contents(perforated_fn))

	# max error if sizes differ
	if standard.shape != perforated.shape:
		return {name: 1.0 for name in error_names}

	return {name:
	  norm_and_error_function(standard, perforated, norm, variance)
	  for name, norm, variance in names_and_args}

def main():
	standard_fn = sys.argv[1] if len(sys.argv) > 2 else 'standard.txt'
	perforated_fn = sys.argv[2] if len(sys.argv) > 2 else 'perforated.txt'
	print(error(standard_fn, perforated_fn))

if __name__ == '__main__':
	main()