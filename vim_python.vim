
if !has('python')
    echo "Error: You need to compile vim with '+python'"
    finish
endif


python << eopython
import vim
import vim_python
reload(vim_python)
vim_python.reload_submodules()
eopython


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
completions = vim_python.Source(source).completion(line, row, column, base)
vim.command('return %s' % completions)
eopython
    endif
endfunction

