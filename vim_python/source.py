"""Interface to simplify source code analysis with astng.
"""
from logilab.astng.builder import ASTNGBuilder

import language_elements


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

    def context_string(self, line, linenumber, column):
        """Return the context string marked by the given line and column number.

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

    def completion(self, line, linenumber, column, base):
        try:
            accessibles = self.context(line, linenumber, column).accessibles()
            return [accessible.completion_entry() for accessible in accessibles
                    if accessible.startswith(base)]
        except Exception, exc:
            log(exc)
            import traceback
            log(traceback.format_exc())
            return []


def indention_by_line(line):
    indention = ''
    for char in line:
        if char == ' ' or char == '\n':
            indention += char
        else:
            break
    return indention


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
                safe_line = indention_by_line(original_line) + 'pass'
                log(safe_line)
                source_lines[linenumber] = safe_line
            module = cls.BUILDER.string_build('\n'.join(source_lines))
        except Exception, exc:
            if linenumber is not None:
                raise NotImplementedError("TODO")
            else:
                raise exc
        return cls(module)

