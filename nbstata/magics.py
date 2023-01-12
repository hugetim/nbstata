# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/09_magics.ipynb.

# %% auto 0
__all__ = ['print_kernel', 'StataMagics']

# %% ../nbs/09_magics.ipynb 3
import nbstata.browse as browse
from fastcore.basics import patch_to
import re
import urllib
from pkg_resources import resource_filename
from bs4 import BeautifulSoup as bs

# %% ../nbs/09_magics.ipynb 4
def print_kernel(msg, kernel):
    msg = re.sub(r'$', r'\r\n', msg, flags=re.MULTILINE)
    msg = re.sub(r'[\r\n]{1,2}[\r\n]{1,2}', r'\r\n', msg, flags=re.MULTILINE)
    stream_content = {'text': msg, 'name': 'stdout'}
    kernel.send_response(kernel.iopub_socket, 'stream', stream_content)

# %% ../nbs/09_magics.ipynb 6
class StataMagics():
    """Class for handling magics"""
    html_base = "https://www.stata.com"
    html_help = urllib.parse.urljoin(html_base, "help.cgi?{}")

    magic_regex = re.compile(
        r'\A(%|\*%)(?P<magic>\w+?)(?P<code>[\s,]+.*?)?\Z', flags=re.DOTALL + re.MULTILINE)

    # Format: magic_name: help_content
    available_magics = {
        'browse': '{} [-h] [varlist] [if] [in] [, nolabel noformat]',
        'head': '{} [-h] [N] [varlist] [if] [, nolabel noformat]',
        'tail': '{} [-h] [N] [varlist] [if] [, nolabel noformat]',
        'locals': '',
        'delimit': '',
        'help': '{} [-h] command_or_topic_name',
        'quietly': '',
        'noecho': '',
        'echo': '',
    }
    
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
        delim = ';' if kernel.sc_delimiter else 'cr'
        print_kernel(f'The delimiter is currently: {delim}', kernel)
        return ''

# %% ../nbs/09_magics.ipynb 7
def _parse_magic_name_code(match):
    v = match.groupdict()
    for k in v:
        v[k] = v[k] if v[k] is not None else ''                
    name = v['magic'].strip()
    code = v['code'].strip()
    return name, code

# %% ../nbs/09_magics.ipynb 8
@patch_to(StataMagics)
def _parse_code_for_magic(self, code):
    match = self.magic_regex.match(code.strip())
    if match:
        name, code = _parse_magic_name_code(match)
        if name not in self.available_magics:
            raise ValueError(f"Unknown magic %{name}.")
        return name, code
    else:
        return None, code

# %% ../nbs/09_magics.ipynb 13
@patch_to(StataMagics)
def _do_magic(self, name, code, kernel, cell):
    if code.startswith('-h') or code.startswith('--help'):
        print_kernel(self.available_magics[name].format(name), kernel)
        return ''
    else:
        return getattr(self, "magic_" + name)(code, kernel, cell)

# %% ../nbs/09_magics.ipynb 14
@patch_to(StataMagics)
def magic(self, code, kernel, cell):
    try:
        name, code = self._parse_code_for_magic(code)
    except ValueError as e:
        print_kernel(str(e), kernel)
    else:
        if name:
            code = self._do_magic(name, code, kernel, cell)
    return code        

# %% ../nbs/09_magics.ipynb 15
def _formatted_local_list(local_dict):
    std_len = 14
    str_reps = []
    for n in local_dict:
        if len(n) <= std_len:
            str_reps.append(f"{n}:{' '*(std_len-len(n))} {local_dict[n]}")
        else:
            str_reps.append(f"{n}:\n{' '*std_len}  {local_dict[n]}")
    return "\n".join(str_reps)

# %% ../nbs/09_magics.ipynb 18
@patch_to(StataMagics)
def magic_locals(self, code, kernel, cell):
    local_dict = kernel.stata_session.get_local_dict()
    print_kernel(_formatted_local_list(local_dict), kernel)
    return ''

# %% ../nbs/09_magics.ipynb 20
@patch_to(StataMagics)
def magic_browse(self, code, kernel, cell):
    """Display data interactively."""
    if kernel.perspective_enabled is None:
        kernel.perspective_enabled = browse.perspective_is_enabled()
    if not kernel.perspective_enabled:
        return browse.browse_not_enabled(kernel)
    try:
        params = browse.browse_df_params(code, obs_count())
        sformat = params[-1]
        df = browse.get_df(*params)
        browse.display_perspective(df, sformat)
    except Exception as e:
        print_kernel(f"Browse failed.\r\n{e}", kernel)
    return ''

# %% ../nbs/09_magics.ipynb 23
def _get_html_data(df):
    html = df.convert_dtypes().to_html(notebook=True)
    return {'text/html': html}

# %% ../nbs/09_magics.ipynb 24
@patch_to(StataMagics)
def _headtail_html(self, df, kernel):
    content = {
        'data': _get_html_data(df),
        'metadata': {},
    }
    kernel.send_response(kernel.iopub_socket, 'display_data', content)

# %% ../nbs/09_magics.ipynb 25
@patch_to(StataMagics)
def _magic_headtail(self, code, kernel, cell, tail=False):
    try:
        df = browse.get_df(*browse.headtail_df_params(
            code, obs_count(), kernel.env['missing'], tail=tail
        ))
        self._headtail_html(df, kernel)
    except Exception as e:
        print_kernel(f"{'Tail' if tail else 'Head'} failed.\r\n{e}", kernel)
    return ''

# %% ../nbs/09_magics.ipynb 26
@patch_to(StataMagics)
def magic_head(self, code, kernel, cell):
    """Display data in a nicely-formatted table."""
    return self._magic_headtail(code, kernel, cell, tail=False)

# %% ../nbs/09_magics.ipynb 27
@patch_to(StataMagics)
def magic_tail(self, code, kernel, cell):
    """Display data in a nicely-formatted table."""
    return self._magic_headtail(code, kernel, cell, tail=True)

# %% ../nbs/09_magics.ipynb 29
@patch_to(StataMagics)
def magic_help(self,code,kernel,cell):
    """Show help file from stata.com."""
    try:
        reply = urllib.request.urlopen(self.html_help.format(code))
        html = reply.read().decode("utf-8")
        soup = bs(html, 'html.parser')

        # Set root for links to https://ww.stata.com
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
                a['href'] = urllib.parse.urljoin(self.html_base, link)
                a['target'] = '_blank'

        # Remove header 'Stata 15 help for ...'
        soup.find('h2').decompose()

        # Remove Stata help menu
        soup.find('div', id='menu').decompose()

        # Remove Copyright notice
        tags = ['a', 'font']
        for tag in tags:
            copyright = soup.find(tag, text='Copyright')
            if copyright:
                copyright.find_parent("table").decompose()
                break

        # Remove last hrule
        soup.find_all('hr')[-1].decompose()

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

        fallback = 'This front-end cannot display HTML help.'
        resp = {
            'data': {
                'text/html': str(soup),
                'text/plain': fallback},
            'metadata': {}}
        kernel.send_response(kernel.iopub_socket, 'display_data', resp)
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        msg = "Failed to fetch HTML help.\r\n{0}"
        print_kernel(msg.format(e), kernel)

    return ''
