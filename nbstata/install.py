import argparse
import json
import os
import sys

from jupyter_client.kernelspec import KernelSpecManager
from IPython.utils.tempdir import TemporaryDirectory
from pkg_resources import resource_filename
from shutil import copyfile
from pathlib import Path
from textwrap import dedent



kernel_json = {
    "argv": [sys.executable, "-m", "nbstata", "-f", "{connection_file}"],
    "display_name": "Stata (nbstata)",
    "language": "stata",
}

def install_my_kernel_spec(user=True, prefix=None):
    with TemporaryDirectory() as td:
        os.chmod(td, 0o755) # Starts off as 700, not user readable
        with open(os.path.join(td, 'kernel.json'), 'w') as f:
            json.dump(kernel_json, f, sort_keys=True)

        # Copy logo to tempdir to be installed with kernelspec
        logo_path = resource_filename('nbstata', 'logo-64x64.png')
        copyfile(logo_path, os.path.join(td, 'logo-64x64.png'))

        print('Installing Jupyter kernel spec')
        KernelSpecManager().install_kernel_spec(td, 'nbstata', user=user, prefix=prefix)

def install_conf(conf_file,gen_file=False):
    """
    From stata_kernel, but the conf here is much simplier.
    """

    # By avoiding an import of .config until we need it, we can
    # complete the installation process in virtual environments
    # without needing this submodule nor its downstream imports.
    from .config import find_dir_edition
    stata_dir,stata_ed = find_dir_edition()
    if not stata_dir:
        gen_file = True
        msg = """\
            WARNING: Could not find Stata path.
            Please specify it manually in configuration file.
            """
        print(dedent(msg))

    conf_default = dedent(
        """\
    [nbstata]
    stata_dir = {}
    edition = {}
    graph_format = png
    echo = None
    splash = False
    """.format(stata_dir,stata_ed))

    if gen_file:
        print("Creating configuration file at:")
        print(str(conf_file))
        try:
            with conf_file.open('w') as f:
                f.write(conf_default)
            print("Success!")
        except:
            print("Failed!")

def _is_root():
    try:
        return os.geteuid() == 0
    except AttributeError:
        return False # assume not an admin on non-Unix platforms

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--user', action='store_true',
        help="Install to the per-user kernels registry. Default if not root.")
    ap.add_argument('--sys-prefix', action='store_true',
        help="Install to sys.prefix (e.g. a virtualenv or conda env)")
    ap.add_argument('--prefix',
        help="Install to the given prefix. "
             "Kernelspec will be installed in {PREFIX}/share/jupyter/kernels/")
    ap.add_argument(
        '--conf-file', action='store_true',
        help="Create a configuration file.")
    args = ap.parse_args(argv)

    if args.sys_prefix:
        args.prefix = sys.prefix
    if not args.prefix and not _is_root():
        args.user = True

    install_my_kernel_spec(user=args.user, prefix=args.prefix)
    if args.user:
        conf_file = Path('~/.nbstata.conf').expanduser()
    else:
        conf_dir = os.path.join(args.prefix,'etc')
        if not Path(os.path.join(args.prefix,'etc')).is_dir():
            os.mkdir(conf_dir)
        conf_file = Path(os.path.join(conf_dir,'nbstata.conf'))
    if not conf_file.is_file():
        install_conf(conf_file,args.conf_file)

if __name__ == '__main__':
    main()
