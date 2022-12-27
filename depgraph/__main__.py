#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
import sys
from pathlib import Path

try:
	from depgraph import cli_main
except ImportError:
	depgraph_path = Path(sys.argv[0]).resolve()

	if (depgraph_path.parent / 'depgraph').is_dir():
		sys.path.insert(0, str(depgraph_path.parent))

	from depgraph import cli_main

sys.exit(cli_main())
