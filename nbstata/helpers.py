# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/01_helpers.ipynb.

# %% auto 0
__all__ = ['launch_stata']

# %% ../nbs/01_helpers.ipynb 3
from . import config
from packaging import version

# %% ../nbs/01_helpers.ipynb 4
def launch_stata(path=None, edition=None, splash=True):
    """
    We modify stata_setup to make splash screen optional
    """
    if path == None or edition == None:
        path_found, edition_found = config.find_dir_edition()
        path = path_found if path==None else path
        edition = edition_found if edition==None else edition
    config.set_pystata_path(path)
    import pystata
    if version.parse(pystata.__version__) >= version.parse("0.1.1"):
        # Splash message control is a new feature of pystata-0.1.1
        pystata.config.init(edition,splash=splash)
    else:
        pystata.config.init(edition)
