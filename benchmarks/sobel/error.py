from __future__ import division
import PIL
import PIL.Image
from statistics import mean

IMGDIR = 'saved_outputs'

def load():
    return 'file:out.pgm'

def error(standard_fn, perforated_fn):
    standard_img = PIL.Image.open(standard_fn)
    perforated_img = PIL.Image.open(perforated_fn)

    try:
        standard = standard_img.getdata()
        perforated = perforated_img.getdata()
    except ValueError:
        return 1.0

    norm_diffs = [abs(p1 - p2)/255 for p1, p2 in zip(standard, perforated)]
    return mean(norm_diffs)