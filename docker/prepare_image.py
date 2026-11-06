"""Set up container-only paths and fail-fast simulation execution (Python 2/3)."""
from __future__ import print_function

import json
import os
import platform
import subprocess

ROOT = '/home/tungthanhle/gem5'
EXAMPLES = ROOT + '/interconnect-routing-gym/example'


def main():
    filename = EXAMPLES + '/icn_gym.py'
    with open(filename) as handle:
        source = handle.read()
    replacements = (
        ('import os\n', 'import os\nimport shlex\nimport subprocess\n'),
        ('build/NULL/gem5.debug', 'build/NULL/gem5.opt'),
        ('os.system(os_command)',
         'subprocess.check_call(shlex.split(os_command), cwd=path)'),
    )
    for old, new in replacements:
        if source.count(old) != 1:
            raise RuntimeError('Unexpected source layout for replacement: ' + old)
        source = source.replace(old, new)
    with open(filename, 'w') as handle:
        handle.write(source)

    os.symlink('/results/m5out', ROOT + '/m5out')
    os.symlink('/results/network_stats.txt',
               ROOT + '/interconnect-routing-gym/network_stats.txt')
    os.symlink('/results', ROOT + '/interconnect-routing-gym/Inter_Connect_Networks')

    import numpy
    import matplotlib
    info = {
        'gem5_commit': subprocess.check_output(
            ['git', '-C', ROOT, 'rev-parse', 'HEAD']).decode('ascii').strip(),
        'gem5_version': '20.0.0.3',
        'protocol': 'Garnet_standalone',
        'binary': 'build/NULL/gem5.opt',
        'python': platform.python_version(),
        'numpy': numpy.__version__,
        'matplotlib': matplotlib.__version__,
        'container_only_changes': [
            'Use gem5.opt instead of gem5.debug.',
            'Raise on simulator failure; run simulator from gem5 root.',
            'Redirect m5out, network_stats and experiment output to /results.',
        ],
    }
    with open('/opt/rle-noc/build-info.json', 'w') as handle:
        json.dump(info, handle, indent=2, sort_keys=True)
        handle.write('\n')


if __name__ == '__main__':
    main()
