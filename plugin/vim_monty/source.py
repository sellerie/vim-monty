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


class Source(object):
    """Provides functionality to analyze a python source code
    """
    def __init__(self, source):
        self.source = source

    def analyze(self, *args, **kwargs):
        """Analyze the source code of this instance.
        """
        return PyModule.by_source(self.source, *args, **kwargs)

    def context_string(self, line, _linenumber, column):
        """Return the context string marked by the line and column number.

        A context string is a path like 'os.path.dirname'.
        """
        column = min(column, len(line))
        start_index = column
        while start_index > 0:
            start_index -= 1
            if line[start_index] in ' \t;([{:,=<>':
                start_index += 1
                break
        string_of_interest = line[start_index:column]
        if string_of_interest and string_of_interest[-1] == '.':
            return string_of_interest[:-1]
        return string_of_interest

    def context(self, line, linenumber, column):
        """Calc the context element marked by the given line and column number.
        """
        context_string = self.context_string(line, linenumber, column)
        module = self.analyze(linenumber - 1)
        scope = module.scope(linenumber)
        return scope.lookup(context_string)

    def import_path_completion(self, line, linenumber, column):
        """Get completion of import paths.

        This method returns the accessible modules and packages in lines like:
        ``import os.`` or ``from os.``.
        """
        import_path = self.context_string(line, linenumber, column)
        module = PyModule.by_module_path(import_path)
        accessibles = module.package_modules()
        accessibles.update(module.accessible_modules())
        return list(accessibles)

    def import_completion(self, import_path):
        """Returns completion of from import lines.

        Complete the part after ``import`` in lines like ``from os import``.
        """
        module = PyModule.by_module_path(import_path)
        accessibles = module.package_modules()
        accessibles.update(module.accessibles())
        return list(accessibles)

    def completion(self, line, linenumber, column, base,
                   completion_builder=None):
        """This is the entry point of the completion functionality.

        Returns all in the given context accessible constructs.  The context
        is given by *line*, *linenumber* and *column*.
        """
        try:
            context = Context(line, linenumber, column)
            # TODO: clean up this bad if else chain
            if context.need_import_statement():
                return ['import ']
            elif context.is_import_path():
                accessibles = self.import_path_completion(line, linenumber,
                                                          column)
                completion_builder = None
            elif context.is_from_import():
                accessibles = self.import_completion(context.tokens()[1])
                completion_builder = None
            else:
                ast_context = self.context(line, linenumber, column)
                accessibles = ast_context.accessibles()
            accessibles.sort()
            return [accessible.completion_entry(completion_builder)
                    for accessible in accessibles
                    if accessible.startswith(base)]
        except Exception, exc:
            log(exc)
            import traceback
            log(traceback.format_exc())
            return []


class Context(object):
    """Represents the current context in the python file.

    The context is given by *line*, *linenumber* and *column*.
    """
    # TODO: Maybe add source here:
    # TODO: Rename some functionality, because the name context is already in
    #       use
    def __init__(self, line, linenumber, column):
        self.line = line
        self.linenumber = linenumber
        self.column = column

    def tokens(self, complete=False):
        if complete:
            return self.line.strip().split()
        return self.line[:self.column].strip().split()

    def is_import_path(self):
        tokens = self.tokens()
        return (tokens and
                (tokens[0] == 'import' or
                 (tokens[0] == 'from' and len(tokens) < 3)))

    def is_from_import(self):
        tokens = self.tokens()
        return tokens and tokens[0] == 'from' and tokens[2] == 'import'

    def need_import_statement(self):
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
        try:
            if linenumber is not None:
                source_lines = source.split('\n')
                original_line = source_lines[linenumber]
                indention = indention_by_line(original_line)
                if original_line.strip().startswith('except'):
                    safe_line = indention + 'except: pass'
                else:
                    safe_line = indention + 'pass'
                log(safe_line)
                source_lines[linenumber] = safe_line
            module = cls.BUILDER.string_build('\n'.join(source_lines))
        except Exception, exc:
            if linenumber is not None:
                raise NotImplementedError("TODO: %s" % exc)
            else:
                raise exc
        return cls(module)

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
