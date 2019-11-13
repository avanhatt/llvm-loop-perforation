import argparse
import json
from matplotlib import pyplot as plt
import os
import numpy as np
from scipy import stats

"""
data is of the form { [JSON STRING RATES] => {return code: _, time: _, errors: {...}} }
"""
def plot_frontier(data, args) :
	if len(args.command) > 1:
		acc_measure = args.command[1]

	else: # do my maximum entropy:
		measures = next(iter(data.values()))['errors'].keys()
		acc_measure, bestent = None, 0
		for m in measures:
			ers = [erdata['errors'][m] for erdata in data.values()]
			ent_m = stats.entropy( np.cumsum(ers) )
			if ent_m > bestent:
				acc_measure, bestent = m, ent_m


	canonicalList = [ (erdata['time'], erdata['errors'])  for erdata in data.values()]
	scatterTimeErr = [ (t, e[acc_measure]) for t,e in canonicalList]
	times, errors = map(np.array, zip(*scatterTimeErr))

	# frontier = [() for t,e in scatterTimeErr ]


	ax = plt.scatter(times, errors)
	ax.axes.set_xlabel('Runtime (seconds)')
	ax.axes.set_ylabel('Normalized error (%s)' % acc_measure)

	ax.axes.set_ylim([-0.1,1.1]);
	ax.axes.set_yticks(np.linspace(0, 1, 11))

	plt.savefig(os.path.join(args.target, 'frontier.png'), dpi=400)
	if(args.show):
		plt.show()




if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="run plots on dumped file from previous completion of `driver.py`")
	parser.add_argument('target', nargs='?', default='tests/matrix_multiply')
	parser.add_argument('command', help="The sub plot command: of [frontier]", nargs='+')
	parser.add_argument('--show', action='store_true', help="")

	argus = parser.parse_args()

	print('cmd', argus.command)

	with open(os.path.join(argus.target, 'results.json'), 'r') as rf:
		data = json.load(rf)


	if argus.command[0] == "frontier":
		plot_frontier(data, argus)
