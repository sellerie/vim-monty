"""This module contains classes to represent language elements of python.

The classes contain some analytic methods used on completion.
"""
from logilab.astng.exceptions import InferenceError

from logger import log


def le_class_name(astng_element):
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
        klass = globals().get(le_class_name(astng_element), LanguageElement)
        return klass(astng_element, *args, **kwargs)

    def parent(self):
        """Returns the parent of this element.

        The parent is the class for a method or the module for a
        module function, ...
        """
        return LanguageElement.create(self.astng_element.parent,
                                      context_string=self.context_string)

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
        return LanguageElement.create(context,
                                      context_string=context_string)

    def accessibles(self):
        """Return a list of every accessible sub of this language element.
        """
        if self.context_string:
            return self.bounded_accessibles()
        else:
            return self.free_accessibles()

    def bounded_accessibles(self):
        """Return all bounded accessible of this element.
        """
        raise NotImplementedError('Implement %s.bounded_accessibles' %
                                  le_class_name(self.astng_element))

    def free_accessibles(self):
        """Return all free accessible of this module
        """
        accessibles = []
        for name, accessible in self.astng_element.items():
            accessibles.append(LanguageElement.create(accessible, name=name,
                                            context_string=self.context_string))
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

    def bounded_accessibles(self):
        return []


class LeModule(LanguageElement):
    """This language element represent a python module.
    """
    def bounded_accessibles(self):
        return self.free_accessibles()


class LeImport(LanguageElement):
    """This language element represent a python import command.
    """
    def import_path(self):
        """Returns the import path.
        """
        return self.astng_element.names[0][0]

    def imported(self):
        """Imports this module.
        """
        astng_imported = self.astng_element.do_import_module(self.import_path())
        return LanguageElement.create(astng_imported,
                                      context_string=self.context_string)

    def bounded_accessibles(self):
        return self.imported().bounded_accessibles()


class LeFrom(LanguageElement):
    """This language element represent a element imported with from
    """
    def imported(self):
        """Returns the imported language element.
        """
        name = self.context_string.split('.')[-1]
        module_name = self.astng_element.modname
        try:
            import_path = module_name + '.' + name
            astng_element = self.astng_element.do_import_module(import_path)
        except InferenceError:
            imported_module = self.astng_element.do_import_module(module_name)
            astng_element = imported_module[name]
        return LanguageElement.create(astng_element, name=name,
                                      context_string=self.context_string)
    def bounded_accessibles(self):
        return self.imported().bounded_accessibles()


class LeClass(LanguageElement):
    """Language element of class elements.
    """
    def free_accessibles(self):
        return self.parent().free_accessibles()

    def bounded_accessibles(self):
        result = set(LanguageElement.create(astng_element, name=name,
                                            context_string=self.context_string)
                     for name, astng_element in self.astng_element.items())
        for base in self.astng_element.bases:
            base_element = LanguageElement.create(base,
                                             context_string=self.context_string)
            result.update(base_element.bounded_accessibles())
        return list(result)

    def instance_attributes(self):
        """Returns the instance attributes of this class.
        """
        result = []
        for name, values in self.astng_element.instance_attrs.iteritems():
            result.append(LanguageElement.create(values[0], name=name,
                                            context_string=self.context_string))
        return result

    def bounded_accessibles_instance(self):
        """Returns the bounded accessible of a instance of this class.
        """
        return self.instance_attributes() + self.bounded_accessibles()


class LeInstance(LanguageElement):
    """This language element represent a class instantiation.
    """
    def bounded_accessibles(self):
        class_name = self.astng_element.pytype()
        if class_name[0] == '.':
            class_name = class_name[1:]
        path_elements = class_name.split('.')
        short_class_name = path_elements[-1]
        astng_module = self.astng_element.parent
        the_class_astng_element = astng_module[short_class_name]
        the_class = LeClass(the_class_astng_element,
                            context_string=self.context_string)
        return the_class.bounded_accessibles_instance()


class LeConst(LanguageElement):
    """This language element represent a constant element.

    At this point I think this can only be a builtin.
    """
    from logilab.astng.builder import ASTNGBuilder
    from logilab.common.compat import builtins
    BUILTINS = ASTNGBuilder().inspect_build(builtins)

    def bounded_accessibles(self):
        name = self.astng_element.pytype()
        if name.startswith('__builtin__'):
            name = name.split('.')[-1]
            builtin_astng_element = self.BUILTINS[name]
            element = LanguageElement.create(builtin_astng_element, name=name,
                                             context_string=self.context_string)
            return element.bounded_accessibles()
        raise RuntimeError("The const type %s is no builtin." %
                           self.astng_element)


class LeName(LanguageElement):
    """This is simply a python variable.
    """
    def infer(self):
        """Find a more specific representation of the variable content.
        """
        infereds = self.astng_element.infered()
        if infereds:
            return LanguageElement.create(infereds[0],
                                          context_string=self.context_string)
        log("Could not infer name: %s" % self.name())
        return LeNoneType(None)
    
    def bounded_accessibles(self):
        return self.infer().bounded_accessibles()


class LeAssName(LeName):
    """This is like 'LeName' but represent a variable assignment.
    """
    pass
