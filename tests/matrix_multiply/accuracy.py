

def string_to_matrix(s):
    return [row for row in s.split("\n")]
    pass

def accuracy(standard, perforated):

standard = sys.argv[1] if len(sys.argv) > 2 else 'output-standard.txt'
perforated = sys.argv[2] if len(sys.argv) > 2 else 'output-perforated.txt'

