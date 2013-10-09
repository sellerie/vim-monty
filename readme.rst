
.. warning::
   I will not maintain this project anymore.
   Use https://github.com/davidhalter/jedi-vim instead.


=========================
Python development in Vim
=========================

With this code I try to extend Vim_ with features related to python_
development.  At first this project should contain two features:

 * a better *omnicompletion* functionality (in progress)

 * a go-to-implementation functionality (TODO)

This project is in an early state and has many issues.

.. _Vim: http://www.vim.org
.. _python: http://www.python.org


Install
=======

If you use Vundle_, simply add this repository (`on github`_) as Bundle to
your vim configuration::

   Bundle 'sellerie/vim-monty'

.. _Vundle: https://github.com/gmarik/vundle
.. _on github: https://github.com/sellerie/vim-monty


The completion is based on logilab-astng library, so you need to install this
by::

   $ pip install logilab-astng


Usage
=====

At this point only *omnicompletion* is supported.  So you can do tasks like::

   import os.<C-X><C-O>
   from os import <C-X><C-O>
   os.pa<C-X><C-O>

Tests
=====

Vim-monty's unittests are written with the py.test_ framework.  This can be
installed with::

   $ pip install pytest

After that you can run the unittests by::

   $ PYTHONPATH=plugin py.test

.. _py.test: http://pytest.org
