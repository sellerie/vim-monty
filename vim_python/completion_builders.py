"""Should contain functions to build a completion entry by one language element

At this point only a builder for VIM exists.
"""
from vim_python.logger import log


def vim_completion_builder(completionable):
    """Completion builder for a entry of the VIM omni completion.
    """
    try:
        word = completionable.complex_name()
        return {
            'word': word,
            'abbr': word,
            'kind': completionable.kind(),
            'menu': str(completionable.linenumber() or ''),
            'dup': '1',
        }
    except Exception, exc:
        log(exc)
        import traceback
        log(traceback.format_exc())
        return completionable.name()
