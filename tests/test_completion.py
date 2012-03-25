"""Test of completion functionality.
"""
# pylint: disable-msg=C0111
import os
import sys

from vim_python import Source


HERE = os.path.dirname(__file__)
FIXTURES = os.path.join(HERE, 'fixtures')


# Append fixtures path to import modules from fixtures directory
sys.path.append(FIXTURES)


class AModule(object):
    """Contains informations about the test source code.
    
    This is only to namespace this data.
    """
    SOURCE_STR = open(os.path.join(FIXTURES, 'a_module.py')).read()
    SOURCE = Source(SOURCE_STR)
    LAST_LINE = len(SOURCE_STR.split('\n')) - 1
    GLOBALS = ['AClass', 'A_CLASS', 'A_INSTANCE', 'A_INTEGER', 'A_STRING',
               'BClass']
    A_CLASS_ELEMENTS = ['CLASS_VAR', 'a_method', 'b_class_method', '__init__']


def test_module():
    compls = AModule.SOURCE.completion('', AModule.LAST_LINE, 0, '')
    assert AModule.GLOBALS == compls


def test_imported():
    python_code = "import a_module\na_module.\n"
    compls = Source(python_code).completion('a_module.', 2, 8, '')
    assert AModule.GLOBALS == compls


def test_method_scope():
    method_variables = ['a_var', 'arg1', 'arg2', 'self']
    compls = AModule.SOURCE.completion('        ', 16, 8, '')
    assert sorted(method_variables + AModule.GLOBALS) == compls


def test_class():
    line = 'AClass.'
    compls = AModule.SOURCE.completion(line, AModule.LAST_LINE, len(line), '')
    for class_element in AModule.A_CLASS_ELEMENTS:
        assert class_element in compls

    line = 'A_CLASS.'
    compls = AModule.SOURCE.completion(line, AModule.LAST_LINE, len(line), '')
    for class_element in AModule.A_CLASS_ELEMENTS:
        assert class_element in compls


def test_deep():
    line = "AClass.CLASS_VAR."
    compls = AModule.SOURCE.completion(line, AModule.LAST_LINE, len(line), '')
    assert '__add__' in compls


def test_instance():
    line = "A_INSTANCE."
    compls = AModule.SOURCE.completion(line, AModule.LAST_LINE, len(line), '')
    for instance_element in AModule.A_CLASS_ELEMENTS + ['_instance_attr']:
        assert instance_element in compls


def test_from():
    line = 'BClass.'
    compls = AModule.SOURCE.completion(line, AModule.LAST_LINE, len(line), '')
    assert 'b_class_method' in compls

    # Test of a deeper from import, BClass is also imported by 'a_module'.
    python_code = 'from a_module import BClass\n\n'
    compls = Source(python_code).completion(line, 2, len(line), '')
    assert 'b_class_method' in compls


def test_builtin():
    line = 'A_STRING.'
    compls = AModule.SOURCE.completion(line, AModule.LAST_LINE, len(line), '')
    assert 'startswith' in compls

