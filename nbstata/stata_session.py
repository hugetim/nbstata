# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/06_stata_session.ipynb.

# %% auto 0
__all__ = ['StataSession']

# %% ../nbs/06_stata_session.ipynb 4
from .utils import HiddenPrints
from .stata import run_direct, get_local, run_as_program, variable_names
from .helpers import diverted_stata_output, local_names
from .helpers import get_local_dict as _get_local_dict, run_as_program_w_locals as _run_as_program_w_locals
from fastcore.basics import patch_to
from textwrap import dedent
import re

# %% ../nbs/06_stata_session.ipynb 6
class StataSession():
    def __init__(self):
        """"""
        self.matchall = re.compile(
            r"\A.*?"
            r"^%varlist%(?P<varlist>.*?)"
            r"%globals%(?P<globals>.*?)"
            r"%locals%(?P<locals>.*?)"
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

        self.clear_suggestions()
#         self.suggestions = self.get_suggestions(kernel)
#         self.suggestions['magics'] = kernel.magics.available_magics
#         self.suggestions['magics_set'] = config.all_settings

    def clear_suggestions(self):
        self.suggestions = None

# %% ../nbs/06_stata_session.ipynb 7
@patch_to(StataSession)
def refresh_suggestions(self):
    self.suggestions = self.get_suggestions()
#     self.suggestions['magics_set'] = config.all_settings
#     self.globals = self.get_globals(kernel)

# %% ../nbs/06_stata_session.ipynb 9
@patch_to(StataSession)
def _completions(self):
#     return dedent(f"""\
#     %varlist%
#     {' '.join(variable_names())}
#     %globals%
#     {' '.join(global_names())}
#     """
    return diverted_stata_output(dedent("""\
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
        disp "%locals%"
        mata : invtokens(st_dir("local", "macro", "*")')
        disp "%scalars%"
        disp `"`:all scalars'"'
        disp "%matrices%"
        disp `"`:all matrices'"'
        disp "%end%"
        local _temp_completions_while_local_ = 0
        }
        macro drop _temp_completions_while_local_
    """))

# %% ../nbs/06_stata_session.ipynb 14
@patch_to(StataSession)
def get_suggestions(self):
    match = self.matchall(self._completions())
    suggestions = match.groupdict()
#         suggestions['mata'] = self._parse_mata_desc(suggestions['mata'])
#         suggestions['programs'] = self._parse_programs_desc(
#             suggestions['programs'])
    for k, v in suggestions.items():
#             if k in ['mata', 'programs']:
#                 continue
#             elif k in ['logfiles']:
#                 suggestions[k] = [
#                     f for f in self.filelist.split(v.strip()) if f]
#             else:
        suggestions[k] = self.varlist.findall(self.varclean('', v))
    #suggestions['locals'] = self.get_locals()
    return suggestions

# %% ../nbs/06_stata_session.ipynb 16
@patch_to(StataSession)
def _get_locals(self):
    return self.suggestions['locals'] if self.suggestions else local_names()

# %% ../nbs/06_stata_session.ipynb 20
@patch_to(StataSession)
def get_local_dict(self):
    return _get_local_dict(self._get_locals())

# %% ../nbs/06_stata_session.ipynb 23
@patch_to(StataSession)
def run_as_program_w_locals(self, std_code):
    """After `break_out_prog_blocks`, run noecho, inserting locals when needed"""
    return _run_as_program_w_locals(std_code, local_dict=self.get_local_dict())
