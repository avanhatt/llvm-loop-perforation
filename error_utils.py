import sys
from scipy.special import erf
import numpy as np
import PIL
import PIL.Image

def error_function(standard, perforated, variance):
	return erf(abs(standard - perforated)/variance)

def norm_and_error_function(standard, perforated, norm, variance):
	return error_function(0, np.linalg.norm(standard - perforated, ord=norm), variance)

def string_to_matrix(s):
	# rows separated by '\n'
	# columns separated by ' '
	return np.asarray([[float(e) for e in l.split()] for l in s.strip().split('\n')])

def get_contents(fn):
	with open(fn, 'r') as f:
		return f.read()

def get_vector(fn):
	with open(fn) as f:
		f.readline()  # skip the count
		return np.asarray([float(line) for line in f if line.strip()])

def get_image(fn):
	return np.asarray(PIL.Image.open(fn).getdata())