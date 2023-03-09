# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/07_browse.ipynb.

# %% auto 0
__all__ = ['matchparts', 'in_range', 'parse_browse_magic', 'get_df', 'headtail_df_params', 'headtail_get_df', 'browse_df_params',
           'display_df_as_ipydatagrid']

# %% ../nbs/07_browse.ipynb 3
from .misc_utils import print_red
from .stata import run_single
from .stata_more import SelectVar, run_direct_cleaned, diverted_stata_output_quicker, run_sfi
from .pandas import better_pdataframe_from_data
from fastcore.basics import patch_to
import re

# %% ../nbs/07_browse.ipynb 6
def _get_start_end_strs(stata_in_code):
    stata_range_code = stata_in_code.replace('in ','').strip()
    slash_pos = stata_range_code.find('/')
    if slash_pos != -1:
        start_str = stata_range_code[:slash_pos]
        end_str = stata_range_code[slash_pos+1:]
    else:
        start_str = "1"
        end_str = stata_range_code
    return start_str, end_str

# %% ../nbs/07_browse.ipynb 8
def _get_pos_stata_obs_num(in_obs_str, count):
    temp_str = in_obs_str.strip().upper()
    if temp_str == 'F': 
        in_obs = 1
    elif temp_str == 'L':
        in_obs = count
    else:
        try:
            in_obs = int(in_obs_str)
        except ValueError as e:
            raise ValueError(f"{in_obs_str} invalid observation number")
        if in_obs < 0: in_obs += count + 1
        if in_obs < 1 or in_obs > count:
            raise ValueError(f"{in_obs_str} invalid observation number")
    return in_obs

# %% ../nbs/07_browse.ipynb 10
def in_range(stata_in_code, count):
    """Return in-statement range"""
    if not stata_in_code.strip():
        return (None, None)
    start, end = (_get_pos_stata_obs_num(in_str, count)
                  for in_str in _get_start_end_strs(stata_in_code))
    if start > end:
        raise ValueError("observations numbers out of range")
    return (start-1, end)

# %% ../nbs/07_browse.ipynb 15
def _parse_browse_magic_syntax(code):
    _program_name = "temp_nbstata_syntax_name"
    run_direct_cleaned((
        f"program define {_program_name}\n"
        """ syntax [varlist(default=none)] [if] [in] [, noLabels noFormat]
            disp "%varlist%"
            foreach var in `varlist' {
                disp "`var'"
            }
            disp "%if%"
            disp `"`if'"'
            disp "%in%"
            disp `"`in'"'
            disp "%nolabels%"
            disp "`labels'"
            disp "%noformat%"
            disp "`format'"
            disp "%end%"
        end
        """), quietly=True)
    try:
        output = diverted_stata_output_quicker(f"""\
            {_program_name} {code}
            program drop {_program_name}
            """).strip()
    except Exception as e:
        run_single(f"capture program drop {_program_name}", show_exc_warning=True)
        raise(e)
    return output.replace("\n> ", "") #[c.strip() for c in var_code.split() if c] if var_code else None

# %% ../nbs/07_browse.ipynb 20
matchparts = re.compile(
            r"\A.*?"
            r"^%varlist%(?P<varlist>.*?)"
            r"%if%(?P<if>.*?)"
            r"%in%(?P<in>.*?)"
            r"%nolabels%(?P<nolabels>.*?)"
            r"%noformat%(?P<noformat>.*?)%end%", #"(\Z|---+\s*end)",
            flags=re.DOTALL + re.MULTILINE).match

# %% ../nbs/07_browse.ipynb 22
def parse_browse_magic(code):
    N = None
    m = re.match(r"\A(?P<N>[0-9]+)?[\s]*(?P<remainder>.*?)\Z", code.strip())
    if m is None:
        raise ValueError(f"syntax error: this magic must be in a code by itself on a single line")
    if m.group('N'):
        N = int(m.group('N'))
    code_minus_N = m.group('remainder')
    args = matchparts(_parse_browse_magic_syntax(code_minus_N)).groupdict()
    _var = [c.strip() for c in args['varlist'].split() if c]
    var = _var if _var else None
    if_code = args['if'].strip()
    in_code = args['in'].strip()
    nolabels = args['nolabels'].strip()
    noformat = args['noformat'].strip()
    return N, var, if_code, in_code, nolabels, noformat

# %% ../nbs/07_browse.ipynb 26
def _parse_df_params(code, count, browse=False, tail=False):
    import numpy as np
    N, var, if_code, in_code, nolabels, noformat = parse_browse_magic(code)
    sformat = not noformat
    valuelabel = not nolabels

    N_max = np.inf if browse else 5
    if N is not None:
        if browse:
            print_red("Warning: '%browse [N]' syntax is deprecated "
                      "and may be removed in v1.0.")
        N_max = N

    # Obs range
    obs_range = None
    if browse:
        start, end = in_range(in_code, count)
        if start != None and end != None:
            obs_range = range(start, end)
        elif count > N_max:
            obs_range = range(0, N_max)
    else:
        if in_code:
            print_red(f"Note: [in] not allowed for {'tail' if tail else 'head'} "
                      "magic and is ignored."
                     )
        if count > N_max:
            obs_range = range(count - N_max, count) if tail else range(0, N_max)

    return obs_range, var, if_code, valuelabel, sformat

# %% ../nbs/07_browse.ipynb 27
def get_df(obs_range, var, stata_if_code, missingval, valuelabel, sformat):
    with SelectVar(stata_if_code) as sel_varname:
        df = better_pdataframe_from_data(obs=obs_range,
                                         var=var,
                                         selectvar=sel_varname,
                                         missingval=missingval,
                                         valuelabel=valuelabel,
                                         sformat=sformat,
                                        )
        if not var and sel_varname is not None and sel_varname in df:
            df = df.drop([sel_varname], axis=1)
    return df

# %% ../nbs/07_browse.ipynb 29
def headtail_df_params(code, count, missing_config, tail=False):
    import numpy as np
    custom_missingval = missing_config != 'pandas'
    missingval = missing_config if custom_missingval else np.NaN
    obs_range, var, stata_if_code, valuelabel, sformat = (
        _parse_df_params(code, count, tail=tail)
    )
    return obs_range, var, stata_if_code, missingval, valuelabel, sformat

# %% ../nbs/07_browse.ipynb 33
def headtail_get_df(obs_range, var, stata_if_code, missingval, valuelabel, sformat):
    if not stata_if_code:
        return get_df(obs_range, var, stata_if_code, missingval, valuelabel, sformat)
    N_max = len(obs_range)
    tail = obs_range[0] != 0
    with SelectVar(stata_if_code) as sel_varname:
        df = better_pdataframe_from_data(obs=None,
                                         var=var,
                                         selectvar=sel_varname,
                                         missingval=missingval,
                                         valuelabel=valuelabel,
                                         sformat=sformat,
                                        )
        if not var and sel_varname is not None and sel_varname in df:
            df = df.drop([sel_varname], axis=1)
    return df.tail(N_max) if tail else df.head(N_max)

# %% ../nbs/07_browse.ipynb 44
def browse_df_params(code, count, missing_config):
    import numpy as np
    custom_missingval = missing_config != 'pandas'
    missingval = missing_config if custom_missingval else np.NaN
    obs_range, var, stata_if_code, valuelabel, sformat = (
        _parse_df_params(code, count, browse=True)
    )
    return obs_range, var, stata_if_code, missingval, valuelabel, sformat

# %% ../nbs/07_browse.ipynb 52
def display_df_as_ipydatagrid(df):
    from ipydatagrid import DataGrid, TextRenderer
    i_renderer = TextRenderer(horizontal_alignment="right", font="11px monospace", background_color="rgb(243, 243, 243)")
    d_renderer = TextRenderer(horizontal_alignment="right", font="11px monospace")
    h_renderer = TextRenderer(horizontal_alignment="center", font="11px monospace")
    column_widths = {}
    temp_head = df.head(23)
    char_px_width = 6.05
    for name in list(df):
        column_widths[name] = max(
            43+char_px_width*min(15.3, len(name)),
            20+char_px_width*max((len(str(value)) for value in temp_head[name])),
        )
    column_widths[""] = 20+char_px_width*len(str(max(df.index.values)))
    g = DataGrid(df,
                 index_name="",
                 editable=False,
                 selection_mode='cell',
                 base_row_size=21,
                 auto_fit_columns=False,
                 default_renderer=d_renderer,
                 header_renderer=h_renderer,
                 renderers={"": i_renderer},
                 column_widths=column_widths,
                )
    g.grid_style = {
        "background_color": "rgb(255, 255, 255)",
        "header_background_color": "rgb(243, 243, 243)",
        "header_grid_line_color": "rgb(229, 229, 229)",
        "vertical_grid_line_color": "rgb(229, 229, 229)",
        "horizontal_grid_line_color": "rgb(229, 229, 229)",
        "selection_fill_color": "rgb(59, 135, 195, .25)", # 206, 225, 240
        "selection_border_color": "rgb(229, 229, 229)",
        "header_selection_fill_color": "rgb(99, 99, 99, .25)", #216
        "header_selection_border_color": "rgb(229, 229, 229)",
        "cursor_fill_color": "rgb(255, 255, 255, 0)",
        "cursor_border_color": "rgb(40, 40, 40)",
        "scroll_shadow": {'size': 0},
    }
    display(g)
