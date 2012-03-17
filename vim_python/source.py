"""Interface to simplify source code analysis with astng.
"""
from logilab.astng.builder import ASTNGBuilder


class LanguageElement(object):
    def lookup(self, context_string):
        """Evaluate the given context string on this element.

        A context string is a path like 'os.path.dirname'.
        See 'Source.context_string'.
        """
        pass

    def accessibles(self):
        """Return a list of every accessible sub of this language element.
        """
        pass

    def implementaion(self):
        """Returns the filename (path) and the line number of this element.
        """
        pass


class Source(object):
    """Provides functionality to analyze a python source code
    """
    def __init__(self, source):
        self.source = source

    def analyze(self, *args, **kwargs):
        """Analyze the source code of this instance.
        """
        return PyModule.by_source(self.source, *args, **kwargs)

    def context_string(self, linenumber, column):
        """Return the context string marked by the given line and column number.

        A context string is a path like 'os.path.dirname'.
        """
        pass

    def context(self, linenumber, column):
        """Calc th context element marked by the given line and column number.
        """
        module = self.analyze(linenumber)
        scope = module.scope(linenumber)
        context_string = self.context_string(linenumber, column)
        return scope.lookup(context_string)


class PyModule(object):
    BUILDER = ASTNGBuilder()

    def __init__(self, module):
        self.module = module

    def scope(self, linenumber, scope=None):
        scope = scope or self.module
        for a_scope in scope.values():
            if a_scope.fromlineno <= linenumber <= a_scope.tolineno:
                return self.scope(linenumber, a_scope)
        return scope

    @classmethod
    def by_source(cls, source, linenumber=None):
        try:
            module = cls.BUILDER.string_build(source)
        except Exception, exc:
            if linenumber is not None:
                raise NotImplementedError("TODO")
            else:
                raise exc
        return cls(module)

