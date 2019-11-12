import numpy as np
from scipy.special import erf

names_and_norms = [('l0', 0), ('l1', 1), ('l2', 2)]
variances = [1, 100, 1000, 10000, 100000]
names_and_args = [('%s_%d' % (name, variance), norm, variance)
  for name, norm in names_and_norms for variance in variances]
error_names = [name for name, _, _ in names_and_args]

def error_function(perforated, variance):
    return erf(abs(perforated)/variance)

def vector_from_file(fn):
    with open(fn) as f:
        f.readline()  # skip the count
        return np.asarray([float(line) for line in f if line.strip()])

def error(standard_fn, perforated_fn):
    standard = vector_from_file(standard_fn)
    perforated = vector_from_file(perforated_fn)

    return {name:
      error_function(np.linalg.norm(standard - perforated, ord=norm), variance)
      for name, norm, variance in names_and_args}