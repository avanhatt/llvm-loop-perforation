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
	measures = next(iter(data.values()))['errors'].keys()

	if len(args.command) > 1:
		acc_measure = args.command[1]
	else: # do my maximum entropy:
		acc_measure, bestent = None, 0
		for m in measures:
			ers = [erdata['errors'][m] for erdata in data.values()]
			ent_m = stats.entropy( np.cumsum(ers) )
			if ent_m > bestent:
				acc_measure, bestent = m, ent_m


	canonicalList = [ (erdata['time'], erdata['errors']) for erdata in data.values()]
	scatterTimeErr = [ (t, e[acc_measure]) for t,e in canonicalList]
	times, errors = map(np.array, zip(*scatterTimeErr))


	frontier = np.ones(times.shape, dtype=bool)
	for i, (t1, es1) in enumerate(canonicalList):
		for j, (t2, es2) in enumerate(canonicalList):
			if i is j: continue

			if t1 >= t2 and all(es1[m] >= es2[m] for m in measures):
				print(i, ' beats ', j)
				frontier[i] = False;

	# frontier = [() for t,e in scatterTimeErr ]
	print(frontier)

	ax = plt.scatter(times, errors, c=np.where(frontier, 'g', 'b'))
	ax.axes.set_xlabel('Runtime (seconds)')
	ax.axes.set_ylabel('Normalized error (%s)' % acc_measure)

	# ax.axes.set_xlim([-0.1, ax.axes.get_xlim()[1]])
	x_step = np.around(times.max()/10, -int(np.ceil(np.log10(times.max())))-2 )
	print(0, times.max(), x_step)
	# ax.axes.set_xticks(np.arange(0, times.max(), x_step))

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
