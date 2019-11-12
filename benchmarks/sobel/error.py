import PIL
import PIL.Image
import numpy as np
from scipy.special import erf

names_and_norms = [('l0', 0), ('l1', 1), ('l2', 2)]
variances = [1000, 10000, 100000]
names_and_args = [('%s_%d' % (name, variance), norm, variance)
  for name, norm in names_and_norms for variance in variances]
error_names = [name for name, _, _ in names_and_args]

def error_function(perforated, variance):
    return erf(abs(perforated)/variance)

def error(standard_fn, perforated_fn):
    standard_img = PIL.Image.open(standard_fn)
    perforated_img = PIL.Image.open(perforated_fn)

    try:
        standard = np.asarray(standard_img.getdata())
        perforated = np.asarray(perforated_img.getdata())
    except ValueError:
        return {name: 1.0 for name in error_names}

    return {name:
      error_function(np.linalg.norm(standard - perforated, ord=norm), variance)
      for name, norm, variance in names_and_args}