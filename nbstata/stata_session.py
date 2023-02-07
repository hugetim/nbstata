# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/08_stata_session.ipynb.

# %% auto 0
__all__ = ['StataSession']

# %% ../nbs/08_stata_session.ipynb 4
from .misc_utils import print_red
from .stata import run_direct
from .stata_more import diverted_stata_output_quicker, local_names, run_sfi
from .stata_more import get_local_dict as _get_local_dict
from .code_utils import remove_comments, ending_sc_delimiter
from .noecho import run_as_program_w_locals, run_noecho
from fastcore.basics import patch_to
from textwrap import dedent
import re

# %% ../nbs/08_stata_session.ipynb 5
class StataSession():
    def __init__(self):
        """"""
        self.sc_delimiter = False
        self.clear_suggestions()
        self._compile_re()

    def clear_suggestions(self):
        self.suggestions = None
        
    def _compile_re(self):
        self.matchall = re.compile(
            r"\A.*?"
            r"^%varlist%(?P<varlist>.*?)"
            r"%globals%(?P<globals>.*?)"
            #r"%locals%(?P<locals>.*?)"
            r"%scalars%(?P<scalars>.*?)"
            r"%matrices%(?P<matrices>.*?)%end%", #"(\Z|---+\s*end)",
            flags=re.DOTALL + re.MULTILINE).match

        # Varlist-style matching; applies to most
        self.varlist = re.compile(r"(?:\s+)(\S+)", flags=re.MULTILINE)

        # file-style matching
        self.filelist = re.compile(r"[\r\n]{1,2}", flags=re.MULTILINE)

        # Clean line-breaks.
        self.varclean = re.compile(
            r"(?=\s*)[\r\n]{1,2}?^>\s", flags=re.MULTILINE).sub
        
        #         # Match output from mata mata desc
#         self.matadesc = re.compile(
#             r"(\A.*?---+|---+[\r\n]*\Z)", flags=re.MULTILINE + re.DOTALL)

#         self.matalist = re.compile(
#             r"(?:.*?)\s(\S+)\s*$", flags=re.MULTILINE + re.DOTALL)

#         self.mataclean = re.compile(r"\W.*?(\b|$)")
#         self.matasearch = re.compile(r"(?P<kw>\w.*?(?=\W|\b|$))").search

# %% ../nbs/08_stata_session.ipynb 6
@patch_to(StataSession)
def refresh_suggestions(self):
    self.suggestions = self.get_suggestions()

# %% ../nbs/08_stata_session.ipynb 8
@patch_to(StataSession)
def _completions(self):
    return diverted_stata_output_quicker(dedent("""\
        local _temp_completions_while_local_ = 1
        while `_temp_completions_while_local_' {
        set more off
        set trace off
        if `"`varlist'"' != "" {
        local _temp_completions_varlist_loc_ `"`varlist'"'
        }
        syntax [varlist]
        disp "%varlist%"
        disp `"`varlist'"'
        macro drop _varlist __temp_completions_while_local_
        if `"`_temp_completions_varlist_loc_'"' != "" {
        local varlist `"`_temp_completions_varlist_loc_'"'
        macro drop __temp_completions_varlist_loc_
        }
        disp "%globals%"
        disp `"`:all globals'"'
        *disp "%locals%"
        *mata : invtokens(st_dir("local", "macro", "*")')
        disp "%scalars%"
        disp `"`:all scalars'"'
        disp "%matrices%"
        disp `"`:all matrices'"'
        disp "%end%"
        local _temp_completions_while_local_ = 0
        }
        macro drop _temp_completions_while_local_
    """))

# %% ../nbs/08_stata_session.ipynb 11
@patch_to(StataSession)
def _get_locals(self):
    return self.suggestions['locals'] if self.suggestions else local_names()

# %% ../nbs/08_stata_session.ipynb 15
@patch_to(StataSession)
def get_suggestions(self):
    match = self.matchall(self._completions())
    suggestions = match.groupdict()
#         suggestions['mata'] = self._parse_mata_desc(suggestions['mata'])
#         suggestions['programs'] = self._parse_programs_desc(
#             suggestions['programs'])
    for k, v in suggestions.items():
        suggestions[k] = self.varlist.findall(self.varclean('', v))
    suggestions['locals'] = self._get_locals()
    return suggestions

# %% ../nbs/08_stata_session.ipynb 19
@patch_to(StataSession)
def get_local_dict(self):
    return _get_local_dict(self._get_locals())

# %% ../nbs/08_stata_session.ipynb 21
@patch_to(StataSession)
def _run_as_program_w_locals(self, std_code):
    """After `break_out_prog_blocks`, run noecho, inserting locals when needed"""
    return run_as_program_w_locals(std_code, local_dict=self.get_local_dict())

# %% ../nbs/08_stata_session.ipynb 26
def _run_simple(code, quietly=False, echo=False, sc_delimiter=False):
    if sc_delimiter:
        code = "#delimit;\n" + code
    if len(code.splitlines()) == 1:
        code = remove_comments(code)
    run_direct(code, quietly=quietly, inline=not quietly, echo=echo)

# %% ../nbs/08_stata_session.ipynb 29
_final_delimiter_warning = (
    "Warning: Code cell (with #delimit; in effect) does not end in ';'. "
    "Exported .do script may behave differently from notebook. "
    "In v1.0, nbstata may trigger an error instead of just a warning."
)

# %% ../nbs/08_stata_session.ipynb 30
@patch_to(StataSession)    
def _update_ending_delimiter(self, code):
    self.sc_delimiter = ending_sc_delimiter(code, self.sc_delimiter)
    _final_character = code.strip()[-1]
    _code_missing_final_delimiter = (self.sc_delimiter
                                     and _final_character != ';')
    if _code_missing_final_delimiter:
        print_red(_final_delimiter_warning)

# %% ../nbs/08_stata_session.ipynb 32
@patch_to(StataSession)
def _post_run_hook(self, code):
    self.clear_suggestions()
    self._update_ending_delimiter(code)

# %% ../nbs/08_stata_session.ipynb 33
@patch_to(StataSession)
def dispatch_run(self, code, quietly=False, echo=False, noecho=False):
    if noecho and not quietly:
        run_noecho(code, self.sc_delimiter, run_as_prog=self._run_as_program_w_locals)
    else:
        _run_simple(code, quietly, echo, self.sc_delimiter)
    self._post_run_hook(code)
