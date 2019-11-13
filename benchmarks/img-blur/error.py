import sys
sys.path.append('../..')
from error_utils import *

names_and_norms = [('l0', 0), ('l1', 1), ('l2', 2)]
variances = [1000, 10000, 100000]
names_and_args = [('%s_%d' % (name, variance), norm, variance)
  for name, norm in names_and_norms for variance in variances]
error_names = [name for name, _, _ in names_and_args]

def error(standard_fn, perforated_fn):

    try:
        standard = get_image(standard_fn)
        perforated = get_image(perforated_fn)
    except ValueError:
        return {name: 1.0 for name in error_names}

    return {name:
      norm_and_error_function(standard, perforated, norm, variance)
      for name, norm, variance in names_and_args}