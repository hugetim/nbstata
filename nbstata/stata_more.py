# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/03_stata_more.ipynb.

# %% auto 0
__all__ = ['SelectVar', 'IndexVar', 'run_as_program', 'diverted_stata_output', 'diverted_stata_output_quicker',
           'var_from_varlist', 'local_names', 'get_local_dict', 'locals_code_from_dict', 'get_inspect']

# %% ../nbs/03_stata_more.ipynb 3
from .misc_utils import DivertedPrints
from .stata import run_direct, get_local, set_local, drop_var
from textwrap import dedent
import functools

# %% ../nbs/03_stata_more.ipynb 6
class SelectVar():
    """Class for generating Stata select_var for getAsDict"""
    varname = None
    
    def __init__(self, stata_if_code):
        condition = stata_if_code.replace('if ', '', 1).strip()
        if condition:
            cmd = dedent(f"""\
                tempvar __selectionVar
                generate `__selectionVar' = cond({condition},1,0)""")
            run_direct(cmd, quietly=True)      
            self.varname = get_local("__selectionVar")  

    def clear(self):
        """Remove temporary select_var from Stata dataset"""
        if self.varname:
            drop_var(self.varname)
            set_local("__selectionVar", "")
            
    def __enter__(self):
        return self.varname
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        self.clear()

# %% ../nbs/03_stata_more.ipynb 10
class IndexVar:
    def __enter__(self):
        run_direct("""\
            tempvar indexvar
            generate `indexvar' = _n""", quietly=True)
        self.idx_var = get_local('indexvar')
        return self.idx_var
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        drop_var(self.idx_var)
        set_local('indexvar', "")

# %% ../nbs/03_stata_more.ipynb 21
def run_as_program(std_non_prog_code, prog_def_option_code=""):
    _program_name = "temp_nbstata_program_name"
    _options = f", {prog_def_option_code}" if prog_def_option_code else ""
    _program_define_code = (
        f"program {_program_name}{_options}\n"
        f"{std_non_prog_code}\n"
        "end\n"
    )
    try:
        run_direct(_program_define_code, quietly=True)
        run_direct(_program_name, quietly=False, inline=True, echo=False)
    finally:
        run_direct(f"program drop {_program_name}", quietly=True)

# %% ../nbs/03_stata_more.ipynb 33
def diverted_stata_output(std_code, runner=None):
    if runner is None:
        runner = functools.partial(run_direct, quietly=False, inline=True, echo=False)
    with DivertedPrints() as diverted:
        run_as_program("return add\ncapture log off", prog_def_option_code="rclass")
        try:
            runner(std_code)
        finally:
            run_as_program("return add\ncapture log on", prog_def_option_code="rclass")
        out = diverted.getvalue()
    return out

# %% ../nbs/03_stata_more.ipynb 39
def diverted_stata_output_quicker(std_non_prog_code):
    with DivertedPrints() as diverted:
        code = f"return add\ncapture log off\n{std_non_prog_code}\ncapture log on"""
        try:
            run_as_program(code, prog_def_option_code="rclass")
        except SystemError as e:
            run_as_rclass_prog("return add\ncapture log on")
            raise(e)
        out = diverted.getvalue()
    return out

# %% ../nbs/03_stata_more.ipynb 46
def var_from_varlist(varlist, stfr=None):
    if stfr:
        var_code = varlist.strip()
    else:
        _program_name = "temp_nbstata_varlist_name"
        run_direct(f"""\
            program define {_program_name}
                syntax [varlist(default=none)]
                disp "`varlist'"
            end
            """, quietly=True)
        try:
            var_code = diverted_stata_output_quicker(f"""\
                {_program_name} {varlist}
                program drop {_program_name}
                """).strip()
        except Exception as e:
            run_direct(f"capture program drop {_program_name}", quietly=True)
            raise(e)
    return [c.strip() for c in var_code.split() if c] if var_code else None

# %% ../nbs/03_stata_more.ipynb 53
def local_names():
    run_direct("""\
        mata : st_local("temp_nbstata_all_locals", invtokens(st_dir("local", "macro", "*")'))
        """, quietly=True)
    out = get_local('temp_nbstata_all_locals')
    set_local('temp_nbstata_all_locals', "")
    return out.split()

# %% ../nbs/03_stata_more.ipynb 57
def get_local_dict(_local_names=None):
    if _local_names is None:
        _local_names = local_names()
    return {n: get_local(n) for n in _local_names}

# %% ../nbs/03_stata_more.ipynb 59
def locals_code_from_dict(preexisting_local_dict):
    local_defs = (f"""local {name} `"{preexisting_local_dict[name]}"'"""
                  for name in preexisting_local_dict)
    return "\n".join(local_defs)

# %% ../nbs/03_stata_more.ipynb 64
def get_inspect(code="", cursor_pos=0, detail_level=0, omit_sections=()):
    runner = functools.partial(run_as_program, prog_def_option_code="rclass")
    inspect_code = """\
        return list
        ereturn list
        return add
        display "*** Last updated `c(current_time)' `c(current_date)' ***"
        describe, fullnames
        """
    raw_output = diverted_stata_output(inspect_code, runner=runner)
    desc_start = raw_output.find('*** Last updated ')
    return raw_output[desc_start:] + raw_output[:desc_start]