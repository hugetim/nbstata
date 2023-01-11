# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_stata.ipynb.

# %% auto 0
__all__ = ['run_direct', 'get_local', 'get_global', 'stata_formatted', 'variable_names', 'obs_count', 'resolve_macro',
           'run_as_program', 'run_non_prog_noecho', 'run_prog_noecho']

# %% ../nbs/02_stata.ipynb 4
from .config import launch_stata
from .utils import HiddenPrints

# %% ../nbs/02_stata.ipynb 8
def run_direct(*args, **kwargs):
    import pystata
    return pystata.stata.run(*args, **kwargs)

# %% ../nbs/02_stata.ipynb 10
def get_local(name):
    import sfi
    return sfi.Macro.getLocal(name)

# %% ../nbs/02_stata.ipynb 12
def get_global(name):
    import sfi
    return sfi.Macro.getGlobal(name)

# %% ../nbs/02_stata.ipynb 14
def stata_formatted(value, s_format):
    import sfi
    return sfi.SFIToolkit.formatValue(value, s_format)

# %% ../nbs/02_stata.ipynb 16
def variable_names():
    from sfi import Data
    return [Data.getVarName(i) for i in range(Data.getVarCount())]

# %% ../nbs/02_stata.ipynb 19
def obs_count():
    """Count the number of observations"""
    import sfi
    return sfi.Data.getObsTotal()

# %% ../nbs/02_stata.ipynb 22
def resolve_macro(macro):
    macro = macro.strip()
    if macro.startswith("`") and macro.endswith("'"):
        macro = get_local(macro[1:-1])
    elif macro.startswith("$_"):
        macro = get_local(macro[2:])
    elif macro.startswith("${") and macro.endswith("}"):
        macro = get_global(macro[2:-1])
    elif macro.startswith("$"):
        macro = get_global(macro[1:])
    return macro

# %% ../nbs/02_stata.ipynb 34
def run_as_program(std_non_prog_code, prog_def_option_code=""):
    _program_name = "temp_nbstata_program_name"
    _program_define_code = (
        f"program {_program_name}"
        f"{', ' if prog_def_option_code else ''}{prog_def_option_code}\n"
        f"{std_non_prog_code}\n"
        "end\n"
    )
    try:
        with HiddenPrints():
            run_direct(_program_define_code, quietly=True)
        run_direct(_program_name, quietly=False, inline=True, echo=False)
    finally:
        run_direct(f"program drop {_program_name}", quietly=True)

# %% ../nbs/02_stata.ipynb 43
def run_non_prog_noecho(std_non_prog_code, run_as_prog=run_as_program):
    if len(std_non_prog_code.splitlines()) <= 1:  # to keep it simple when we can
        run_direct(std_non_prog_code, quietly=False, inline=True, echo=False)
    else:
        run_as_prog(std_non_prog_code)

# %% ../nbs/02_stata.ipynb 46
def run_prog_noecho(std_prog_code):
    if std_prog_code.splitlines()[0] in {'mata', 'mata:'}:  # b/c 'quietly' blocks mata output
        run_direct(std_prog_code, quietly=False, inline=True, echo=False)
    else:
        run_direct(std_prog_code, quietly=True, inline=True, echo=False)
