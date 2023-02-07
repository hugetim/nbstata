# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/12_inspect.ipynb.

# %% auto 0
__all__ = ['get_inspect']

# %% ../nbs/12_inspect.ipynb 3
from .stata_more import run_as_program, run_sfi, diverted_stata_output
import functools

# %% ../nbs/12_inspect.ipynb 6
def get_inspect(code="", cursor_pos=0, detail_level=0, omit_sections=()):
    runner = functools.partial(run_as_program, prog_def_option_code="rclass")
    inspect_code = """
        disp _newline "*** Stored results:"
        return list
        ereturn list
        return add
        display "*** Last updated `c(current_time)' `c(current_date)' ***"
        describe, fullnames
        """
    raw_output = diverted_stata_output(inspect_code, runner=runner)
    desc_start = raw_output.find('*** Last updated ')
    out = raw_output[desc_start:]
    if desc_start > 21:
        out += raw_output[:desc_start]
    return out