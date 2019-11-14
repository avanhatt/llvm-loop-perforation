import argparse
import json
from matplotlib import pyplot as plt
import os
import numpy as np
from scipy import stats
import seaborn as sns
import pandas as pd

sns.set(style="ticks")
sns.set_palette("bright")
seaborn_colors = sns.color_palette().as_hex()
 # [ '#%02X%02X%02X' % tuple(int(v*255) for v in rgb) for rgb in sns.color_palette() ]


def hd(l):
	return next(iter(l))

"""
data is of the form { [JSON STRING RATES] => {return code: _, time: _, errors: {...}} }
"""
def plot_frontier(data, args) :
	measures = hd(hd(data.values()))['errors'].keys()

	if args.acc_measure == None and len(args.command) > 2:
		acc_measure = args.command[2]
	elif not args.acc_measure: # do my maximum entropy:
		acc_measure, bestent = None, 0
		for m in measures:
			ers = [erdat['errors'][m] for erdat_l in data.values() for erdat in erdat_l]
			ent_m = stats.entropy( np.cumsum(ers) )
			if ent_m > bestent:
				acc_measure, bestent = m, ent_m

	acc_measure = args.acc_measure

	canonicalList = [ (erdata['time'], erdata['errors'], paramstr, erdata['return_code'] ) for paramstr, erdatlist in data.items() \
		for erdata in erdatlist ]

	# print(hd(canonicalList)[1].keys())
	scatterTimeErr = [ (t, e[acc_measure], p, ec) for t,e,p,ec in canonicalList]
	times, errors, params, ercodes = map(np.array, zip(*scatterTimeErr))


	frontier = np.ones(times.shape, dtype=bool)
	special =  np.empty(times.shape, dtype='object')

	color_lookup = {'!original' : seaborn_colors[6], '!joined' : seaborn_colors[9]}
	for i, (t1, es1, p, ec) in enumerate(canonicalList):
		special[i] = color_lookup[p[:p.index('_')]] if p[0] == '!' else seaborn_colors[0]
		if ec != 0:
			special[i] = '#000000'

		for j, (t2, es2, _, _) in enumerate(canonicalList):
			if i is j: continue

			if t1 >= t2 and all(es1[m] >= es2[m] for m in measures):
				frontier[i] = False;

	nofrontier = np.logical_not(frontier);
	ax = plt.scatter(times[nofrontier], errors[nofrontier],
		c = special[nofrontier].tolist(),
		marker='o',
		alpha = 0.4,
		linewidths = 0, s=100, zorder=0)

	ax.axes.scatter(times[frontier], errors[frontier], zorder=1,
		c=special[frontier].tolist(), marker='o', s=100, linewidths=2, edgecolor=seaborn_colors[3])
	# ax.axes.scatter(times[frontier], errors[frontier], s=1000, zorder=0, c=seaborn_colors[1])

	ax.axes.set_xlabel('Runtime (seconds)')
	ax.axes.set_ylabel('Normalized error (%s)' % acc_measure)
	ax.axes.set_title(args.target.split('/')[-1]);

	# ax.axes.set_xlim([-0.1, ax.axes.get_xlim()[1]])
	x_step = np.around(times.max()/5, -int(np.ceil(np.log10(times.max()))-2) )
	# if (times.max()

	ax.axes.set_xticks(np.arange(0, times.max(), x_step))

	ax.axes.set_ylim([-0.1,1.1]);
	ax.axes.set_yticks(np.linspace(0, 1, 11))

	# create fake markers for the legend
	plt.plot([], [], marker='o', color=seaborn_colors[0], alpha=0.4, ls='None', markeredgewidth=0, label='Perforated')
	plt.plot([], [], marker='o', color='k', alpha=0.4, ls='None', markeredgewidth=0, label='Program error') 
	plt.plot([], [], marker='o', color=seaborn_colors[6], alpha=0.4, ls='None', markeredgewidth=0, label='Original')
	plt.plot([], [], marker='o', color=seaborn_colors[9], alpha=0.4, ls='None', markeredgewidth=0, label='Best perforated')
	plt.plot([], [], marker='o', color=seaborn_colors[0], alpha=1.0, ls='None', markeredgewidth=1, markeredgecolor=seaborn_colors[3], label='Frontier')

	plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
	plt.savefig(os.path.join(args.target, 'frontier.png'), bbox_inches='tight', dpi=400)
	if(args.show):
		plt.show()


def plot_speedups(data, args):
	plt.rcParams['figure.figsize'] = (7.6,4.8)
	# convert to seaborn data format
	graph_data = pd.DataFrame(columns=['Benchmark', 'Type', 'Time', 'Trial'])
	for benchmark, all_rates in data.items():
		for rates, rslt_list in all_rates.items():
			for j,rslt_dict in enumerate(rslt_list):
				typ = None
				if '!original_' in rates:
					typ = 'Original'
				if '!joined_' in rates:
					typ = 'Perforated'
				if typ != None:
					graph_data = graph_data.append({'Benchmark': benchmark, 'Type': typ, 'Time': rslt_dict['time'], 'Trial' : j}, ignore_index=True)
	ax = sns.barplot(x="Benchmark", y="Time", hue="Type", data=graph_data)
	plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
	plt.savefig('speedup.png', bbox_inches='tight', dpi=400)
	if(args.show):
		plt.show()
	plt.close()

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="run plots on dumped file from previous completion of `driver.py`")
	parser.add_argument('command', help="The sub plot command: of [frontier]", nargs='+')
	# parser.add_argument('target', nargs='?', default='tests/matrix_multiply')
	parser.add_argument('--show', action='store_true', help="")
	parser.add_argument('--target', help="", required=False, default=None)
	parser.add_argument('--acc-measure', help="accuracy measure", required=False, default=None)

	args = parser.parse_args()

	if args.command[0] == "frontier":
		if args.target == None and len(args.command) > 1:
			args.target = args.command[1];

		with open(os.path.join(args.target, 'results.json'), 'r') as rf:
			data = json.load(rf)

		plot_frontier(data, args)

	elif args.command[0] == "speedups":
		if args.target == None and len(args.command) > 1:
			args.target = args.command[1];

		data = {}
		for subdir in ['benchmarks', 'tests']:
			for base_name in os.listdir( os.path.join(args.target, subdir) ):
				base_path = os.path.join(args.target, subdir, base_name)

				if os.path.isdir(base_path):
					try:
						with open(os.path.join(base_path, 'results.json'), 'r') as rf:
							data_here = json.load(rf)
						data[base_name] = data_here
					except FileNotFoundError as fne:
						print(fne)

		plot_speedups(data, args);
