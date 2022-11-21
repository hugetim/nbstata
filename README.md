
::: {.cell 0=‘h’ 1=‘i’ 2=‘d’ 3=‘e’}

``` python
from nbstata.helpers import *
```

:::

# nbstata

> Jupyter kernel for Stata based on pystata

Requires Stata 17 or above because it uses
[pystata](https://www.stata.com/python/pystata/). Consider
[stata_kernel](https://github.com/kylebarron/stata_kernel) instead if
you have an older version of Stata.

## Install

To install, run:

``` sh
pip install nbstata
python -m nbstata.install [--sys-prefix] [--prefix] [--conf-file]
```

Include `--sys-prefix` if you are installing `nbstata` in a multi-user
environment, or `--prefix` if you want to specify a path yourself.

At runtime, `nbstata` will try to determine the location of your Stata
installation. You can create a configuration file to preempt this
detection with the `--conf-file` option. Even if you do not include this
option, the configuration file will still be created if the installer
cannot find any Stata installation.

The location of the configuration file is:

- `[prefix]/etc/nbstata.conf` if `--sys-prefix` or `--prefix` is
  specified.
- `~/.nbstata.conf` otherwise.

If a configuration file exists in both locations, the user version takes
precedence.

Syntax highlighting is the same as `stata_kernel`:

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
- `echo`: controls the echo of commands:
  - ‘True’: the kernel will echo all commands.
  - ‘False’: the kernel will not echo single-line commands.
  - ‘None’: the kernel will not echo any command.

  Default is ‘None’.
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

#### Default Graph Format

Both `pystata` and `stata_kernel` default to the SVG image format.
`nbstata` defaults to the PNG image format instead for several reasons:

- Jupyter does not show SVG images from untrusted notebooks ([link
  1](https://stackoverflow.com/questions/68398033/svg-figures-hidden-in-jupyterlab-after-some-time)).
- Notebooks with empty cells are untrusted ([link
  2](https://github.com/jupyterlab/jupyterlab/issues/9765)).
- SVG images cannot be copied and pasted directly into Word or
  PowerPoint.

### Magics

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
| `*%noecho`  | Suppress echo in current cell         | `*%noecho`                              |
| `*%quietly` | Suppress all output from current cell | `*%quietly`                             |

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
