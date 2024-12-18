"""Utilities for loading Stata and nbstata"""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/01_config.ipynb.

# %% auto 0
__all__ = ['find_dir_edition', 'find_edition', 'set_pystata_path', 'launch_stata', 'set_graph_format', 'xdg_user_config_path',
           'old_user_config_path', 'Config']

# %% ../nbs/01_config.ipynb 5
from .misc_utils import print_red
from fastcore.basics import patch_to
import os
import sys
import platform
from shutil import which
from pathlib import Path
from packaging import version
import configparser

# %% ../nbs/01_config.ipynb 8
def _win_find_path(_dir=None):
    if _dir is None:
        dirs = [r'C:\Program Files\Stata19',
                r'C:\Program Files\Stata18',
                r'C:\Program Files\Stata17']
    else:
        dirs = [_dir]
    for this_dir in dirs:
        path = Path(this_dir)
        if os.path.exists(path):
            executables = [exe for exe in path.glob("Stata*.exe") if exe not in set(path.glob("Stata*_old.exe"))]
            if executables:
                return str(executables[0])
    # Otherwise, try old way
    import winreg
    reg = winreg.ConnectRegistry(None, winreg.HKEY_CLASSES_ROOT)
    subkey = r'Stata17Do\shell\do\command'
    try:
        key = winreg.OpenKey(reg, subkey)
        return winreg.QueryValue(key, None).split('"')[1]
    except FileNotFoundError:
        return ''

# %% ../nbs/01_config.ipynb 10
def _mac_find_path(_dir=None):
    """
    Attempt to find Stata path on macOS when not on user's PATH.
    Modified from stata_kernel's original to only location "Applications/Stata". 

    Returns:
        (str): Path to Stata. Empty string if not found.
    """
    if _dir is None:
        _dir = '/Applications/Stata'
    path = Path(_dir)
    if not os.path.exists(path):
        return ''
    else:
        try:
            # find the application with the suffix .app
            # example path: /Applications/Stata/StataMP.app
            return str(next(path.glob("Stata*.app")))
        except StopIteration:
            return ''

# %% ../nbs/01_config.ipynb 12
def _other_find_path():
    for i in ['stata-mp', 'stata-se', 'stata']:
        stata_path = which(i)
        if stata_path:
            return stata_path
    return ''

# %% ../nbs/01_config.ipynb 14
def _find_path(_dir=None):
    if os.getenv('CONTINUOUS_INTEGRATION'):
        print('WARNING: Running as CI; Stata path not set correctly')
        return 'stata'
    path = ''
    if platform.system() == 'Windows':
        path = _win_find_path(_dir)
    elif platform.system() == 'Darwin':
        path = _mac_find_path(_dir)
    return path if path else _other_find_path()

# %% ../nbs/01_config.ipynb 16
def _edition(stata_exe):
    edition = 'be'
    for e in ('be', 'se', 'mp'):
        if stata_exe.find(e) > -1:
            edition = e
            break
    return edition

# %% ../nbs/01_config.ipynb 18
def find_dir_edition(stata_path=None):
    if stata_path is None:
        stata_path = _find_path()
    if not stata_path:
        raise OSError("Stata path not found.")
    stata_dir = str(os.path.dirname(stata_path))
    stata_exe = str(os.path.basename(stata_path)).lower()
    return stata_dir, _edition(stata_exe)

# %% ../nbs/01_config.ipynb 20
def find_edition(stata_dir):
    stata_path = _find_path(stata_dir)
    stata_exe = str(os.path.basename(stata_path)).lower()
    return _edition(stata_exe)

# %% ../nbs/01_config.ipynb 25
def set_pystata_path(stata_dir=None):
    if stata_dir is None:
        stata_dir, _ = find_dir_edition()
    if not os.path.isdir(stata_dir):
        raise OSError(f'Specified stata_dir, "{stata_dir}", is not a valid directory path')
    if not os.path.isdir(os.path.join(stata_dir, 'utilities')):
        raise OSError(f'Specified stata_dir, "{stata_dir}", is not Stata\'s installation path')
    sys.path.append(os.path.join(stata_dir, 'utilities'))

# %% ../nbs/01_config.ipynb 29
def launch_stata(stata_dir=None, edition=None, splash=True):
    """
    We modify stata_setup to make splash screen optional
    """
    if stata_dir is None:
        stata_dir, edition_found = find_dir_edition()
        edition = edition_found if edition is None else edition
    elif edition is None:
        edition = find_edition(stata_dir)
    set_pystata_path(stata_dir)
    import pystata
    try:
        if version.parse(pystata.__version__) >= version.parse("0.1.1"):
            # Splash message control is a new feature of pystata-0.1.1
            pystata.config.init(edition, splash=splash)
        else:
            pystata.config.init(edition)
    except FileNotFoundError as err:
        raise OSError(f'Specified edition, "{edition}", is not present at "{stata_dir}"')

# %% ../nbs/01_config.ipynb 35
def set_graph_format(gformat):
    import pystata
    if gformat == 'pystata':
        gformat = 'svg' # pystata default
    pystata.config.set_graph_format(gformat)

# %% ../nbs/01_config.ipynb 37
def _set_graph_size(width, height):
    import pystata
    pystata.config.set_graph_size(width, height)

# %% ../nbs/01_config.ipynb 41
def _get_config_settings(cpath):
    parser = configparser.ConfigParser(
        empty_lines_in_values=False,
        comment_prefixes=('*','//'),
        inline_comment_prefixes=('//',),
    )
    parser.read(str(cpath))
    return dict(parser.items('nbstata'))

# %% ../nbs/01_config.ipynb 42
def xdg_user_config_path():
    xdg_config_home = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config'))
    return xdg_config_home / 'nbstata/nbstata.conf'

def old_user_config_path():
    return Path('~/.nbstata.conf').expanduser()

# %% ../nbs/01_config.ipynb 45
class Config:
    "nbstata configuration"
    env = {'stata_dir': None,
           'edition': None,
           'splash': 'False',
           'graph_format': 'png',
           'graph_width': '5.5in',
           'graph_height': '4in',
           'echo': 'None',
           'missing': '.',
           'browse_auto_height': 'True',
          }
    valid_values_of = dict(
        edition={None, 'mp', 'se', 'be'},
        graph_format={'pystata', 'svg', 'png', 'pdf'},
        echo={'True', 'False', 'None'},
        splash={'True', 'False'},
        browse_auto_height={'True', 'False'},
    )
    
    @property
    def splash(self):
        return False if self.env['splash'] == 'False' else True
    
    @property
    def browse_auto_height(self):
        return False if self.env['browse_auto_height'] == 'False' else True
      
    @property
    def noecho(self):
        return self.env['echo'] == 'None'
    
    @property
    def echo(self):
        return self.env['echo'] == 'True'
    
    def display_status(self):
        import pystata
        pystata.config.status()
        print(f"""
      echo                   {self.env['echo']}
      missing                {self.env['missing']}
      browse_auto_height     {self.env['browse_auto_height']}
      config file path       {self.config_path}""")

    def __init__(self):
        """First check if a configuration file exists. If not, try `find_dir_edition`."""
        self.errors = []
        self._update_backup_graph_size()
        self.config_path = None

    def _update_backup_graph_size(self):
        self.backup_graph_size = {key: self.env[key] for key in {'graph_width', 'graph_height'}}
                
    def process_config_file(self):
        global_config_path = Path(os.path.join(sys.prefix, 'etc', 'nbstata.conf'))
        for cpath in (xdg_user_config_path(), old_user_config_path(), global_config_path):      
            if cpath.is_file():
                self._get_config_env(cpath)
                break
            
    def _get_config_env(self, cpath):
        try:
            settings = _get_config_settings(cpath)
        except configparser.Error as err:
            print_red(f"Configuration error in {cpath}:\n"
                      f"    {str(err)}")
        else:
            self.config_path = str(cpath)
            self.update(
                settings, 
                init=True, 
                error_header=f"Configuration errors in {self.config_path}:"  
            )
            
    def update(self, env, init=False, error_header="%set error(s):"):
        init_only_settings = {'stata_dir','edition','splash'}
        allowed_settings = self.env if init else set(self.env)-init_only_settings
        for key in list(env):
            if key not in allowed_settings:
                explanation = (
                    "is only allowed in a configuration file." if key in init_only_settings
                    else "is not a valid setting."
                )
                self.errors.append(f"    '{key}' {explanation}")
                env.pop(key)
            elif key in self.valid_values_of and env[key] not in self.valid_values_of[key]:
                self.errors.append(
                    f"    '{key}' configuration invalid: '{env[key]}' is not a valid value. "
                    f"Reverting to: {key} = {self.env[key]}"
                )
                env.pop(key)
        self._display_and_clear_update_errors(error_header)
        for key in set(env)-{'graph_width', 'graph_height'}:
            if not init: print(f"{key} was {self.env[key]}, is now {env[key]}")
        self.env.update(env)
  
    def _display_and_clear_update_errors(self, error_header):
        if self.errors:
            print_red(error_header)
        for message in self.errors:
            print_red(message)
        self.errors = []

# %% ../nbs/01_config.ipynb 53
@patch_to(Config)
def set_graph_size(self, init=False):
    try:
        _set_graph_size(self.env['graph_width'], self.env['graph_height'])
    except ValueError as err:
        self.env.update(self.backup_graph_size)
        print_red(f"Configuration error: {str(err)}. Graph size not changed.")
        if init: self.set_graph_size() # ensures set to definite measures rather than "default"
    else:
        if {key: self.env[key] for key in {'graph_width', 'graph_height'}} != self.backup_graph_size:
            if not init:
                print(f"graph size was ({self.backup_graph_size['graph_width']}, "
                      f"{self.backup_graph_size['graph_height']}), "
                      f"is now ({self.env['graph_width']}, {self.env['graph_height']}).")
            self._update_backup_graph_size()

# %% ../nbs/01_config.ipynb 59
@patch_to(Config)
def update_graph_config(self, init=False):
    graph_format = self.env['graph_format']
    if graph_format == 'pystata':
        graph_format = 'svg'
    set_graph_format(graph_format)
    self.set_graph_size(init)

# %% ../nbs/01_config.ipynb 61
@patch_to(Config)
def init_stata(self):
    launch_stata(self.env['stata_dir'],
                 self.env['edition'],
                 self.splash,
                )
    self.update_graph_config(init=True)
