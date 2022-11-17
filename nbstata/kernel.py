# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/04_kernel.ipynb.

# %% auto 0
__all__ = ['PyStataKernel', 'Cell']

# %% ../nbs/04_kernel.ipynb 4
from .config import get_config, launch_stata
from . import parsers
from .magics import StataMagics
from fastcore.basics import patch_to
from ipykernel.ipkernel import IPythonKernel
import os
import sys
from packaging import version

# %% ../nbs/04_kernel.ipynb 5
class PyStataKernel(IPythonKernel):
    implementation = 'nbstata'
    implementation_version = '0.0.1'
    language = 'stata'
    language_version = '17'
    language_info = {
        'name': 'stata',
        'mimetype': 'text/x-stata',
        'codemirror_mode': 'stata',
        'file_extension': '.do',
    }
    banner = "nbstata: a Jupyter kernel for Stata based on pystata"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stata_ready = False
        self.shell.execution_count = 0
        self.magic_handler = None
        self.env = None

# %% ../nbs/04_kernel.ipynb 6
@patch_to(PyStataKernel)
def init_stata(self):
    def _set_graph_format(graph_format):
        if graph_format == 'nbstata':
            pass
        else:
            from pystata.config import set_graph_format
            set_graph_format(graph_format)
    
    self.env = get_config()
    if self.env['echo'] not in ('True', 'False', 'None'):
        raise OSError("'" + self.env['echo'] + "' is not an acceptable value for 'echo'.")

    launch_stata(self.env['stata_dir'], self.env['edition'],
                 False if self.env['splash']=='False' else True)

    _set_graph_format(self.env['graph_format'])

    self.magic_handler = StataMagics()

    self.stata_ready = True

# %% ../nbs/04_kernel.ipynb 7
class Cell:
    def __init__(self, kernel, code_w_magics):
        if kernel.env['echo'] == 'None':
            self.noecho = True
            self.echo = False
        elif kernel.env['echo'] == 'True':
            self.noecho = False
            self.echo = True
        else:
            self.noecho = False
            self.echo = False
        self.quietly = False
        self.code = kernel.magic_handler.magic(code_w_magics, kernel, self)
    
    def run(self):
        if self.code != '':
            if self.noecho and not self.quietly:
                from nbstata.helpers import run_noecho
                run_noecho(self.code)
            else:
                from pystata.stata import run
                run(self.code, quietly=self.quietly, inline=True, echo=self.echo)

# %% ../nbs/04_kernel.ipynb 17
@patch_to(PyStataKernel)
def do_execute(self, code, silent, store_history=True, user_expressions=None,
               allow_stdin=False):
    if not self.stata_ready:
        self.init_stata()
    Cell(self, code).run()
    self.shell.execution_count += 1
    return {
        'status': 'ok',
        'execution_count': self.execution_count,
        'payload': [],
        'user_expressions': {},
        }
