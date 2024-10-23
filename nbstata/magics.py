"""IPython magics for nbstata"""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/09_magics.ipynb.

# %% auto 0
__all__ = ['print_kernel', 'StataMagics', 'Frame']

# %% ../nbs/09_magics.ipynb 3
from .config import Config
from .misc_utils import print_red
from .stata import obs_count, macro_expand, get_global
from .stata_session import warn_re_unclosed_comment_block_if_needed
import nbstata.browse as browse
from fastcore.basics import patch_to
import re
import urllib
from pkg_resources import resource_filename
from bs4 import BeautifulSoup as bs
import configparser

# %% ../nbs/09_magics.ipynb 4
def print_kernel(msg, kernel):
    msg = re.sub(r'$', r'\r\n', msg, flags=re.MULTILINE)
    msg = re.sub(r'[\r\n]{1,2}[\r\n]{1,2}', r'\r\n', msg, flags=re.MULTILINE)
    stream_content = {'text': msg, 'name': 'stdout'}
    kernel.send_response(kernel.iopub_socket, 'stream', stream_content)

# %% ../nbs/09_magics.ipynb 5
def _construct_abbrev_dict():
    def _all_abbrevs(full_command, shortest_abbrev):
        for j in range(len(shortest_abbrev), len(full_command)):
            yield full_command[0:j]
    out = {}
    abbrev_list = [
        ('browse', 'br'),
        ('frbrowse', 'frbr'),
        ('help', 'h'),
        ('quietly', 'q'),
    ]
    for full_command, shortest_abbrev in abbrev_list:
        out.update(
            {abbrev: full_command
             for abbrev in _all_abbrevs(full_command, shortest_abbrev)}
        )
    return out

# %% ../nbs/09_magics.ipynb 7
class StataMagics():
    """Class for handling magics"""
    magic_regex = re.compile(
        r'\A\*?(?P<magic>%%?\w+?)(?P<code>[\s,]+.*?)?\Z', flags=re.DOTALL + re.MULTILINE)

    # Format: magic_name: help_content
    available_magics = {
        '%browse': '{} [-h] [varlist] [if] [in] [, nolabel noformat]',
        '%head': '{} [-h] [N] [varlist] [if] [, nolabel noformat]',
        '%tail': '{} [-h] [N] [varlist] [if] [, nolabel noformat]',
        '%frbrowse': '{} [-h] framename: [varlist] [if] [in] [, nolabel noformat]',
        '%frhead': '{} [-h] framename: [N] [varlist] [if] [, nolabel noformat]',
        '%frtail': '{} [-h] framename: [N] [varlist] [if] [, nolabel noformat]',
        '%locals': '',
        '%delimit': '',
        '%help': '{} [-h] command_or_topic_name',
        '%set': '{} [-h] key = value',
        '%%set': '{} [-h]\nkey1 = value1\n[key2 = value2]\n[...]',
        '%status': '',
        '%%quietly': '',
        '%%noecho': '',
        '%%echo': '',
    }
    
    abbrev_dict = _construct_abbrev_dict()
    
    csshelp_default = resource_filename(
        'nbstata', 'css/_StataKernelHelpDefault.css'
    )

    def magic_quietly(self, code, kernel, cell):
        """Suppress all display for the current cell."""
        cell.quietly = True
        return code

    def magic_noecho(self, code, kernel, cell):
        """Suppress echo for the current cell."""
        cell.noecho = True
        cell.echo = False
        return code
    
    def magic_echo(self, code, kernel, cell):
        """Suppress echo for the current cell."""
        cell.noecho = False
        cell.echo = True
        return code
    
    def magic_delimit(self, code, kernel, cell):
        delim = ';' if kernel.stata_session.sc_delimiter else 'cr'
        print_kernel(f'Current Stata command delimiter: {delim}', kernel)
        return ''
    
    def magic_status(self, code, kernel, cell):
        kernel.nbstata_config.display_status()
        return ''

# %% ../nbs/09_magics.ipynb 8
@patch_to(StataMagics)
def _unabbrev_magic_name(self, raw_name):
    last_percent = raw_name.rfind('%')
    percent_part = raw_name[:last_percent+1]
    raw_name_part = raw_name[last_percent+1:]
    if raw_name_part in self.abbrev_dict:
        name_part = self.abbrev_dict[raw_name_part]
    else:
        name_part = raw_name_part
    return percent_part + name_part

# %% ../nbs/09_magics.ipynb 11
def _parse_magic_name_code(match):
    v = match.groupdict()
    for k in v:
        v[k] = v[k] if v[k] is not None else ''                
    name = v['magic'].strip()
    code = v['code'].strip()
    return name, code

# %% ../nbs/09_magics.ipynb 12
@patch_to(StataMagics)
def _parse_code_for_magic(self, code):
    match = self.magic_regex.match(code.strip())
    if match:
        raw_name, mcode = _parse_magic_name_code(match)
        name = self._unabbrev_magic_name(raw_name)
        if name in {'%quietly', '%noecho', '%echo'}:
            print_red(
                f"Warning: The correct syntax for a cell magic is '%{name}', not '{name}'. "
                "In v1.0, nbstata may trigger an error instead of just a warning."
            )
            name = '%' + name
        elif name == "%set" and len(code.splitlines()) > 1:
            print_red(
                f"Warning: The correct syntax for the multi-line 'set' magic is '%{name}', not '{name}'. "
                "In v1.0, nbstata may trigger an error instead of just a warning."
            )
            name = '%' + name
        elif name == "%%set" and len(code.splitlines()) == 1:
            print_red(
                f"Warning: The correct syntax for the single-line 'set' magic is '%set', not '{name}'. "
                "In v1.0, nbstata may trigger an error instead of just a warning."
            )
            name = '%set'
        elif name not in self.available_magics:
            raise ValueError(f"Unknown magic {name}.")
        return name, mcode
    else:
        return None, code

# %% ../nbs/09_magics.ipynb 19
@patch_to(StataMagics)
def _do_magic(self, name, code, kernel, cell):
    if code.startswith('-h') or code.startswith('--help') or (name == "%help" and (not code or code.isspace())):
        print_kernel(self.available_magics[name].format(name), kernel)
        return ''
    else:
        return getattr(self, "magic_" + name.lstrip('%'))(code, kernel, cell)

# %% ../nbs/09_magics.ipynb 21
@patch_to(StataMagics)
def magic(self, code, kernel, cell):
    try:
        if not kernel.ipydatagrid_height_set:
            browse.set_ipydatagrid_height()
            kernel.ipydatagrid_height_set = True
        name, code = self._parse_code_for_magic(code)
    except ValueError as e:
        print_kernel(str(e), kernel)
    else:
        if name:
            code = self._do_magic(name, code, kernel, cell)
    return code        

# %% ../nbs/09_magics.ipynb 22
def _formatted_local_list(local_dict):
    std_len = 14
    str_reps = []
    for n in local_dict:
        if len(n) <= std_len:
            str_reps.append(f"{n}:{' '*(std_len-len(n))} {local_dict[n]}")
        else:
            str_reps.append(f"{n}:\n{' '*std_len}  {local_dict[n]}")
    return "\n".join(str_reps)

# %% ../nbs/09_magics.ipynb 25
@patch_to(StataMagics)
def magic_locals(self, code, kernel, cell):
    local_dict = kernel.stata_session.get_local_dict()
    print_kernel(_formatted_local_list(local_dict), kernel)
    return ''

# %% ../nbs/09_magics.ipynb 27
def _get_new_settings(code):
    parser = configparser.ConfigParser(
        empty_lines_in_values=False,
        comment_prefixes=('*','//', '/*'), # '/*': to not cause error when commenting out for Stata purposes only
        inline_comment_prefixes=('//',),
    )
    parser.read_string("[set]\n" + code.strip(), source="set")
    return dict(parser.items('set'))

# %% ../nbs/09_magics.ipynb 31
def _clean_error_message(err_str):
    return (err_str
            .replace("While reading from 'set'", "")
            .replace(" in section 'set' already exists", " already set above")
            .replace("Source contains ", "")
            .replace(" 'set'\n", "\n")
           )

# %% ../nbs/09_magics.ipynb 32
def _process_new_settings(settings, kernel):
    kernel.nbstata_config.update(settings)
    kernel.nbstata_config.update_graph_config()

# %% ../nbs/09_magics.ipynb 33
@patch_to(StataMagics)
def magic_set(self, code, kernel, cell):
    try:
        settings = _get_new_settings(code)
    except configparser.Error as err:
        print_red(f"set error:\n    {_clean_error_message(str(err))}")
    else:
        _process_new_settings(settings, kernel)
        warn_re_unclosed_comment_block_if_needed(code)

# %% ../nbs/09_magics.ipynb 38
@patch_to(StataMagics)
def magic_browse(self, code, kernel, cell):
    """Display data interactively."""
    try:
        expanded_code = macro_expand(code)
        params = browse.browse_df_params(
            expanded_code, obs_count(), kernel.nbstata_config.env['missing'],
        )
        sformat = params[-1]
        df = browse.get_df(*params)
        browse.display_df_as_ipydatagrid(df, kernel.nbstata_config.browse_auto_height)
    except Exception as e:
        print_kernel(f"browse failed.\r\n{e}", kernel)
    return ''

# %% ../nbs/09_magics.ipynb 39
class Frame():
    """Class for generating Stata select_var for getAsDict"""
    def __init__(self, framename):
        self.original_framename = get_global('c(frame)')
        self.framename = framename
            
    def __enter__(self):
        import sfi
        try:
            frame = sfi.Frame.connect(self.framename)
        except sfi.FrameError:
            raise ValueError(f"frame {self.framename} not found")
        else:
            frame.changeToCWF()
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        import sfi
        orig_frame = sfi.Frame.connect(self.original_framename)
        orig_frame.changeToCWF()

# %% ../nbs/09_magics.ipynb 40
def _parse_frame_prefix(code):
    pattern = re.compile(
        r'\A(?P<frame>\w+)[ \t]*(?:\:[ \t]*(?P<code>.*?))?\Z', flags=re.DOTALL)
    match = pattern.match(code)
    if not match:
        raise ValueError("invalid syntax: missing framename or colon?")
    v = match.groupdict()
    for k in v:
        v[k] = v[k] if v[k] is not None else ''                
    framename = v['frame'].strip()
    main_code = v['code'].strip()
    return framename, main_code

# %% ../nbs/09_magics.ipynb 42
@patch_to(StataMagics)
def magic_frbrowse(self, code, kernel, cell):
    """Display frame interactively."""
    try:
        framename, main_code = _parse_frame_prefix(code)
        with Frame(framename):
            self.magic_browse(main_code, kernel, cell)
    except Exception as e:
        print_kernel(f"frbrowse failed.\r\n{e}", kernel)
    return ''

# %% ../nbs/09_magics.ipynb 46
def _get_html_data(df):
    html = df.convert_dtypes().to_html(notebook=True)
    return {'text/html': html}

# %% ../nbs/09_magics.ipynb 47
@patch_to(StataMagics)
def _headtail_html(self, df, kernel):
    content = {
        'data': _get_html_data(df),
        'metadata': {},
    }
    kernel.send_response(kernel.iopub_socket, 'display_data', content)

# %% ../nbs/09_magics.ipynb 48
@patch_to(StataMagics)
def _magic_headtail(self, code, kernel, cell, tail=False):
    try:
        expanded_code = macro_expand(code)
        df = browse.headtail_get_df(*browse.headtail_df_params(
            expanded_code, obs_count(), kernel.nbstata_config.env['missing'], tail=tail
        ))
        self._headtail_html(df, kernel)
    except Exception as e:
        print_kernel(f"{'tail' if tail else 'head'} failed.\r\n{e}", kernel)
    return ''

# %% ../nbs/09_magics.ipynb 49
@patch_to(StataMagics)
def magic_head(self, code, kernel, cell):
    """Display data in a nicely-formatted table."""
    return self._magic_headtail(code, kernel, cell, tail=False)

# %% ../nbs/09_magics.ipynb 50
@patch_to(StataMagics)
def magic_frhead(self, code, kernel, cell):
    """Display data in a nicely-formatted table."""
    return self._magic_frheadtail(code, kernel, cell, tail=False)

# %% ../nbs/09_magics.ipynb 51
@patch_to(StataMagics)
def magic_tail(self, code, kernel, cell):
    """Display data in a nicely-formatted table."""
    return self._magic_headtail(code, kernel, cell, tail=True)

# %% ../nbs/09_magics.ipynb 52
@patch_to(StataMagics)
def magic_frtail(self, code, kernel, cell):
    """Display data in a nicely-formatted table."""
    return self._magic_frheadtail(code, kernel, cell, tail=True)

# %% ../nbs/09_magics.ipynb 53
@patch_to(StataMagics)
def _magic_frheadtail(self, code, kernel, cell, tail):
    """Display frame interactively."""
    try:
        framename, main_code = _parse_frame_prefix(code)
        with Frame(framename):
            self._magic_headtail(main_code, kernel, cell, tail)
    except Exception as e:
        print_kernel(f"{'tail' if tail else 'head'} failed.\r\n{e}", kernel)
    return ''

# %% ../nbs/09_magics.ipynb 55
@patch_to(StataMagics)
def _get_help_html(self, code):
    html_base = "https://www.stata.com"
    html_help = urllib.parse.urljoin(html_base, "help.cgi?{}")
    reply = urllib.request.urlopen(html_help.format(code))
    html = reply.read().decode("utf-8")

    # Remove excessive extra lines (Note css: "white-space: pre-wrap")
    edited_html = html.replace("<p>\n", "<p>")
    soup = bs(edited_html, 'html.parser')

    # Set root for links to https://www.stata.com
    for a in soup.find_all('a', href=True):
        href = a.get('href')
        match = re.search(r'{}(.*?)#'.format(code), href)
        if match:
            hrelative = href.find('#')
            a['href'] = href[hrelative:]
        elif not href.startswith('http'):
            link = a['href']
            match = re.search(r'/help.cgi\?(.+)$', link)
            # URL encode bad characters like %
            if match:
                link = '/help.cgi?'
                link += urllib.parse.quote_plus(match.group(1))
            a['href'] = urllib.parse.urljoin(html_base, link)
            a['target'] = '_blank'

    # Remove header 'Stata 15 help for ...'
    stata_header = soup.find('h2')
    if stata_header:
        stata_header.decompose()

    # Remove Stata help menu
    soup.find('div', id='menu').decompose()

    # Remove Copyright notice
    copyright = soup.find(string=re.compile(r".*Copyright.*", flags=re.DOTALL))
    copyright.find_parent("table").decompose()

    # Remove last hrule
    soup.find_all('hr')[-1].decompose()
    
    # Remove last br
    soup.find_all('br')[-1].decompose()
    
    # Remove last empty paragraph, empty space
    empty_paragraphs = soup.find_all('p', string="")
    if str(empty_paragraphs[-1]) == "<p></p>":
        empty_paragraphs[-1].decompose()

    # Set all the backgrounds to transparent
    for color in ['#ffffff', '#FFFFFF']:
        for bg in ['bgcolor', 'background', 'background-color']:
            for tag in soup.find_all(attrs={bg: color}):
                if tag.get(bg):
                    tag[bg] = 'transparent'

    # Set html
    css = soup.find('style', {'type': 'text/css'})
    with open(self.csshelp_default, 'r') as default:
        css.string = default.read()

    return str(soup)

# %% ../nbs/09_magics.ipynb 56
@patch_to(StataMagics)
def magic_help(self, code, kernel, cell):
    """Show help file from stata.com/help.cgi?\{\}"""
    try:
        html_help = self._get_help_html(code)
    except Exception as e: # original: (urllib.error.HTTPError, urllib.error.URLError)
        msg = "Failed to fetch HTML help.\r\n{0}"
        print_kernel(msg.format(e), kernel)
    else:
        fallback = 'This front-end cannot display HTML help.'
        resp = {
            'data': {
                'text/html': html_help,
                'text/plain': fallback},
            'metadata': {}}
        kernel.send_response(kernel.iopub_socket, 'display_data', resp)
    return ''
