"""Use the Source class of this module to work.
"""
import source
import logger


def reload_submodules():
    """Reload every imported module to simplify development.
    """
    for name, value in globals().iteritems():
        if(not name.startswith('__') and not name.endswith('__') and
           value.__class__.__name__ == 'module'):
            if hasattr(value, 'reload_submodules'):
                value.reload_submodules()
            reload(value)
    global Source
    Source = source.Source


Source = source.Source
__builtins__['log'] = logger.log


def find_base_column(line, column):
    # TODO: This method is a copy from pysmell, but it's not perfect.
    index = column
    # col points at the end of the completed string
    # so col-1 is the last character of base
    while index > 0:
        index -= 1
        if line[index] in '. ([{:,=<>':
            index += 1
            break
    return index # this is zero based :S
 
