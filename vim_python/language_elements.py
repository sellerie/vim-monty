

def class_name(astng_element):
    return "LE%s" % astng_element.__class__.__name__


class LanguageElement(object):
    def __init__(self, astng_element, context_string=""):
        self.astng_element = astng_element
        self.context_string = context_string

    @classmethod
    def create(cls, astng_element):
        klass = globals().get(class_name(astng_element), cls)
        return klass(astng_element)

    def lookup(self, context_string):
        """Evaluate the given context string on this element.

        A context string is a path like 'os.path.dirname'.
        See 'Source.context_string'.
        """
        context = self.astng_element
        for p in context_string.split('.'):
            scope, contexts = context.lookup(p)
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
        pass

    def implementaion(self):
        """Returns the filename (path) and the line number of this element.
        """
        pass

    def startswith(self, init_string):
        return self.astng_element.name.startswith(init_string)

    def completion_entry(self):
        """Returns the entry for the vim completion menu.
        """
        # TODO
        return self.astng_element.name


