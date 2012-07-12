"""Should contain functions to build a completion entry by one language element

At this point only a builder for VIM exists.
"""
from vim_monty.logger import log


def vim_completion_builder(completionable, file_state):
    """Completion builder for a entry of the VIM omni completion.
    """
    try:
        complex_name = completionable.complex_name()
        if file_state:
            if file_state.is_import_path() or file_state.is_from_import():
                complex_name = completionable.name()
        return {
            'word': complex_name,
            'abbr': completionable.name(),
            'kind': completionable.kind(),
            'menu': str(completionable.linenumber() or ''),
            'dup': '1',
        }
    except Exception, exc:
        log(exc)
        import traceback
        log(traceback.format_exc())
        return completionable.name()
