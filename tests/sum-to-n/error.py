import sys
sys.path.append('../..')
from error_utils import *

error_names = ["error_ratio"]

def error(standard_fn, perforated_fn):
    standard = int(get_contents(standard_fn))
    perforated = int(get_contents(perforated_fn))

    delta = abs(standard - perforated)
    ratio = delta / standard

    return {"error_ratio" : ratio}

def main():
    standard_fn = sys.argv[1] if len(sys.argv) > 2 else 'standard.txt'
    perforated_fn = sys.argv[2] if len(sys.argv) > 2 else 'perforated.txt'
    print(error(standard_fn, perforated_fn))

if __name__ == '__main__':
    main()