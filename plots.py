import argparse
import json
from matplotlib import pyplot as plt
import os
import numpy as np

"""
data is of the form { [JSON STRING RATES] => {return code: _, time: _, errors: {...}} }
"""
def plot_frontier(data, acc_measure, target) :
	scatterTimeErr = [ [erdata['time'], erdata['errors'][acc_measure]] for erdata in data.values()]
	times, errors = map(np.array, zip(*scatterTimeErr))


	ax = plt.scatter(times, errors)
	ax.axes.set_xlabel('Runtime (seconds)')
	ax.axes.set_ylabel('Normalized error (bullshit units)')

	ax.axes.set_ylim([-0.1,1.1]);
	ax.axes.set_yticks(np.linspace(0, 1, 11))

	plt.savefig(os.path.join(args.target, 'frontier.png'), dpi=400)
	plt.show()


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="run plots on dumped file from previous completion of `driver.py`")
	parser.add_argument('target', nargs='?', default='tests/matrix_multiply')
	parser.add_argument('command', help="The sub plot command: of [frontier]", nargs='+')

	args = parser.parse_args()

	print('cmd', args.command)

	with open(os.path.join(args.target, 'results.json'), 'r') as rf:
		data = json.load(rf)


	if args.command[0] == "frontier":
		plot_frontier(data, args.command[1], target=args.target)
