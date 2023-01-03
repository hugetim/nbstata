# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_helpers.ipynb.

# %% auto 0
__all__ = ['count', 'resolve_macro', 'Selectvar', 'run_as_program', 'run_non_prog_noecho', 'run_prog_noecho', 'run_noecho',
           'diverted_stata_output', 'simple_dataframe_from_stata', 'better_dataframe_from_stata',
           'better_pdataframe_from_data', 'better_pdataframe_from_frame']

# %% ../nbs/02_helpers.ipynb 4
from .config import launch_stata
from .utils import break_out_prog_blocks, HiddenPrints
import sys
from io import StringIO
from textwrap import dedent
import pandas as pd
import numpy as np

# %% ../nbs/02_helpers.ipynb 6
def count():
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
    elif macro.startswith("$"):
        macro = sfi.Macro.getGlobal(macro[1:])
    return macro

# %% ../nbs/02_helpers.ipynb 10
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
            
    def __enter__(self):
        return self.varname
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        self.clear()

# %% ../nbs/02_helpers.ipynb 26
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

# %% ../nbs/02_helpers.ipynb 32
def run_non_prog_noecho(std_non_prog_code, run_as_prog=run_as_program):
    from pystata.stata import run
    if len(std_non_prog_code.splitlines()) == 1:  # to keep it simple when we can
        run(std_non_prog_code, quietly=False, inline=True, echo=False)
    else:
        run_as_prog(std_non_prog_code)

# %% ../nbs/02_helpers.ipynb 34
def run_prog_noecho(std_prog_code):
    from pystata.stata import run
    if std_prog_code.splitlines()[0] in {'mata', 'mata:'}:  # b/c 'quietly' blocks mata output
        run(std_prog_code, quietly=False, inline=True, echo=False)
    else:
        run(std_prog_code, quietly=True, inline=True, echo=False)

# %% ../nbs/02_helpers.ipynb 40
def run_noecho(code, starting_delimiter=None, run_as_prog=run_as_program):
    """After `break_out_prog_blocks`, run each prog and non-prog block noecho"""
    for block in break_out_prog_blocks(code, starting_delimiter):
        if block['is_prog']:
            run_prog_noecho(block['std_code'])
        else:
            run_non_prog_noecho(block['std_code'], run_as_prog=run_as_prog)

# %% ../nbs/02_helpers.ipynb 43
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

# %% ../nbs/02_helpers.ipynb 50
def simple_dataframe_from_stata(stfr, var, valuelabel, missingval):
    from pystata import stata
    if stfr is None:
        df = stata.pdataframe_from_data(var=var, valuelabel=valuelabel, missingval=missingval)
    else:
        df = stata.pdataframe_from_frame(stfr, var=var, valuelabel=valuelabel, missingval=missingval)
    df.index += 1
    return df

# %% ../nbs/02_helpers.ipynb 51
def _better_dataframe(hdl, var, obs, selectvar, valuelabel, missingval):
    import sfi, pystata
    pystata.stata.run("""tempvar indexvar
                         generate `indexvar' = _n""", quietly=True)
    idx_var = sfi.Macro.getLocal('indexvar')

    data = hdl.getAsDict(var, obs, selectvar, valuelabel, missingval)

    if idx_var in data:
        idx = data.pop(idx_var)
    else:
        idx = hdl.getAsDict(idx_var, obs, selectvar, valuelabel, missingval).pop(idx_var)
    idx = pd.array(idx, dtype='int64')
    sfi.Data.dropVar(idx_var)

    return pd.DataFrame(data=data, index=idx)

# %% ../nbs/02_helpers.ipynb 52
def better_dataframe_from_stata(stfr, var, obs, selectvar, valuelabel, missingval, sformat):
    import sfi, pystata
    hdl = sfi.Data if stfr is None else sfi.Frame.connect(stfr)

    custom_index_not_needed = obs is None and not selectvar
    if custom_index_not_needed:
        df = simple_dataframe_from_stata(stfr, var, valuelabel, missingval)
    else:
        if hdl.getObsTotal() <= 0:
            return pd.DataFrame()
        df = _better_dataframe(hdl, var, obs, selectvar, valuelabel, missingval)
        
    if sformat:
        for var in list(df.columns):
            if hdl.isVarTypeString(var) or (valuelabel and pd.api.types.is_string_dtype(df[var])):
                continue
            v_format = hdl.getVarFormat(var)
            if missingval != np.NaN:
                df[var] = df[var].apply(lambda x: sfi.SFIToolkit.formatValue(x, v_format) if type(x)!=str else x)
            else:
                df[var] = df[var].apply(lambda x: sfi.SFIToolkit.formatValue(x, v_format))
    return df

# %% ../nbs/02_helpers.ipynb 53
def better_pdataframe_from_data(var=None, obs=None, selectvar=None, valuelabel=False, missingval=np.NaN, sformat=False):
    import pystata
    pystata.config.check_initialized()

    return better_dataframe_from_stata(None, var, obs, selectvar, valuelabel, missingval, sformat)

# %% ../nbs/02_helpers.ipynb 54
def better_pdataframe_from_frame(stfr, var=None, obs=None, selectvar=None, valuelabel=False, missingval=np.NaN, sformat=False):
    import pystata
    pystata.config.check_initialized()

    return better_dataframe_from_stata(stfr, var, obs, selectvar, valuelabel, missingval, sformat)
