#!/usr/bin/env python3

import platform
import sys

import pytest

ARGS = [#'--run-slow',
        #'--collect-only',
        '--capture=no',  # a.k.a. -s
        #'--verbose',
        #'--pdb',
        #'--exitfirst',  # a.k.a. -x
        #'-W', 'error',
        ]

if platform.system() == 'Windows':
    if 'idlelib' in sys.modules:
        ARGS += ['--capture=sys', '--color=no']

args = sys.argv[1:] + ARGS

print(f'pytest.main({args!r})')
sys.exit(pytest.main(args))
