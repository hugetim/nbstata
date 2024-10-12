"""Helper functions that expand on `pystata`/`sfi` functionality"""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/03_stata_more.ipynb.

# %% auto 0
__all__ = ['run_direct_cleaned', 'run_sfi', 'SelectVar', 'IndexVar', 'run_as_program', 'diverted_stata_output',
           'diverted_stata_output_quicker', 'var_from_varlist', 'local_names', 'get_local_dict',
           'locals_code_from_dict', 'user_expression']

# %% ../nbs/03_stata_more.ipynb 4
from .misc_utils import print_red
from .stata import run_direct, run_single, get_local, set_local, drop_var, stata_formatted
from textwrap import dedent
import functools
from contextlib import redirect_stdout
from io import StringIO
import re

# %% ../nbs/03_stata_more.ipynb 8
def run_direct_cleaned(cmds, quietly=False, echo=False, inline=True):
    if quietly:
        with redirect_stdout(StringIO()) as diverted: # to prevent blank line output, as with `program define`
            out = run_direct(cmds, quietly, echo, inline)
            prints = diverted.getvalue()
        for line in prints.splitlines():
            if line.strip():
                print(line)
        return out
    elif len(cmds.splitlines()) > 1:
        with redirect_stdout(StringIO()) as diverted:
            run_direct(cmds, quietly, echo, inline)
            output_lines = diverted.getvalue().splitlines()
        if (len(output_lines) >= 2 
            and not output_lines[0].strip() 
            and "\n".join(output_lines[-2:]).strip() == "."):
            print("\n".join(output_lines[1:-2]))
        else:
            print("\n".join(output_lines))
    else:
        return run_direct(cmds, quietly, echo, inline)

# %% ../nbs/03_stata_more.ipynb 30
def run_sfi(std_code, echo=False, show_exc_warning=True):
    import sfi
    cmds = std_code.splitlines()
    for i, cmd in enumerate(cmds):
        try:
            sfi.SFIToolkit.stata(cmd, echo)
        except Exception as e:
            if show_exc_warning:
                print_red(f"run_sfi (sfi.SFIToolkit.stata) error: {repr(e)}")
            remaining_code = "\n".join(cmds[i:])
            run_direct(remaining_code, echo=echo)
            break

# %% ../nbs/03_stata_more.ipynb 35
class SelectVar():
    """Class for generating Stata select_var for getAsDict"""
    varname = None
    
    def __init__(self, stata_if_code):
        import sfi
        condition = stata_if_code.replace('if ', '', 1).strip()
        if condition:
            self.varname = sfi.SFIToolkit.getTempName()
            cmd = f"quietly gen {self.varname} = cond({condition},1,0)"
            run_single(cmd)

    def clear(self):
        """Remove temporary select_var from Stata dataset"""
        if self.varname:
            drop_var(self.varname)
            
    def __enter__(self):
        return self.varname
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        self.clear()

# %% ../nbs/03_stata_more.ipynb 38
class IndexVar:
    """Class for generating Stata index var for use with pandas"""
    def __enter__(self):
        import sfi
        self.idx_var = sfi.SFIToolkit.getTempName()
        run_single(f"gen {self.idx_var} = _n")
        return self.idx_var
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        drop_var(self.idx_var)

# %% ../nbs/03_stata_more.ipynb 51
def run_as_program(std_non_prog_code, prog_def_option_code=""):
    _program_name = "temp_nbstata_program_name"
    _options = f", {prog_def_option_code}" if prog_def_option_code else ""
    _program_define_code = (
        f"program {_program_name}{_options}\n"
        f"{std_non_prog_code}\n"
        "end\n"
    )
    try:
        run_direct_cleaned(_program_define_code, quietly=True)
        run_direct(_program_name, quietly=False, inline=True, echo=False)
    finally:
        run_single(f"capture program drop {_program_name}")

# %% ../nbs/03_stata_more.ipynb 65
def diverted_stata_output(std_code, runner=None):
    if runner is None:
        runner = functools.partial(run_direct, quietly=False, inline=True, echo=False)
    with redirect_stdout(StringIO()) as diverted:
        run_as_program("return add\ncapture log off", prog_def_option_code="rclass")
        try:
            runner(std_code)
        finally:
            run_as_program("return add\ncapture log on", prog_def_option_code="rclass")
        out = diverted.getvalue()
    return out

# %% ../nbs/03_stata_more.ipynb 71
def diverted_stata_output_quicker(std_non_prog_code):
    with redirect_stdout(StringIO()) as diverted:
        code = f"return add\ncapture log off\n{std_non_prog_code}\ncapture log on"""
        try:
            run_as_program(code, prog_def_option_code="rclass")
        except SystemError as e:
            run_as_program("return add\ncapture log on", prog_def_option_code="rclass")
            raise(e)
        out = diverted.getvalue()
    return out

# %% ../nbs/03_stata_more.ipynb 76
def var_from_varlist(varlist, stfr=None):
    if stfr:
        var_code = varlist.strip()
    else:
        _program_name = "temp_nbstata_varlist_name"
        run_direct_cleaned((
            f"program define {_program_name}\n"
            """ syntax [varlist(default=none)]
                foreach var in `varlist' {
                    disp "`var'"
                }
            end
            """), quietly=True)
        try:
            var_code = diverted_stata_output_quicker(f"""\
                {_program_name} {varlist}
                program drop {_program_name}
                """).strip()
        except Exception as e:
            run_sfi(f"capture program drop {_program_name}")
            raise(e)
    return [c.strip() for c in var_code.split() if c] if var_code else None

# %% ../nbs/03_stata_more.ipynb 86
def local_names():
    run_single("""\
        mata : st_local("temp_nbstata_all_locals", invtokens(st_dir("local", "macro", "*")'))""")
    out = get_local('temp_nbstata_all_locals')
    set_local('temp_nbstata_all_locals', "")
    return out.split()

# %% ../nbs/03_stata_more.ipynb 90
def get_local_dict(_local_names=None):
    if _local_names is None:
        _local_names = local_names()
    return {n: get_local(n) for n in _local_names}

# %% ../nbs/03_stata_more.ipynb 92
def locals_code_from_dict(preexisting_local_dict):
    local_defs = (f"""local {name} `"{preexisting_local_dict[name]}"'"""
                  for name in preexisting_local_dict)
    return "\n".join(local_defs)

# %% ../nbs/03_stata_more.ipynb 98
def user_expression(input_str):
    run_single("tempname output")
    try:
        run_single(f"local `output': display {input_str}")
    except SyntaxError as e:
        combined_message = f"{str(e)}\nInvalid Stata '[%fmt] [=]exp' display expression: {input_str}"
        raise SyntaxError(combined_message)
    return get_local(get_local("output"))
