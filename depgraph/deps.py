# SPDX-License-Identifier: BSD-3-Clause

import logging            as log

from elftools.elf.elffile import ELFFile


__all__ = (
	'get_deps',
)

def get_deps(obj, args):
	_KNOWN_LIBS = [
		'ld-linux-x86-64.so',
	]

	if args.filter_common:
		_KNOWN_LIBS += [
			'libc.so',
			'libgcc_s.so',
			'libstdc++.so',
			'libpthread.so',
			'libm.so',
			'libdl.so',
			'libgomp.so',
			'librt.so',
			'libedit.so',
			'libz.so',
		]

	is_lib = '.so' in obj.name

	if is_lib:
		name = f'{obj.name.split(".so")[0]}.so'
	else:
		name = obj.name

	dep = {
		'name': name,
		'lib': is_lib
	}

	if not obj.exists():
		return None

	try:
		needed = None
		soname = None

		with obj.open('rb') as f:
			elf = ELFFile(f)
			dyn = elf.get_section_by_name('.dynamic')

			needed = map(
				lambda s: s.needed,
				dyn.iter_tags(type = 'DT_NEEDED')
			)

			soname = map(
				lambda s: s.soname,
				dyn.iter_tags(type = 'DT_SONAME')
			)

			dep['deps'] = list(filter(
				lambda d: d not in _KNOWN_LIBS,
				map(
					lambda n: f'{n.split(".so")[0]}.so',
					needed
				)
			))

			dep['soname'] = list(map(
				lambda n: f'{n.split(".so")[0]}.so',
				soname
			))

		if len(dep['deps']) == 0:
			dep['terminal'] = True
		else:
			dep['terminal'] = False

		log.debug(f'Found {len(dep["deps"])} deps for {obj.name}')
		for d in dep['deps']:
			log.debug(f'\t * {d}')

	except:
		return None

	return dep
