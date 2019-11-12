import sys
from scipy.special import erf


variances = [1, 10, 100, 1000]
names_and_variances = [('erf_variance_%d' % variance, variance) for variance in variances]
error_names = [name for name, _ in names_and_variances]

def error_function(standard, perforated, variance):
	return erf(abs(standard - perforated)/variance)

def error(standard_fn, perforated_fn):
	standard = get_contents(standard_fn).strip('\n')
	perforated = get_contents(perforated_fn).strip('\n')
	if standard == '': standard = '0'
	if perforated == '': perforated = '0'
	standard = int(standard)
	perforated = int(perforated)
	return {n: error_function(standard, perforated, v) for n, v in names_and_variances}

def get_contents(fn):
	with open(fn, 'r') as f:
		return f.read()

def main():
	standard_fn = sys.argv[1] if len(sys.argv) > 2 else 'standard.txt'
	perforated_fn = sys.argv[2] if len(sys.argv) > 2 else 'perforated.txt'
	print(error(standard_fn, perforated_fn))

if __name__ == '__main__':
	main()