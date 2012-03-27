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

    @staticmethod
    def completion(line, linenumber=None, column=None, base=''):
        if linenumber is None:
            linenumber = AModule.LAST_LINE
        if column is None:
            column = len(line)
        return AModule.SOURCE.completion(line, linenumber, column, base)


def test_module():
    assert AModule.GLOBALS == AModule.completion('')


def test_imported():
    python_code = "import a_module\na_module.\n"
    compls = Source(python_code).completion('a_module.', 2, 8, '')
    assert AModule.GLOBALS == compls


def test_method_scope():
    method_variables = ['a_var', 'arg1', 'arg2', 'self']
    compls = AModule.completion('        ', 16)
    assert sorted(method_variables + AModule.GLOBALS) == compls


def test_class():
    compls = AModule.completion("AClass.")
    for class_element in AModule.A_CLASS_ELEMENTS:
        assert class_element in compls

    compls = AModule.completion("A_CLASS.")
    for class_element in AModule.A_CLASS_ELEMENTS:
        assert class_element in compls


def test_deep():
    compls = AModule.completion("AClass.CLASS_VAR.")
    assert '__add__' in compls


def test_instance():
    compls = AModule.completion("A_INSTANCE.")
    instance_elements = ['_instance_attr', '_b_attr']
    for instance_element in AModule.A_CLASS_ELEMENTS + instance_elements:
        assert instance_element in compls


def test_from():
    line = 'BClass.'
    compls = AModule.completion(line)
    assert 'b_class_method' in compls

    # Test of a deeper from import, BClass is also imported by 'a_module'.
    python_code = 'from a_module import BClass\n\n'
    compls = Source(python_code).completion(line, 2, len(line), '')
    assert 'b_class_method' in compls


def test_builtin():
    compls = AModule.completion("A_STRING.")
    assert 'startswith' in compls


PACKAGE_MODULES = ['completionable', 'language_elements', 'logger', 'source']


def test_import_line():
    line = "import vim_python."
    compls = Source("\n\n").completion(line, 1, len(line), '')
    assert PACKAGE_MODULES == compls

    line = "from vim_python."
    compls = Source("\n\n").completion(line, 1, len(line), '')
    assert PACKAGE_MODULES == compls


def test_from_line():
    line = "from vim_python import "
    compls = Source("\n\n").completion(line, 1, len(line), '')
    expect = sorted(PACKAGE_MODULES +
                    ['Source', 'find_base_column', 'reload_submodules'])
    assert expect == compls

