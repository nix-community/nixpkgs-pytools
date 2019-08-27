SOURCE = '''
import numpy
import numpy.random

numpy.random()
numpy.asdf

def foo():
    numpy = 'asdf'
    numpy.qwer = 1
    return numpy

def bar():
    global numpy
    numpy = 1

def baz():
    numpy.qwer = 'qwer'

dontchange.numpy.asdf = 2
'''

EXPECTED_SOURCE = '''
import mynumpy
import mynumpy.random

mynumpy.random()
mynumpy.asdf

def foo():
    numpy = 'asdf'
    numpy.qwer = 1
    return numpy

def bar():
    global mynumpy
    mynumpy = 1

def baz():
    mynumpy.qwer = 'qwer'

dontchange.numpy.asdf = 2
'''

import os
import tempfile

import pytest

from nixpkgs_pytools.import_rewrite import rename_modules


def test_module_rewrite():
    with tempfile.TemporaryDirectory() as tempdir:
        with open(os.path.join(tempdir, 'example.py'), 'w') as f:
            f.write(SOURCE)

        rename_modules(tempdir, [('numpy', 'mynumpy')])

        assert open(os.path.join(tempdir, 'example.py')).read() == EXPECTED_SOURCE
