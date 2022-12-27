# SPDX-License-Identifier: BSD-3-Clause
import logging    as log
from argparse     import ArgumentParser, Namespace, ArgumentDefaultsHelpFormatter
from pathlib      import Path
from itertools    import chain

from rich         import traceback
from rich.logging import RichHandler

from .deps        import get_deps
from .graphviz    import emit_graphviz

__all__ = (
	'cli_main'
)


def setup_logging(args: Namespace = None) -> None:
	'''Initialize logging subscriber
	Set up the built-in rich based logging subscriber, and force it
	to be the one at runtime in case there is already one set up.
	Parameters
	----------
	args : argparse.Namespace
		Any command line arguments passed.
	'''

	level = log.INFO
	if args is not None and args.verbose:
		level = log.DEBUG

	log.basicConfig(
		force    = True,
		format   = '%(message)s',
		datefmt  = '[%X]',
		level    = level,
		handlers = [
			RichHandler(rich_tracebacks = True, show_path = False)
		]
	)

def cli_main():
	traceback.install()
	setup_logging()

	parser = ArgumentParser(
		formatter_class = ArgumentDefaultsHelpFormatter,
		description     = 'Render a dependency graph for a collection of binaries',
		prog            = 'depgraph'
	)

	parser.add_argument(
		'--directory', '-d',
		action = 'append',
		type = Path,
		help = 'The directory of libraries or executables'
	)

	parser.add_argument(
		'--output', '-o',
		type = Path,
		help = 'The output graph file'
	)


	core_options = parser.add_argument_group('Core configuration options')

	core_options.add_argument(
		'--verbose', '-v',
		action = 'store_true',
		help   = 'Enable verbose output'
	)

	deps_options = parser.add_argument_group('Dependency options')

	deps_options.add_argument(
		'--filter-common', '-f',
		action = 'store_true',
		help   = 'Filter out common system libraries'
	)

	output_options = parser.add_mutually_exclusive_group()

	output_options.add_argument(
		'--graphviz', '-g',
		action = 'store_true',
		help   = 'Output in graphviz format'
	)

	gv_options = parser.add_argument_group('graphviz options')

	gv_options.add_argument(
		'--gv-engine', '-E',
		action = 'store',
		type = str,
		choices = ['neato', 'dot', 'twopi', 'circo', 'sfdp', 'fdp', 'osage', 'patchwork'],
		default = 'dot'
	)

	gv_options.add_argument(
		'--gv-spline', '-S',
		action = 'store',
		type = str,
		choices = ['none', 'line', 'polyline', 'curved', 'ortho', 'spline'],
		default = 'spline'
	)

	gv_options.add_argument(
		'--gv-view', '-V',
		action = 'store_true',
		help   = 'Display graphviz results after generation'
	)

	gv_options.add_argument(
		'--gv-cluster', '-C',
		action = 'store_true',
		help   = 'Enable subgraph clustering'
	)

	gv_options.add_argument(
		'--gv-dpi', '-D',
		type = float,
		default = 96.0,
		help    = 'graphviz output DPI'
	)

	gv_options.add_argument(
		'--gv-outputorder', '-O',
		action = 'store',
		type = str,
		choices = ['breadthfirst', 'nodesfirst', 'edgesfirst'],
		default = 'breadthfirst'
	)

	gv_options.add_argument(
		'--gv-overlap', '-R',
		action = 'store',
		type = str,
		choices = ['prism0', 'prisim10000', 'voroni', 'scalexy', 'compress', 'vpsc', 'ortoxy', 'orthoyx', 'ortho', 'false', 'true'],
		default = 'scalexy'
	)


	args = parser.parse_args()

	setup_logging(args)


	if args.directory is not None:
		log.info(f'Extracting deps from {args.directory}')
		deps = list(filter(lambda d: d is not None, map(
			lambda d: get_deps(d, args),
			filter(
				lambda f: not f.is_dir(),
				chain.from_iterable(map(
					lambda d: list(d.iterdir()),
					args.directory
				))
			)
		)))

		log.info(f'Found {len(deps)} objects')

		if args.graphviz:
			log.info('Generating graphviz output')
			emit_graphviz(deps, args)


	return 0
