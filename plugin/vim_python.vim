
if !has('python')
    echo "Error: You need to compile vim with '+python'"
    finish
endif

let s:here=expand("<sfile>:h")

python << eopython
import sys

import vim

sys.path.append(vim.eval('s:here'))
import vim_python
reload(vim_python)
vim_python.reload_submodules()
eopython


autocmd FileType python call PythonCompleteInit()


function! PythonCompleteInit()
  setlocal omnifunc=vim_python#Complete
endfunction


function! vim_python#Complete(findstart, base)
    " see :help complete-functions
    if a:findstart == 1
python << eopython
row, column = vim.current.window.cursor
line = vim.current.buffer[row-1]
index = vim_python.find_base_column(line, column)
vim.command('let g:vim_python_column = %d' % index)
vim.command('let g:vim_python_line = %r' % line)
vim.command('return %d' % index)
eopython
    else
python << eopython
column = int(vim.eval('g:vim_python_column'))
row, _column = vim.current.window.cursor
line = vim.eval('g:vim_python_line')
source = '\n'.join(vim.current.buffer[:])
base = vim.eval("a:base")
completions = vim_python.Source(source).completion(line, row, column, base,
                                             vim_python.vim_completion_builder)
vim.command('return %s' % completions)
eopython
    endif
endfunction
