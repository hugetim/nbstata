# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/05_noecho.ipynb.

# %% auto 0
__all__ = ['parse_sreturn', 'pre', 'kwargs', 'local_def_in', 'run_as_program_w_locals', 'run_non_prog_noecho', 'run_prog_noecho',
           'run_noecho', 'run_simple', 'dispatch_run']

# %% ../nbs/05_noecho.ipynb 3
from .code_utils import break_out_prog_blocks
from .stata import run_direct
from . import stata_more as sm 
from textwrap import dedent
import re

# %% ../nbs/05_noecho.ipynb 10
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

# %% ../nbs/05_noecho.ipynb 13
parse_sreturn = re.compile(
    r'^\s*?(?:\ss\((?P<name>\w+)\) : \"(?P<value>.+)\"\s)', flags=re.MULTILINE
).findall

# %% ../nbs/05_noecho.ipynb 15
def _local_dict_from_sreturn(sreturn_output):
    matches = parse_sreturn(sreturn_output)
    return {m[0]: m[1] for m in matches}

# %% ../nbs/05_noecho.ipynb 18
def _after_local_dict():
    sreturn_output = sm.diverted_stata_output_quicker("sreturn list")
    return _local_dict_from_sreturn(sreturn_output)

# %% ../nbs/05_noecho.ipynb 19
def _restore_locals_and_clear_sreturn():
    # run non-prog to avoid clearing locals
    after_local_dict = _after_local_dict()
    after_locals_code = sm.locals_code_from_dict(after_local_dict)
    if after_local_dict:
        after_locals_code += "\n" + "sreturn clear"
    run_direct(after_locals_code, quietly=True)

# %% ../nbs/05_noecho.ipynb 20
pre = (
    r'(cap(t|tu|tur|ture)?'
    r'|qui(e|et|etl|etly)?'
    r'|n(o|oi|ois|oisi|oisil|oisily)?)')
kwargs = {'flags': re.MULTILINE}
local_def_in = re.compile(
    r"(^({0} )*(loc(a|al)?|tempname|tempvar|tempfile|gettoken|token(i|iz|ize)?)\s)|st_local\(".format(pre),
    **kwargs,
).search

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

# %% ../nbs/05_noecho.ipynb 26
def run_non_prog_noecho(std_non_prog_code, run_as_prog=run_as_program_w_locals):
    if len(std_non_prog_code.splitlines()) <= 1:  # to keep it simple when we can
        run_direct(std_non_prog_code, quietly=False, inline=True, echo=False)
    else:
        run_as_prog(std_non_prog_code)

# %% ../nbs/05_noecho.ipynb 29
def run_prog_noecho(std_prog_code):
    if std_prog_code.splitlines()[0] in {'mata', 'mata:'}:  # b/c 'quietly' blocks mata output
        run_direct(std_prog_code, quietly=False, inline=True, echo=False)
    else:
        run_direct(std_prog_code, quietly=True, inline=True, echo=False)

# %% ../nbs/05_noecho.ipynb 35
def run_noecho(code, sc_delimiter=False, run_as_prog=run_as_program_w_locals):
    """After `break_out_prog_blocks`, run each prog and non-prog block noecho"""
    for block in break_out_prog_blocks(code, sc_delimiter):
        if block['is_prog']:
            run_prog_noecho(block['std_code'])
        else:
            run_non_prog_noecho(block['std_code'], run_as_prog=run_as_prog)

# %% ../nbs/05_noecho.ipynb 39
def run_simple(code, quietly=False, echo=False, sc_delimiter=False):
    if sc_delimiter:
        code = "#delimit;\n" + code
    run_direct(code, quietly=quietly, inline=not quietly, echo=echo)

# %% ../nbs/05_noecho.ipynb 41
def dispatch_run(code, quietly=False, echo=False, sc_delimiter=False, noecho=False, run_as_prog=run_as_program_w_locals):
    if noecho and not quietly:
        run_noecho(code, sc_delimiter, run_as_prog=run_as_prog)
    else:
        run_simple(code, quietly, echo, sc_delimiter)   
