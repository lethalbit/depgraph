# SPDX-License-Identifier: BSD-3-Clause

import logging as log
from re        import Match, compile, finditer, sub

from graphviz  import Digraph

__all__ = (
	'emit_grapviz',
)

def ascii_escape(string: str) -> str:
	''' Apply escaping to turn any character that is not A-Za-z0-9_ into hex '''

	def esc_match(m: Match) -> str:
		if m.group(1) is not None:
			return f'_{ord(m.group(1)[0]):02x}_'
		return m.group(2)

	return ''.join(
		map(esc_match, finditer(r'([^A-Za-z0-9_])|(.)', string))
	)


def emit_graphviz(deps, args):

	log.info(f'graphviz: engine               - \'{args.gv_engine}\'')
	log.info(f'graphviz: clustering subgraphs - \'{args.gv_cluster}\'')
	log.info(f'graphviz: spline type          - \'{args.gv_spline}\'')
	log.info(f'graphviz: dpi                  - \'{args.gv_dpi}\'')
	log.info(f'graphviz: output order         - \'{args.gv_outputorder}\'')
	log.info(f'graphviz: overlap mode         - \'{args.gv_overlap}\'')


	dep_graph = Digraph(
		name    = 'dep-graph',
		comment = 'dependency graph',
		engine  = args.gv_engine
	)

	dep_graph.attr(overlap = args.gv_overlap)
	dep_graph.attr(rankdir = 'LR')
	dep_graph.attr(splines = args.gv_spline)
	dep_graph.attr(dpi = f'{args.gv_dpi}')
	dep_graph.attr(outputorder = args.gv_outputorder)


	for dep in deps:
		if not dep['terminal']:
			sg = Digraph(
				name    = ascii_escape(dep['name']),
				comment = dep
			)
			sg.attr(overlap = args.gv_overlap)
			sg.attr(rankdir = 'TB')
			sg.attr(cluster = 'true' if args.gv_cluster else 'false')
			sg.node(ascii_escape(
				dep['name']), dep['name'],
				shape = 'diamond' if not dep['lib'] else 'ellipse',
				style = 'filled' if not dep['lib'] else ''
			)

			for d in dep['deps']:
				sg.edge(ascii_escape(dep['name']), ascii_escape(d))

			dep_graph.subgraph(sg)
		else:
			dep_graph.node(
				ascii_escape(dep['name']), dep['name'],
				shape = 'box' if dep['lib'] else 'diamond',
				syle = '' if dep['lib'] else 'filled'
			)

	if args.gv_view:
		log.info('Rendering to view')
		dep_graph.view()

	if args.output is not None:
		with args.output.open('w') as f:
			f.write(dep_graph.source)
