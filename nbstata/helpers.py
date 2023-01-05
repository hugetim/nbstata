# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_helpers.ipynb.

# %% auto 0
__all__ = ['obs_count', 'resolve_macro', 'Selectvar', 'IndexVar', 'run_as_program', 'run_non_prog_noecho', 'run_prog_noecho',
           'run_noecho', 'diverted_stata_output']

# %% ../nbs/02_helpers.ipynb 4
from .config import launch_stata
from .utils import break_out_prog_blocks, HiddenPrints
import sys
from io import StringIO
from textwrap import dedent

# %% ../nbs/02_helpers.ipynb 6
def obs_count():
    """Count the number of observations"""
    import sfi
    return sfi.Data.getObsTotal()

# %% ../nbs/02_helpers.ipynb 8
def resolve_macro(macro):
    import sfi
    macro = macro.strip()
    if macro.startswith("`") and macro.endswith("'"):
        macro = sfi.Macro.getLocal(macro[1:-1])
    elif macro.startswith("$_"):
        macro = sfi.Macro.getLocal(macro[2:])
    elif macro.startswith("${") and macro.endswith("}"):
        macro = sfi.Macro.getGlobal(macro[2:-1])
    elif macro.startswith("$"):
        macro = sfi.Macro.getGlobal(macro[1:])
    return macro

# %% ../nbs/02_helpers.ipynb 11
class Selectvar():
    """Class for generating Stata selectvar for getAsDict"""
    varname = None
    
    def __init__(self, stata_if_code):
        import sfi, pystata
        condition = stata_if_code.replace('if ', '', 1).strip()
        if condition:
            cmd = dedent(f"""\
                tempvar __selectionVar
                generate `__selectionVar' = cond({condition},1,0)""")
            pystata.stata.run(cmd, quietly=True)      
            self.varname = sfi.Macro.getLocal("__selectionVar")  

    def clear(self):
        """Remove temporary selectvar from Stata dataset"""
        import sfi
        if self.varname:
            sfi.Data.dropVar(self.varname)
            sfi.Macro.setLocal("__selectionVar", "")
            
    def __enter__(self):
        return self.varname
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        self.clear()

# %% ../nbs/02_helpers.ipynb 16
class IndexVar:
    def __enter__(self):
        import sfi, pystata
        pystata.stata.run("""tempvar indexvar
                             generate `indexvar' = _n""", quietly=True)
        self.idx_var = sfi.Macro.getLocal('indexvar')
        return self.idx_var
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        import sfi
        sfi.Data.dropVar(self.idx_var)
        sfi.Macro.setLocal('indexvar', "")

# %% ../nbs/02_helpers.ipynb 27
def run_as_program(std_non_prog_code):
    from pystata.stata import run
    _program_name = "temp_nbstata_program_name"
    _program_define_code = f"program {_program_name}\n{std_non_prog_code}\nend\n"
    with HiddenPrints():
        run(_program_define_code, quietly=True)
    try:
        run(_program_name, quietly=False, inline=True, echo=False)
    finally:
        run(f"program drop {_program_name}", quietly=True)

# %% ../nbs/02_helpers.ipynb 33
def run_non_prog_noecho(std_non_prog_code, run_as_prog=run_as_program):
    from pystata.stata import run
    if len(std_non_prog_code.splitlines()) == 1:  # to keep it simple when we can
        run(std_non_prog_code, quietly=False, inline=True, echo=False)
    else:
        run_as_prog(std_non_prog_code)

# %% ../nbs/02_helpers.ipynb 35
def run_prog_noecho(std_prog_code):
    from pystata.stata import run
    if std_prog_code.splitlines()[0] in {'mata', 'mata:'}:  # b/c 'quietly' blocks mata output
        run(std_prog_code, quietly=False, inline=True, echo=False)
    else:
        run(std_prog_code, quietly=True, inline=True, echo=False)

# %% ../nbs/02_helpers.ipynb 41
def run_noecho(code, starting_delimiter=None, run_as_prog=run_as_program):
    """After `break_out_prog_blocks`, run each prog and non-prog block noecho"""
    for block in break_out_prog_blocks(code, starting_delimiter):
        if block['is_prog']:
            run_prog_noecho(block['std_code'])
        else:
            run_non_prog_noecho(block['std_code'], run_as_prog=run_as_prog)

# %% ../nbs/02_helpers.ipynb 44
def diverted_stata_output(std_code, noecho=True):
    import pystata
    old_stdout = sys.stdout
    diverted = StringIO()
    sys.stdout = diverted
    if noecho:
        code = f"capture log off\n{std_code}\ncapture log on"""
        run_noecho(code) # multi-line code run as a program, which clears locals
    else:
        pystata.stata.run("capture log off", quietly=True)
        code = f"{std_code}\ncapture log on"""
        pystata.stata.run(code, quietly=False, inline=True, echo=False)
    sys.stdout = old_stdout
    out = diverted.getvalue()
    return out #.replace("\n> ", "")
