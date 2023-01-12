# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/12_cell.ipynb.

# %% auto 0
__all__ = ['Cell']

# %% ../nbs/12_cell.ipynb 3
from .config import launch_stata
from .misc_utils import print_red
from .code_utils import ending_sc_delimiter
from .noecho import dispatch_run
from .stata_session import StataSession
from .magics import StataMagics
from fastcore.basics import patch_to

# %% ../nbs/12_cell.ipynb 4
_final_delimiter_warning = (
    "Warning: Code cell (with #delimit; in effect) does not end in ';'. "
    "Exported .do script may behave differently from notebook. "
    "In v1.0, nbstata may trigger an error instead of just a warning."
)

# %% ../nbs/12_cell.ipynb 5
class Cell:
    """A class for managing execution of a single code cell"""                
    def _set_echo(self, echo_config):
        if echo_config == 'None':
            self.noecho = True
            self.echo = False
        elif echo_config == 'True':
            self.noecho = False
            self.echo = True
        else:
            self.noecho = False
            self.echo = False
    
    def __init__(self, kernel, code_w_magics, silent=False):
        self._set_echo(kernel.env['echo'])
        self.quietly = silent
        self.sc_delimiter = kernel.sc_delimiter
        self.stata_session = kernel.stata_session
        self.code = kernel.magic_handler.magic(code_w_magics, kernel, self)
       
    def run(self):
        if not self.code:
            return
        dispatch_run(self.code, 
            quietly=self.quietly, echo=self.echo, sc_delimiter=self.sc_delimiter,
            noecho=self.noecho, run_as_prog=self.stata_session.run_as_program_w_locals)
        self.sc_delimiter = self._check_ending_delimiter()

    def _check_ending_delimiter(self):
        _ending_sc_delimiter = ending_sc_delimiter(self.code, self.sc_delimiter)
        _final_character = self.code.strip()[-1]
        _code_missing_final_delimiter = (_ending_sc_delimiter
                                         and _final_character != ';')
        if _code_missing_final_delimiter:
            print_red(_final_delimiter_warning)
        return _ending_sc_delimiter
