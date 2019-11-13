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
	target = args.command[1]

	if len(args.command) > 2:
		acc_measure = args.command[2]
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
				frontier[i] = False;

	# frontier = [() for t,e in scatterTimeErr ]

	ax = plt.scatter(times, errors, c=np.where(frontier, 'g', 'b'))
	ax.axes.set_xlabel('Runtime (seconds)')
	ax.axes.set_ylabel('Normalized error (%s)' % acc_measure)
	ax.axes.set_title(target.split('/')[-1]);

	# ax.axes.set_xlim([-0.1, ax.axes.get_xlim()[1]])
	x_step = np.around(times.max()/5, -int(np.ceil(np.log10(times.max()))-2) )
	# if (times.max()

	ax.axes.set_xticks(np.arange(0, times.max(), x_step))

	ax.axes.set_ylim([-0.1,1.1]);
	ax.axes.set_yticks(np.linspace(0, 1, 11))

	plt.savefig(os.path.join(target, 'frontier.png'), dpi=400)
	if(args.show):
		plt.show()


def plot_speedups():
	pass

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="run plots on dumped file from previous completion of `driver.py`")
	parser.add_argument('command', help="The sub plot command: of [frontier]", nargs='+')
	# parser.add_argument('target', nargs='?', default='tests/matrix_multiply')
	parser.add_argument('--show', action='store_true', help="")
	parser.add_argument('--base', action='store_true', help="")

	args = parser.parse_args()

	if args.command[0] == "frontier":
		target = args.command[1];
		with open(os.path.join(target, 'results.json'), 'r') as rf:
			data = json.load(rf)

		plot_frontier(data, args)

	elif args.command[0] == "speedups":
		data = {}
		for subdir in ['benchmarks', 'tests']:
			for base_name in os.listdir( os.path.join(args.base, subdir) ):
				base_path = os.path.join(args.base, subdir, base_name)

				if os.path.isdir(base_path):
					with open(os.path.join(base_path, 'results.json'), 'r') as rf:
						data_here = json.load(rf)
					data[base_name] = data_here
