"""This module contains classes to represent language elements of python.

The classes contain some analytic methods used on completion.
"""
from logilab.astng.exceptions import InferenceError

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


def le_class_name(astng_element):
    """Returns the name of the special implementation class.
    """
    return "Le%s" % astng_element.__class__.__name__


class LanguageElement(completionable.Completionable):
    """A instance of this class represents a python language element.

    This module contains some special implementations of this class for some
    language elements like ``LeClass`` for classes.
    """
    def __init__(self, astng_element, context_string="", name=None):
        super(LanguageElement, self).__init__(name)
        self.astng_element = astng_element
        self.context_string = context_string

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

    def name(self):
        """Returns the name of this element.
        """
        if self._name:
            return self._name
        return self.astng_element.name

    def linenumber(self):
        return self.astng_element.fromlineno


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
    KIND = 'm'

    def bounded_accessibles(self):
        return self.free_accessibles()


class LeImport(LanguageElement):
    """This language element represent a python import command.
    """
    KIND = 'm'

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
    def complex_name(self):
        try:
            imported = self.imported(self.name())
            return imported.complex_name()
        except InferenceError:
            return self.name()

    def kind(self):
        imported = self.imported(self.name())
        return imported.kind()

    def imported(self, name=None):
        """Returns the imported language element.
        """
        if not name:
            name = self.context_string.split('.')[-1]
        module_name = self.astng_element.modname
        try:
            import_path = module_name + '.' + name
            astng_element = self.astng_element.do_import_module(import_path)
        except InferenceError:
            imported_module = self.astng_element.do_import_module(module_name)
            try:
                astng_element = imported_module[name]
            except KeyError:
                astng_element = imported_module[self.name()]
        return LanguageElement.create(astng_element, name=name,
                                      context_string=self.context_string)
    def bounded_accessibles(self):
        return self.imported().bounded_accessibles()


class LeClass(LanguageElement):
    """Language element of class elements.
    """
    KIND = 'c'

    def __init__(self, *args, **kwargs):
        super(LeClass, self).__init__(*args, **kwargs)
        self._bases = None

    def complex_name(self):
        # TODO add constructor arguments here:
        return self.name() + '('

    def free_accessibles(self):
        return self.parent().free_accessibles()

    def base_classes(self):
        """Returns language elements of base classes of this class.
        """
        if self._bases is None:
            self._bases = [LanguageElement.create(base,
                                             context_string=self.context_string)
                           for base in self.astng_element.bases]
        return self._bases

    def bounded_accessibles(self):
        result = set(LanguageElement.create(astng_element, name=name,
                                            context_string=self.context_string)
                     for name, astng_element in self.astng_element.items())
        for base_class in self.base_classes():
            result.update(base_class.bounded_accessibles())
        return list(result)

    def instance_attributes(self):
        """Returns the instance attributes of this class.
        """
        result = set()
        for name, values in self.astng_element.instance_attrs.iteritems():
            result.add(LanguageElement.create(values[0], name=name,
                                            context_string=self.context_string))
        for base_class in self.base_classes():
            result.update(base_class.instance_attributes())
        return list(result)

    def bounded_accessibles_instance(self):
        """Returns the bounded accessible of a instance of this class.
        """
        return self.instance_attributes() + self.bounded_accessibles()


class LeFunction(LanguageElement):
    """This language element represent a python function or method.
    """
    KIND = 'f'

    def complex_name(self):
        return '%s(%s)' % (self.name(), self.astng_element.args.as_string())


class LeInstance(LanguageElement):
    """This language element represent a class instantiation.
    """
    KIND = 'i'

    def get_class(self):
        """Returns the language element of the class for this instance.
        """
        class_name = self.astng_element.pytype()
        if class_name[0] == '.':
            class_name = class_name[1:]
        path_elements = class_name.split('.')
        short_class_name = path_elements[-1]
        astng_module = self.astng_element.parent
        the_class_astng_element = astng_module[short_class_name]
        return LeClass(the_class_astng_element,
                       context_string=self.context_string)

    def bounded_accessibles(self):
        return self.get_class().bounded_accessibles_instance()


class LeConst(LanguageElement):
    """This language element represent a constant element.

    At this point I think this can only be a builtin.
    """
    from logilab.astng.builder import ASTNGBuilder
    from logilab.common.compat import builtins
    BUILTINS = ASTNGBuilder().inspect_build(builtins)
    KIND = 'b'

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
    KIND = 'v'

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

    def instance_attributes(self):
        """Returns the instance attributes of this class.
        """
        return self.infer().instance_attributes()


class LeAssName(LeName):
    """This is like 'LeName' but represent a variable assignment.
    """


class LeAssAttr(LeName):
    """A argument of a function.
    """
    KIND = 'a'
