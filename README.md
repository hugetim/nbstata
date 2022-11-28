nbstata
================

<!-- WARNING: THIS FILE WAS AUTOGENERATED! DO NOT EDIT! -->

Because it uses [pystata](https://www.stata.com/python/pystata/) under
the hood, `nbstata` requires Stata 17 to be installed locally. (If you
have an older version of Stata, consider
[stata_kernel](https://github.com/kylebarron/stata_kernel) instead.)

## Install

To install, run:

``` sh
pip install nbstata
python -m nbstata.install [--sys-prefix] [--prefix PREFIX] [--conf-file]
```

Include `--sys-prefix` to install to `sys.prefix` (e.g. a virtualenv or
conda env), or `--prefix PREFIX` if you want to specify the install path
yourself.

### Configuration file

The `--conf-file` option creates a configuration file for you. (Note: If
the installer cannot find the location of your Stata installation, a
configuration file will be created even if you do not include the
`--conf-file` option to allow you to manually specify the Stata
location.) The location of the configuration file will be:

- `[prefix]/etc/nbstata.conf` if `--sys-prefix` or `--prefix` is
  specified.
- `~/.nbstata.conf` otherwise.

(Note: If a configuration file exists in both locations at kernel
runtime, the user version takes precedence.)

### Syntax highlighting

Stata syntax highlighting can be installed for Jupyter Lab ([just as for
stata_kernel](https://kylebarron.dev/stata_kernel/getting_started/#jupyter)):

``` sh
conda install nodejs -c conda-forge --repodata-fn=repodata.json
jupyter labextension install jupyterlab-stata-highlight
```

## Configuration

The following settings are permitted inside the configuration file:

- `stata_dir`: Stata installation directory.
- `edition`: Stata edition. Acceptable values are ‘be’, ‘se’ and ‘mp’.
  Default is ‘be’.
- `graph_format`: Graph format. Acceptable values are ‘png’, ‘pdf’,
  ‘svg’ and ‘pystata’. Specify the last option if you want to use
  `nbstata`‘s setting. Default is ’png’.
- `echo`: controls the echo of commands, with the default being ‘None’:
  - ‘True’: the kernel will echo all commands.
  - ‘False’: the kernel will not echo single-line commands.
  - ‘None’: the kernel will not echo any command.
- `splash`: controls display of the splash message during Stata startup.
  Default is ‘False’.
- `missing`: What should be displayed in the output of the `*%browse`
  magic for a missing value. Default is ‘.’, following Stata. To defer
  to pandas’ format for `NA`, specify ‘pandas’.

Settings must be under the title `[nbstata]`. Example:

    [nbstata]
    stata_dir = /opt/stata
    edition = mp
    graph_format = svg
    echo = True
    splash = False
    missing = NA

### Default Graph Format

Both `pystata` and `stata_kernel` default to the SVG image format.
`nbstata` defaults to the PNG image format instead for several reasons:

- Jupyter does not show SVG images from untrusted notebooks ([link
  1](https://stackoverflow.com/questions/68398033/svg-figures-hidden-in-jupyterlab-after-some-time)).
- Notebooks with empty cells are untrusted ([link
  2](https://github.com/jupyterlab/jupyterlab/issues/9765)).
- SVG images cannot be copied and pasted directly into Word or
  PowerPoint.

## Magics

Magics are commands that only work in `nbstata` and are not part of
Stata’s syntax. Magics normally start with `%`, but this will cause
errors when the notebook is exported and run as a Stata script. As an
alternative, you can prefix the magic name with `*%`, which will simply
be treated by Stata as a single-line comment.

`nbstata` currently supports the following magics:

| Magic       | Description                           | Full Syntax                             |
|:------------|:--------------------------------------|:----------------------------------------|
| `*%browse`  | View dataset                          | `*%browse [-h] [N] [varlist] [if] [in]` |
| `*%help`    | Display a help file in rich text      | `*%help [-h] command_or_topic_name`     |
| `*%echo`    | Ensure echo in current cell           | `*%echo`                                |
| `*%noecho`  | Suppress echo in current cell         | `*%noecho`                              |
| `*%quietly` | Suppress all output from current cell | `*%quietly`                             |

## Stata Implementation Details

### \#delimit behavior

A [`#delimit;`](https://www.stata.com/manuals/pdelimit.pdf) command in
one cell will persist into other cells, until `#delimit cr` is called.
For example, see [delimit
tests.ipynb](https://github.com/hugetim/nbstata/blob/master/manual_test_nbs/delimit%20tests.ipynb).
(If anyone desires each cell to instead be treated as a separate .do
file, so that every cell defaults to `#delimit cr` at the start, please
raise an Issue to request this as a configuration option.)

## Contributing

`nbstata` is being developed using [nbdev](https://nbdev.fast.ai/). The
`/nbs` directory is where edits to the source code should be made. (The
python code is then exported to the `/nbdev` library folder.) The one
exception is `install.py`.

The [@patch_to](https://fastcore.fast.ai/basics.html#patch_to) decorator
is occasionally used to break up class definitions into separate cells.

For more, see
[CONTRIBUTING.md](https://github.com/hugetim/nbstata/blob/master/CONTRIBUTING.md).

## Acknowledgements

Kyle Barron authored the original `stata_kernel` and Vinci Chow carried
that work forward for Stata 17, converting the backend to use
[pystata](https://www.stata.com/python/pystata/). `nbstata` is directly
derived from his
[pystata-kernel](https://github.com/ticoneva/pystata-kernel).
