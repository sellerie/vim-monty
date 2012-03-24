"""This module contains classes to represent language elements of python.

The classes contain sum analytic methods used on completion.
"""


def class_name(astng_element):
    """Returns the name of the special implementation class.
    """
    return "Le%s" % astng_element.__class__.__name__


class LanguageElement(object):
    """A instance of this class represents a python language element.

    This module contains some special implementations of this class for some
    language elements like ``LeClass`` for classes.
    """
    def __init__(self, astng_element, context_string="", name=None):
        self.astng_element = astng_element
        self.context_string = context_string
        self._name = name

    @staticmethod
    def create(astng_element, *args, **kwargs):
        """Creates a LanguageElement instance for the given astng_element.

        Creates the special class, LanguageElement is only the fallback.
        """
        klass = globals().get(class_name(astng_element), LanguageElement)
        return klass(astng_element, *args, **kwargs)

    def parent(self):
        """Returns the parent of this element.

        The parent is the class for a method or the module for a
        module function, ...
        """
        return LanguageElement.create(self.astng_element.parent)

    def lookup(self, context_string):
        """Evaluate the given context string on this element.

        A context string is a path like 'os.path.dirname'.
        See 'Source.context_string'.
        """
        context = self.astng_element
        for path_element in context_string.split('.'):
            _scope, contexts = context.lookup(path_element)
            if contexts:
                # TODO: multiple names
                context = contexts[0]
                if context.__class__.__name__ == 'Import':
                    module_name = context.names[0][0]
                    context = context.do_import_module(module_name)
            else:
                return self
        return LanguageElement.create(context, context_string)

    def accessibles(self):
        """Return a list of every accessible sub of this language element.
        """
        if self.context_string:
            return self.bounded_accessibles()
        else:
            return self.free_accessibles()

    def bounded_accessibles(self):
        """Return all bounded accessibles of this element.
        """
        raise NotImplementedError('Implement %s.bounded_accessibles' %
                                  class_name(self.astng_element))

    def free_accessibles(self):
        """Return all free accessibles of this module
        """
        accessibles = []
        for name, accessible in self.astng_element.items():
            accessibles.append(LanguageElement.create(accessible, name=name))
        return accessibles + self.parent().free_accessibles()

    def implementaion(self):
        """Returns the filename (path) and the line number of this element.
        """
        pass

    def name(self):
        """Returns the name of this element.
        """
        if self._name:
            return self._name
        return self.astng_element.name

    def startswith(self, init_string):
        """Like str.startswith on self.name().
        """
        return self.name().startswith(init_string)

    def completion_entry(self):
        """Returns the entry for the vim completion menu.
        """
        return self.name()


class LeNoneType(LanguageElement):
    """Language element if the element can not be found.
    """
    def free_accessibles(self):
        return []


class LeClass(LanguageElement):
    """Language element of class elements.
    """
    def free_accessibles(self):
        return self.parent().free_accessibles()

