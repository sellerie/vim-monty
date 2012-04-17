"""Contains a class that defines a interface for completionables.
"""


class Completionable(object):
    """This class is the interface for a completionable element.

    Completionalbe is the support of the completion_entry, and startswith
    methods.  This class is extended by the LanguageElement classes.
    """
    KIND = '?'

    def __init__(self, name):
        self._name = name

    def name(self):
        """Returns the name of this element.
        """
        return self._name

    def complex_name(self):
        """Overwrite this to return a complexer name of the given element.

        For example: function name with arguments.
        """
        return self.name()

    def kind(self):
        """Returns a char that represents the kind of the completionable.
        
        Overwrite this method with a special implementation for every
        completionable.
        """
        return self.KIND

    def linenumber(self):
        """The completionable is defined on the resulting linenumber
        """
        return ''

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

    def completion_entry(self, completion_builder=None):
        """Returns the entry for the completion list.
        """
        if completion_builder:
            return completion_builder(self)
        return self.name()

    def startswith(self, init_string):
        """Like str.startswith, works on the element name.
        """
        return self.name().startswith(init_string)

