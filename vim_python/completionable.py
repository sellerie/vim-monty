"""Contains a class that defines a interface for completionables.
"""


class Completionable(object):
    """This class is the interface for a completionable element.

    Completionalbe is the support of the completion_entry, and startswith
    methods.  This class is extended by the LanguageElement classes.
    """
    def __init__(self, name):
        self._name = name

    def name(self):
        """Returns the name of this element.
        """
        return self._name

    def __cmp__(self, other):
        if self.startswith('__') and not other.startswith('__'):
            return 1
        if not self.startswith('__') and other.startswith('__'):
            return -1
        if self.startswith('_') and not other.startswith('_'):
            return 1
        if not self.startswith('_') and other.startswith('_'):
            return -1
        return cmp(self.name(), other.name())

    def __eq__(self, other):
        return self.name() == other.name()

    def __hash__(self):
        return hash(self.name())

    def completion_entry(self):
        """Returns the entry for the completion list.
        """
        return self.name()

    def startswith(self, init_string):
        """Like str.startswith, works on the element name.
        """
        return self.name().startswith(init_string)

