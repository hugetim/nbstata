# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/06_kernel.ipynb.

# %% auto 0
__all__ = ['PyStataKernel', 'Cell', 'print_stata_error']

# %% ../nbs/06_kernel.ipynb 4
from .config import get_config, launch_stata
from .utils import print_red, ending_delimiter, is_cr_delimiter
from .stata_session import StataSession
from .magics import StataMagics
from .completions import CompletionsManager
from fastcore.basics import patch_to
from ipykernel.ipkernel import IPythonKernel
import os
import sys
from packaging import version

# %% ../nbs/06_kernel.ipynb 5
class PyStataKernel(IPythonKernel):
    """A jupyter kernel based on pystata"""
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
        self.starting_delimiter = None
        try:
            self.init_stata()
        except ModuleNotFoundError as err:
            pass # wait for first do_execute so error message can be displayed under cell

# %% ../nbs/06_kernel.ipynb 6
def _set_graph_format(graph_format):
    if graph_format != 'pystata':
        from pystata.config import set_graph_format
        set_graph_format(graph_format)

# %% ../nbs/06_kernel.ipynb 7
@patch_to(PyStataKernel)
def init_stata(self):
    self.env = get_config()
    launch_stata(self.env['stata_dir'], self.env['edition'],
                 False if self.env['splash']=='False' else True)
    _set_graph_format(self.env['graph_format'])
    self.stata_session = StataSession()
    self.magic_handler = StataMagics()
    self.completions = CompletionsManager(self.stata_session, list(self.magic_handler.available_magics.keys()))
    self.stata_ready = True

# %% ../nbs/06_kernel.ipynb 8
class Cell:
    """A class for managing execution of a single code cell"""
    def __init__(self, kernel, code_w_magics, silent=False):
        if kernel.env['echo'] == 'None':
            self.noecho = True
            self.echo = False
        elif kernel.env['echo'] == 'True':
            self.noecho = False
            self.echo = True
        else:
            self.noecho = False
            self.echo = False
        self.quietly = silent
        self.starting_delimiter = kernel.starting_delimiter
        self.stata_session = kernel.stata_session
        self.code = kernel.magic_handler.magic(code_w_magics, kernel, self)
    
    def run(self):
        if self.code != '':
            if self.noecho and not self.quietly:
                from nbstata.helpers import run_noecho
                run_noecho(self.code, self.starting_delimiter,
                           run_as_prog=self.stata_session.run_as_prog_with_locals)
            else:
                from pystata.stata import run
                if not is_cr_delimiter(self.starting_delimiter):
                    self.code = "#delimit;\n" + self.code
                run(self.code, quietly=self.quietly, inline=True, echo=self.echo)

# %% ../nbs/06_kernel.ipynb 19
_missing_stata_message = (
    "pystata path not found\n"
    "A Stata 17 installation is required to use the nbstata Stata kernel. "
    "If you already have Stata 17 installed, "
    "please specify its path in your configuration file."
)

# %% ../nbs/06_kernel.ipynb 21
def _handle_stata_import_error(err, silent, execution_count):
    if not silent:
        print_red(f"ModuleNotFoundError: {_missing_stata_message}")
    return {
        "traceback": [],
        "ename": "ModuleNotFoundError",
        "evalue": _missing_stata_message,
        'status': "error",
        'execution_count': execution_count,
    }

# %% ../nbs/06_kernel.ipynb 22
def print_stata_error(text):
    lines = text.splitlines()
    if len(lines) > 2:
        print("\n".join(lines[:-2]))
    print_red("\n".join(lines[-2:]))

# %% ../nbs/06_kernel.ipynb 24
def _handle_stata_error(err, silent, execution_count):
    reply_content = {
        "traceback": [],
        "ename": "Stata error",
        "evalue": str(err),
    }
    if not silent:
        print_stata_error(reply_content['evalue'])
#         self.send_response(
#             self.iopub_socket,
#             "error",
#             reply_content,
#         )
    reply_content.update({
        'status': "error",
        'execution_count': execution_count,
    })
    return reply_content

# %% ../nbs/06_kernel.ipynb 25
@patch_to(PyStataKernel)
def post_do_hook(self):
    self.stata_session.clear_suggestions()

# %% ../nbs/06_kernel.ipynb 26
@patch_to(PyStataKernel)
def do_execute(self, code, silent, store_history=True, user_expressions=None,
               allow_stdin=False):
    """Execute Stata code cell"""
    if not self.stata_ready:
        try:
            self.init_stata()
        except ModuleNotFoundError as err:
            return _handle_stata_import_error(err, silent, self.execution_count)
    self.shell.execution_count += 1
    _ending_delimiter = ending_delimiter(code, self.starting_delimiter)
    code_cell = Cell(self, code, silent)
    try:
        code_cell.run()
    except SystemError as err:
        return _handle_stata_error(err, silent, self.execution_count)
    if _ending_delimiter == ';' and code.strip()[-1] != ';':
        print_red("Warning: Code cell (with #delimit; in effect) does not end in ';'. "
                  "Exported .do script may behave differently from notebook.")
    self.starting_delimiter = _ending_delimiter
    self.post_do_hook()
    return {
        'status': "ok",
        'execution_count': self.execution_count,
        'payload': [],
        'user_expressions': {},
    }

# %% ../nbs/06_kernel.ipynb 27
@patch_to(PyStataKernel)
def do_complete(self, code, cursor_pos):
    """Provide context-aware suggestions"""
    if self.stata_ready:
        cursor_start, cursor_end, matches = self.completions.do(
            code,
            cursor_pos,
            self.starting_delimiter,
        )
        return {
            'status': "ok",
            'cursor_start': cursor_start,
            'cursor_end': cursor_end,
            'metadata': {},
            'matches': matches,
        }
    else:
        return {
            'status': "ok",
            'cursor_start': cursor_pos,
            'cursor_end': cursor_pos,
            'metadata': {},
            'matches': [],
        }

# %% ../nbs/06_kernel.ipynb 28
@patch_to(PyStataKernel)
def do_is_complete(self, code):
    """Overrides IPythonKernel with kernelbase default"""
    return {"status": "unknown"}

# %% ../nbs/06_kernel.ipynb 29
@patch_to(PyStataKernel)
def do_inspect(self, code, cursor_pos, detail_level=0, omit_sections=()):
    """Overrides IPythonKernel with kernelbase default"""
    return {"status": "ok", "data": {}, "metadata": {}, "found": False}

# %% ../nbs/06_kernel.ipynb 30
@patch_to(PyStataKernel)
def do_history(
    self,
    hist_access_type,
    output,
    raw,
    session=None,
    start=None,
    stop=None,
    n=None,
    pattern=None,
    unique=False,
):
    """Overrides IPythonKernel with kernelbase default"""
    return {"status": "ok", "history": []}
