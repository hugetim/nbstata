# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/14_kernel.ipynb.

# %% auto 0
__all__ = ['PyStataKernel', 'print_stata_error']

# %% ../nbs/14_kernel.ipynb 4
from .config import Config
from .misc_utils import print_red
from .inspect import get_inspect
from .stata_session import StataSession
from .completions import CompletionsManager
from .cell import Cell
import nbstata # for __version__
from fastcore.basics import patch_to
from ipykernel.ipkernel import IPythonKernel

# %% ../nbs/14_kernel.ipynb 6
class PyStataKernel(IPythonKernel):
    """A jupyter kernel based on pystata"""
    implementation = 'nbstata'
    implementation_version = nbstata.__version__
    language_info = {
        'name': 'stata',
        'version': '17',
        'mimetype': 'text/x-stata',
        'file_extension': '.do',
    }
    banner = "nbstata: a Jupyter kernel for Stata based on pystata"
    help_links = [
        {
            "text": "Stata Documentation",
            "url": "https://www.stata.com/features/documentation/",
        },
        {
            "text": "nbstata Help",
            "url": "https://hugetim.github.io/nbstata/",
        },
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stata_ready = False
        self.shell.execution_count = 0
        self.perspective_enabled = None
        self.inspect_output = "Stata not yet initialized."
        try:
            self.init_session()
        except ModuleNotFoundError as err:
            pass # wait for first do_execute so error message can be displayed under cell

# %% ../nbs/14_kernel.ipynb 7
@patch_to(PyStataKernel)
def init_session(self):
    self.nbstata_config = Config()
    self.stata_session = StataSession()
    self.stata_session.init_stata(self.nbstata_config)
    self.completions = CompletionsManager(self.stata_session)
    self.inspect_output = ""
    self.stata_ready = True

# %% ../nbs/14_kernel.ipynb 8
_missing_stata_message = (
    "pystata path not found\n"
    "A Stata 17 installation is required to use the nbstata Stata kernel. "
    "If you already have Stata 17 installed, "
    "please specify its path in your configuration file."
)

# %% ../nbs/14_kernel.ipynb 10
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

# %% ../nbs/14_kernel.ipynb 13
def print_stata_error(text):
    lines = text.splitlines()
    if len(lines) >= 2 and lines[-2] == lines[-1]:
        lines.pop(-1) # remove duplicate error code glitch in pystata.stata.run multi-line (ex. below)
    if len(lines) > 2:
        print("\n".join(lines[:-2]))
    print_red("\n".join(lines[-2:]))

# %% ../nbs/14_kernel.ipynb 19
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

# %% ../nbs/14_kernel.ipynb 20
@patch_to(PyStataKernel)
def post_do_hook(self):
    self.inspect_output = ""

# %% ../nbs/14_kernel.ipynb 21
@patch_to(PyStataKernel)
def do_execute(self, code, silent,
               store_history=True, user_expressions=None, allow_stdin=False):
    """Execute Stata code cell"""
    if not self.stata_ready:
        try:
            self.init_session()
        except ModuleNotFoundError as err:
            return _handle_stata_import_error(err, silent, self.execution_count)
    self.shell.execution_count += 1
    code_cell = Cell(self, code, silent)
    try:
        code_cell.run()
    except SystemError as err:
        return _handle_stata_error(err, silent, self.execution_count)
    self.post_do_hook()
    return {
        'status': "ok",
        'execution_count': self.execution_count,
        'payload': [],
        'user_expressions': {},
    }

# %% ../nbs/14_kernel.ipynb 22
@patch_to(PyStataKernel)
def do_complete(self, code, cursor_pos):
    """Provide context-aware suggestions"""
    if self.stata_ready:
        cursor_start, cursor_end, matches = self.completions.do(
            code,
            cursor_pos,
        )
    else:
        cursor_start = cursor_end = cursor_pos
        matches = []
    return {
        'status': "ok",
        'cursor_start': cursor_start,
        'cursor_end': cursor_end,
        'metadata': {},
        'matches': matches,
    }

# %% ../nbs/14_kernel.ipynb 23
@patch_to(PyStataKernel)
def do_is_complete(self, code):
    """Overrides IPythonKernel with kernelbase default"""
    return {"status": "unknown"}

# %% ../nbs/14_kernel.ipynb 24
@patch_to(PyStataKernel)
def do_inspect(self, code, cursor_pos, detail_level=0, omit_sections=()):
    """Display Stata 'describe' output regardless of cursor position"""
    if not self.inspect_output:
        self.inspect_output = get_inspect(code, cursor_pos, detail_level, omit_sections)
    data = {'text/plain': self.inspect_output}
    return {"status": "ok", "data": data, "metadata": {}, "found": True}

# %% ../nbs/14_kernel.ipynb 25
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
