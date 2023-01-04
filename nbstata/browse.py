# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/04_browse.ipynb.

# %% auto 0
__all__ = ['parse_code_if_in_regex', 'parse_code_if_in', 'in_range', 'headtail_df_params', 'get_df', 'parse_browse_magic',
           'browse_df_params', 'perspective_not_found', 'perspective_is_enabled', 'browse_not_enabled',
           'display_perspective']

# %% ../nbs/04_browse.ipynb 3
from .config import launch_stata
from .helpers import *
from .utils import *
from .pandas import better_pdataframe_from_data
from fastcore.basics import patch_to
import re
import numpy as np
import subprocess

# %% ../nbs/04_browse.ipynb 5
parse_code_if_in_regex = re.compile(
    r'\A(?P<code>(?!if\s)(?!\sif)(?!in\s)(?!\sin).+?)?(?P<if>\s*if\s+.+?)?(?P<in>\s*in\s.+?)?\Z',
    flags=re.DOTALL + re.MULTILINE
)

# %% ../nbs/04_browse.ipynb 6
def parse_code_if_in(code):
    """Parse line of Stata code into code, if, in"""
    match = parse_code_if_in_regex.match(code.strip())
    if match:
        args = match.groupdict()
        for k in args:
            args[k] = args[k].strip() if args[k] is not None else ''   
    else:
        args = {'code': code,
                'if': '',
                'in': ''}    
    return args

# %% ../nbs/04_browse.ipynb 11
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

# %% ../nbs/04_browse.ipynb 13
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

# %% ../nbs/04_browse.ipynb 15
def in_range(stata_in_code, count):
    """Return in-statement range"""
    if not stata_in_code.strip():
        return (None, None)
    start, end = (_get_pos_stata_obs_num(in_str, count)
                  for in_str in _get_start_end_strs(stata_in_code))
    if start > end:
        raise ValueError("observations numbers out of range")
    return (start-1, end)

# %% ../nbs/04_browse.ipynb 20
def _split_option_code(code):
    code_parts = code.split(',')
    main_code = code_parts[0] if code_parts else ""
    option_code = code_parts[1] if len(code_parts) > 1 else ""
    return main_code, option_code

# %% ../nbs/04_browse.ipynb 21
def headtail_df_params(code, count, missing_config, tail=False):
    custom_missingval = missing_config != 'pandas'
    missingval = missing_config if custom_missingval else np.NaN

    main_code, option_code = _split_option_code(code)
    oargs = [c.strip() for c in option_code.split() if c]
    sformat = 'noformat' not in oargs
    valuelabel = 'nolabel' not in oargs
    
    vargs = [c.strip() for c in main_code.split() if c]
    N_max = 5
    if len(vargs) >= 1:
        if vargs[0].isnumeric():
            # 1st argument is obs count
            N_max = int(vargs[0])
            del vargs[0]

    # Specified variables?
    varlist = " ".join(vargs)

    # Obs range
    obs_range = None
    if count > N_max:
        obs_range = range(count - N_max, count) if tail else range(0, N_max)

    stata_if_code=""
    return obs_range, varlist, stata_if_code, missingval, valuelabel, sformat

# %% ../nbs/04_browse.ipynb 25
def get_df(obs_range, varlist, stata_if_code, missingval, valuelabel, sformat):
    with Selectvar(stata_if_code) as sel_varname:
        df = better_pdataframe_from_data(obs=obs_range,
                                         varlist=varlist,
                                         selectvar=sel_varname,
                                         missingval=missingval,
                                         valuelabel=valuelabel,
                                         sformat=sformat,
                                        )
        if not varlist and sel_varname is not None:
            df = df.drop([sel_varname], axis=1)
    return df

# %% ../nbs/04_browse.ipynb 29
def parse_browse_magic(code):
    non_option_code, option_code = _split_option_code(code)
    args = parse_code_if_in(non_option_code)
    return args, option_code

# %% ../nbs/04_browse.ipynb 31
def browse_df_params(code, count):
    missingval = np.NaN

    args, option_code = parse_browse_magic(code)
    oargs = [c.strip() for c in option_code.split() if c]
    sformat = 'noformat' not in oargs
    valuelabel = 'nolabel' not in oargs

    vargs = [c.strip() for c in args['code'].split() if c]
    N_max = np.inf
    if len(vargs) >= 1:
        if vargs[0].isnumeric():
            # 1st argument is obs count
            print_red("Warning: '%browse [N]' syntax is deprecated "
                      "and may be removed in v1.0.")
            N_max = int(vargs[0])
            del vargs[0]
    # Specified variables?
    varlist = " ".join(vargs)

    # Obs range
    obs_range = None
    start, end = in_range(args['in'], count)
    if start != None and end != None:
        obs_range = range(start, end)
    elif count > N_max:
        obs_range = range(0, N_max)

    stata_if_code = args['if']
    return obs_range, varlist, stata_if_code, missingval, valuelabel, sformat

# %% ../nbs/04_browse.ipynb 40
def perspective_not_found():
    try:
        import perspective
    except ModuleNotFoundError as e:
        return True
    else:
        return False

# %% ../nbs/04_browse.ipynb 41
def perspective_is_enabled():
    return not perspective_not_found()
#     if perspective_not_found():
#         return False
#     try:
#         output = subprocess.getoutput('jupyter labextension list')
#         enabled = bool(re.search(r'@finos/perspective-jupyterlab v\d\.\d\.\d enabled ok', output))
#         built = not re.search(r'@finos/perspective-jupyterlab needs to be included in build', output)
#         return enabled and built
#     except Exception as e:
#         return False

# %% ../nbs/04_browse.ipynb 43
def browse_not_enabled(kernel):
    content = {
        'data': {'text/markdown': (
            "browse requires perspective widget to be "
            "[installed](https://perspective.finos.org/docs/python/#jupyterlab)"
        )},
        'metadata': {},
    }
    kernel.send_response(kernel.iopub_socket, 'display_data', content)
    return ''

# %% ../nbs/04_browse.ipynb 44
def display_perspective(df, sformat):
    import perspective
    from IPython.display import display
    if sformat:
        # To prevent perspective from wrongly interpreting numbers as dates
        # See: https://perspective.finos.org/docs/table/#schema-and-types
        schema = {'index': int}
        schema.update({name: str for name in list(df.columns)})
        table = perspective.Table(schema)
        table.update(df)
    else:
        table = perspective.Table(df)
    w = perspective.PerspectiveWidget(table)
    display(w)
    
    # Alternate display code, from attempt to customize alt. mime-type(s)
#     data = {'application/vnd.jupyter.widget-view+json': {
#         'version_major': w.get_manager_state()['version_major'],
#         'version_minor': w.get_manager_state()['version_minor'],
#         'model_id': w.model_id,
#     }}
#     content = {
#         'data': data,
#         'metadata': {},
#     }
#     kernel.send_response(kernel.iopub_socket, 'display_data', content) 
