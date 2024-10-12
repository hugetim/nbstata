"""For running multi-line Stata code without echoing the commands"""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/05_noecho.ipynb.

# %% auto 0
__all__ = ['parse_sreturn', 'run_as_program_w_locals', 'run_non_prog_noecho', 'run_prog_noecho', 'run_noecho']

# %% ../nbs/05_noecho.ipynb 4
from .code_utils import break_out_prog_blocks, valid_single_line_code, local_def_in, preserve_restore_in
from .stata import run_direct, set_local, run_single, get_global
from . import stata_more as sm 
from textwrap import dedent
import re

# %% ../nbs/05_noecho.ipynb 7
def _run_as_program_w_locals_sreturned(std_code):
    sreturn_code = dedent("""\
        
        mata : st_local("temp_nbstata_all_locals", invtokens(st_dir("local", "macro", "*")'))
        foreach lname in `temp_nbstata_all_locals' {
            sreturn local `lname' "``lname''"
        }
        """)
    store_new_locals_code = ("sreturn clear\n" 
                             + std_code
                             + sreturn_code)                          
    sm.run_as_program(store_new_locals_code, "sclass")

# %% ../nbs/05_noecho.ipynb 11
parse_sreturn = re.compile(
    r'^\s*?(?:\ss\((?P<name>\w+)\) : )', flags=re.MULTILINE
).findall

# %% ../nbs/05_noecho.ipynb 13
def _local_names_from_sreturn(sreturn_output):
    matches = parse_sreturn(sreturn_output)
    return matches

# %% ../nbs/05_noecho.ipynb 15
def _after_local_dict():
    sreturn_output = sm.diverted_stata_output_quicker("sreturn list")
    _local_names = _local_names_from_sreturn(sreturn_output)
    return {name: get_global(f"s({name})") for name in _local_names}

# %% ../nbs/05_noecho.ipynb 20
def _restore_locals_and_clear_sreturn():
    for lname, value in _after_local_dict().items():
        set_local(lname, value)
    run_single("sreturn clear")

# %% ../nbs/05_noecho.ipynb 22
def run_as_program_w_locals(std_code, local_dict=None):
    if local_dict is None:
        local_dict = sm.get_local_dict()
    locals_code = sm.locals_code_from_dict(local_dict)
    if not local_def_in(std_code):
        sm.run_as_program(f"""{locals_code}\n{std_code}""")
    else:
        _run_as_program_w_locals_sreturned(f"""{locals_code}\n{std_code}""")
        _restore_locals_and_clear_sreturn()

# %% ../nbs/05_noecho.ipynb 25
def run_non_prog_noecho(std_non_prog_code, run_as_prog=run_as_program_w_locals):
    if len(std_non_prog_code.splitlines()) <= 1:  # to keep it simple when we can
        run_direct(valid_single_line_code(std_non_prog_code),
                   quietly=False, inline=True, echo=False)
    elif preserve_restore_in(std_non_prog_code):
        print("(Note: Below code run with echo to enable preserve/restore functionality.)")
        run_direct(std_non_prog_code,
                   quietly=False, inline=True, echo=False)
    else:
        run_as_prog(std_non_prog_code)

# %% ../nbs/05_noecho.ipynb 32
def run_prog_noecho(std_prog_code):
    if std_prog_code.splitlines()[0] in {'mata', 'mata:'}:  # b/c 'quietly' blocks mata output
        run_direct(std_prog_code, quietly=False, inline=True, echo=False)
    else:
        run_direct(std_prog_code, quietly=True, inline=True, echo=False)

# %% ../nbs/05_noecho.ipynb 38
def run_noecho(code, sc_delimiter=False, run_as_prog=run_as_program_w_locals):
    """After `break_out_prog_blocks`, run each prog and non-prog block noecho"""
    for block in break_out_prog_blocks(code, sc_delimiter):
        if block['is_prog']:
            run_prog_noecho(block['std_code'])
        else:
            run_non_prog_noecho(block['std_code'], run_as_prog=run_as_prog)
