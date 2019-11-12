def vector_from_file(fn):
    with open(fn) as f:
        f.readline()  # skip the count
        return [float(line) for line in f if line.strip()]

def error(standard_fn, perforated_fn):
    standard = vector_from_file(standard_fn)
    perforated = vector_from_file(perforated_fn)
    return 0