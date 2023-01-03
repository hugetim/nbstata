# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/04_magics.ipynb.

# %% auto 0
__all__ = ['print_kernel', 'perspective_is_enabled', 'StataMagics']

# %% ../nbs/04_magics.ipynb 3
from .config import get_config
from .helpers import *
from .utils import *
import re
import urllib
from pkg_resources import resource_filename
import numpy as np
from bs4 import BeautifulSoup as bs
import subprocess

# %% ../nbs/04_magics.ipynb 4
def print_kernel(msg, kernel):
    msg = re.sub(r'$', r'\r\n', msg, flags=re.MULTILINE)
    msg = re.sub(r'[\r\n]{1,2}[\r\n]{1,2}', r'\r\n', msg, flags=re.MULTILINE)
    stream_content = {'text': msg, 'name': 'stdout'}
    kernel.send_response(kernel.iopub_socket, 'stream', stream_content)

# %% ../nbs/04_magics.ipynb 5
def perspective_is_enabled():
    try:
        output = subprocess.getoutput('jupyter labextension list')
        return bool(re.search(r'@finos/perspective-jupyterlab v\d\.\d\.\d enabled ok', output))
    except Exception as e:
        return False

# %% ../nbs/04_magics.ipynb 6
class StataMagics():
    """Class for handling magics"""
    html_base = "https://www.stata.com"
    html_help = urllib.parse.urljoin(html_base, "help.cgi?{}")

    magic_regex = re.compile(
        r'\A(%|\*%)(?P<magic>.+?)(?P<code>[\s,]+(.|\s)+?)?\Z', flags=re.DOTALL + re.MULTILINE)

    # This is the original regex that splits into magic code if in
    #magic_regex = re.compile(
    #    r'\A(%|\*%)(?P<magic>.+?)(?P<code>\s+(?!if\s)(?!\sif)(?!in\s)(?!\sin).+?)?(?P<if>\s+if\s+.+?)?(?P<in>\s+in\s+.+?)?\Z', flags=re.DOTALL + re.MULTILINE)
    
    # Format: magic_name: help_content
    available_magics = {
        'browse': '{} [-h] [N] [varlist] [if] [in] [, format]',
        'help': '{} [-h] command_or_topic_name',
        'quietly': '',
        'noecho': '',
        'echo': '',
    }
    
    csshelp_default = resource_filename(
        'nbstata', 'css/_StataKernelHelpDefault.css'
    )

    def magic(self, code, kernel, cell):
        match = self.magic_regex.match(code.strip())
        if match:
            v = match.groupdict()
            for k in v:
                v[k] = v[k] if isinstance(v[k],str) else ''                

            name = v['magic'].strip()
            code = v['code'].strip()

            if name in self.available_magics:
                if code.find('-h') >= 0:
                    print_kernel(self.available_magics[name].format(name), kernel)
                    code = ''
                else:
                    code = getattr(self, "magic_" + name)(code, kernel, cell)
            else:
                print_kernel("Unknown magic %{0}.".format(name), kernel)
    
        return code        

    def magic_quietly(self, code, kernel, cell):
        """
        Supress all display for the current cell.
        """
        cell.quietly = True
        return code

    def magic_noecho(self, code, kernel, cell):
        """
        Supress echo for the current cell.
        """
        cell.noecho = True
        cell.echo = False
        return code
    
    def magic_echo(self, code, kernel, cell):
        """
        Supress echo for the current cell.
        """
        cell.noecho = False
        cell.echo = True
        return code

    def _browse_df_params(self, code, kernel, N_max=200):
        missing_config = kernel.env['missing']
        custom_missingval = missing_config != 'pandas' and not kernel.perspective_enabled
        missingval = missing_config if custom_missingval else np.NaN
        
        args, option_code = parse_browse_magic(code)
        oargs = [c.strip() for c in option_code.split() if c]
        sformat = 'noformat' not in oargs
        valuelabel = 'nolabel' not in oargs
        
        vargs = [c.strip() for c in args['code'].split() if c]
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
        start, end = in_range(args['in'])
        if start != None and end != None:
            obs_range = range(start, end)
        elif count() > N_max and not kernel.perspective_enabled:
            obs_range = range(0, min(count(), N_max))
            
        stata_if_code = args['if']
        return obs_range, varlist, stata_if_code, missingval, valuelabel, sformat
    
    def _browse_display_perspective(self, df, sformat):
        import perspective
        from IPython.display import display
        if sformat:
            # To prevent perspective from wrongly interpreting numbers as dates
            # See: https://perspective.finos.org/docs/table/#schema-and-types
            schema = {name: str for name in list(df.columns)}
            table = perspective.Table(schema)
            table.update(df)
        else:
            table = perspective.Table(df)
        display(perspective.PerspectiveWidget(table))

    def _browse_html(self, df, kernel):
        html = df.convert_dtypes().to_html(notebook=True)
        content = {
            'data': {'text/html': html},
            'metadata': {},
        }
        kernel.send_response(kernel.iopub_socket, 'display_data', content)
        
    def magic_browse(self, code, kernel, cell):
        """Display data in a nicely-formatted table."""
        if kernel.perspective_enabled is None:
            kernel.perspective_enabled = perspective_is_enabled()
        try:
            obs_range, varlist, stata_if_code, missingval, valuelabel, sformat = (
                self._browse_df_params(code, kernel, N_max=200)
            )
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

            if kernel.perspective_enabled:
                self._browse_display_perspective(df, sformat)
            else:
                self._browse_html(df, kernel)
        except Exception as e:
            print_kernel(f"Failed to browse data.\r\n{e}", kernel)
        return ''

    def magic_help(self,code,kernel,cell):
        """
        Show help file from stata.com.
        """

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
