"""Interface to simplify source code analysis with logilab astng.
"""
import os

from logilab.astng.builder import ASTNGBuilder

from vim_monty import language_elements
from vim_monty import completionable
from vim_monty.logger import log



def reload_submodules():
    """Reload every imported module to simplify development.
    """
    for name, value in globals().iteritems():
        if(not name.startswith('__') and not name.endswith('__') and
           value.__class__.__name__ == 'module'):
            if hasattr(value, 'reload_submodules'):
                value.reload_submodules()
            reload(value)


def completion(file_state, base='', completion_builder=None):
    """Returns the completion.

    Use this function as entry point to this module.  See __init__.completion.
    """
    try:
        accessibles = file_state.accessibles()
        accessibles.sort()
        return [accessible.completion_entry(completion_builder, file_state)
                for accessible in accessibles if accessible.startswith(base)]
    except Exception, exc:
        log(exc)
        import traceback
        log(traceback.format_exc())
        return []


class FileState(object):
    """Represents the current state in the python file.

    The context is given by *line*, *source*, *linenumber* and *column*.
    """
    def __init__(self, line, source, linenumber, column):
        self.line = line
        self.source = source
        self.linenumber = linenumber
        self.column = column

    def accessibles(self):
        """Returns all accessibles of this file state.
        """
        if self.need_import_statement():
            return [completionable.Completionable('import ')]
        elif self.is_import_path():
            return self.import_path_completion()
        elif self.is_from_import():
            return self.import_completion()
        return self.context().accessibles()

    def context_string(self):
        """Return the context string marked by the line and column number.

        A context string is a path like 'os.path.dirname'.
        """
        column = min(self.column, len(self.line))
        start_index = column
        while start_index > 0:
            start_index -= 1
            if self.line[start_index] in ' \t;([{:,=<>':
                start_index += 1
                break
        string_of_interest = self.line[start_index:self.column]
        if string_of_interest and string_of_interest[-1] == '.':
            return string_of_interest[:-1]
        return string_of_interest

    def context(self):
        """Calc the context element marked by the given line and column number.
        """
        context_string = self.context_string()
        module = PyModule.by_source(self.source, self.linenumber - 1)
        scope = module.scope(self.linenumber)
        return scope.lookup(context_string)

    def import_path_completion(self):
        """Get completion of import paths.

        This method returns the accessible modules and packages in lines like:
        ``import os.`` or ``from os.``.
        """
        import_path = self.context_string()
        module = PyModule.by_module_path(import_path)
        accessibles = module.package_modules()
        accessibles.update(module.accessible_modules())
        return list(accessibles)

    def import_completion(self, import_path=None):
        """Returns completion of from import lines.

        Complete the part after ``import`` in lines like ``from os import``.
        """
        import_path = import_path or self.tokens()[1]
        module = PyModule.by_module_path(import_path)
        accessibles = module.package_modules()
        accessibles.update(module.accessibles())
        return list(accessibles)

    def tokens(self, complete=False):
        """Returns a list of tokens (strings) of the current line.

        If ``complete`` ist true, use only the line before the current column.
        """
        if complete:
            return self.line.strip().split()
        return self.line[:self.column].strip().split()

    def is_import_path(self):
        """Returns true, if the current context is a import path.

        A import path ist the part after import or between from and import.
        """
        tokens = self.tokens()
        return (tokens and
                (tokens[0] == 'import' or
                 (tokens[0] == 'from' and len(tokens) < 3)))

    def is_from_import(self):
        """True, if the context is the part after import of a from line.
        """
        tokens = self.tokens()
        return tokens and tokens[0] == 'from' and tokens[2] == 'import'

    def need_import_statement(self):
        """True, if we are in a from line and now we need the import keyword.
        """
        tokens = self.tokens()
        return (len(tokens) == 2 and
                tokens[0] == 'from' and
                self.line.endswith(' '))


def indention_by_line(line):
    """Returns the indention of the given line.
    """
    indention = ''
    for char in line:
        if char == ' ' or char == '\n':
            indention += char
        else:
            break
    return indention


def is_module_or_package(module_path):
    """Is the given path a python module or package.

    Returns the module name if it is a module or a package, else None.
    """
    module_extensions = ('.py', '.pyc', '.pyo', '.pyw')
    module_file = os.path.basename(module_path)
    module_name, extension = os.path.splitext(module_file)
    if os.path.isdir(module_path):
        for module_extension in module_extensions:
            if '__init__' + module_extension in os.listdir(module_path):
                return module_name
    else:
        if module_name != '__init__' and extension in module_extensions:
            return module_name
    return None


class PyModule(object):
    BUILDER = ASTNGBuilder()

    def __init__(self, module):
        self.astng_module = module

    def scope(self, linenumber, scope=None):
        scope = scope or self.astng_module
        for a_scope in scope.values():
            if a_scope.fromlineno <= linenumber <= a_scope.tolineno:
                scope = self.scope(linenumber, a_scope)
                break
        if isinstance(scope, language_elements.LanguageElement):
            return scope
        return language_elements.LanguageElement.create(scope)

    @classmethod
    def by_source(cls, source, linenumber=None):
        if linenumber is not None:
            source_lines = source.split('\n')
            original_line = source_lines[linenumber]
            indention = indention_by_line(original_line)
            for fill in ('pass', 'except: pass', 'except:', '', original_line):
                try:
                    source_lines[linenumber] = indention + fill
                    module = cls.BUILDER.string_build('\n'.join(source_lines))
                    return cls(module)
                except:
                    pass
            raise NotImplementedError("TODO: Can't parse file")
        else:
            raise RuntimeError("No line number given.")
        return None

    @classmethod
    def by_module_path(cls, module_path):
        helper_module = cls.BUILDER.string_build('')  # TODO: bad
        module = helper_module.import_module(module_path)
        return cls(module)

    def package_modules(self):
        result = set()
        if self.astng_module.package:
            package_dir = os.path.dirname(self.astng_module.file)
            for module_file in os.listdir(package_dir):
                module_path = os.path.join(package_dir, module_file)
                module_name = is_module_or_package(module_path)
                if module_name:
                    result.add(completionable.Completionable(module_name))
        return result

    def accessible_modules(self):
        result = set()
        for accessible in self.accessibles():
            if accessible.__class__.__name__ in ('LeModule', 'LeImport'):
                result.add(accessible)
        return result

    def accessibles(self):
        module = language_elements.LanguageElement.create(self.astng_module)
        return module.accessibles()
