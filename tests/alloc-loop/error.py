import sys
from scipy.special import erf


names_and_variances = [('erf_variance_1', 1), ('erf_variance_10', 10), ('erf_variance_100', 100)]
error_names = [name for name, _ in names_and_variances]

def error_function(standard, perforated, variance):
	return erf(abs(standard - perforated)/variance)

def error(standard, perforated):
	standard = standard.strip('\n')
	perforated = perforated.strip('\n')
	if standard == '': standard = '0'
	if perforated == '': perforated = '0'
	standard = int(standard)
	perforated = int(perforated)
	return {n: error_function(standard, perforated, v) for n, v in names_and_variances}

def get_contents(fn):
	with open(fn, 'r') as f:
		return f.read()

def main():
	standard_fn = sys.argv[1] if len(sys.argv) > 2 else 'output-standard.txt'
	perforated_fn = sys.argv[2] if len(sys.argv) > 2 else 'output-perforated.txt'
	standard = get_contents(standard_fn)
	perforated = get_contents(perforated_fn)
	print(error(standard, perforated))

if __name__ == '__main__':
	main()