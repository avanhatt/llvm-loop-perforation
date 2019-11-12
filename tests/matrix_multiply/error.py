import sys
import numpy as np

def string_to_matrix(s):
	m = np.empty((3,3))
	for i, row in enumerate(s.split("\n")):
		for j, element in enumerate(row.split(' ')):
			m[i, j] = float(element)
	return m

def error(standard, perforated):
	standard = string_to_matrix(standard)
	perforated = string_to_matrix(perforated)
	names_and_norms = [('l2', 2), ('froebenius', 'fro')]
	print(perforated - standard)
	return {name: np.linalg.norm(standard - perforated, ord=norm) for name, norm in names_and_norms}

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