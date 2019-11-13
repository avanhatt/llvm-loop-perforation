import sys
import numpy as np
sys.path.append('../..')
from error_utils import *

names_and_norms = [('l0', 0), ('l1', 1), ('l2', 2)]
variances = [1, 100, 1000, 10000, 100000]
names_and_args = [('%s_%d' % (name, variance), norm, variance)
  for name, norm in names_and_norms for variance in variances]
error_names = [name for name, _, _ in names_and_args]

def error(standard_fn, perforated_fn):
    standard = get_vector(standard_fn)
    perforated = get_vector(perforated_fn)

    results = {name:
      norm_and_error_function(standard, perforated, norm, variance)
      for name, norm, variance in names_and_args}

    # any nan incurs the max error
    return {name: (error if not np.isnan(error) else 1.0) for name, error in results.items()}