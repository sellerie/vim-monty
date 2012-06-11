
if !has('python')
    echo "Error: You need to compile vim with '+python'"
    finish
endif

let s:here=expand("<sfile>:h")

let s:pythonpath=system('python -c "import sys,os;print(os.linesep.join(sys.path))"')

python << eopython
import sys
import os

import vim

# improve this by running the completion functionality through an extra program
sys.path.extend(vim.eval('s:pythonpath').split(os.linesep))
sys.path.append(vim.eval('s:here'))
import vim_monty
reload(vim_monty)
vim_monty.reload_submodules()
eopython


autocmd FileType python call PythonCompleteInit()


function! PythonCompleteInit()
  setlocal omnifunc=vim_monty#Complete

  if !exists('g:vim_monty_debug')
    let g:vim_monty_debug = 0
  endif

python << eopython
from vim_monty import logger
logger.ENABLED = bool(int(vim.eval('g:vim_monty_debug')))

eopython
endfunction


function! vim_monty#Complete(findstart, base)
    " see :help complete-functions
    if a:findstart == 1
python << eopython
row, column = vim.current.window.cursor
line = vim.current.buffer[row-1]
index = vim_monty.find_base_column(line, column)
vim.command('let g:vim_monty_column = %d' % index)
vim.command('let g:vim_monty_line = %r' % line)
vim.command('return %d' % index)
eopython
    else
python << eopython
column = int(vim.eval('g:vim_monty_column'))
row, _column = vim.current.window.cursor
line = vim.eval('g:vim_monty_line')
source = '\n'.join(vim.current.buffer[:])
base = vim.eval("a:base")
completions = vim_monty.Source(source).completion(line, row, column, base,
                                             vim_monty.vim_completion_builder)
vim.command('return %s' % completions)
eopython
    endif
endfunction
