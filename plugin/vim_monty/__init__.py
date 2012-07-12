"""Use the Source class of this module to work.
"""
import source
import completion_builders


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
    global vim_completion_builder
    vim_completion_builder = vim_completion_builder


vim_completion_builder = completion_builders.vim_completion_builder


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
 

def completion(src, line, lineno, column, base, completion_builder=None):
    """This is the entry point for the completion.
    """
    file_state = source.FileState(line, src, lineno, column)
    return source.completion(file_state, base, completion_builder)
