nbstata
================

<!-- WARNING: THIS FILE WAS AUTOGENERATED! DO NOT EDIT! -->

## What is Jupyter?

[JupyterLab](https://jupyterlab.readthedocs.io/en/stable/getting_started/overview.html)
is a browser-based editor that allows you to combine interactive code
and results with
[Markdown](https://daringfireball.net/projects/markdown/basics) in a
single document (called a Jupyter notebook). It is open source and
widely used. Though it is named after the three core programming
languages it supports (Julia, Python, and R), it can be used with with a
wide variety of languages.

`nbstata` allows you to create Stata notebooks (as opposed to using
Stata within a *Python* notebook, which is a nice way to [embed Stata
commands within Python
code](https://www.stata.com/python/pystata/notebook/Example2.html) but
is needlessly clunky if you are working primarily with Stata).

<img align="center" width="650" src="https://github.com/hugetim/nbstata/raw/master/nbs/jupyter_notebook_example.gif">

### `nbstata` features

- [x] Works with Stata 17 (only).
- [x] Autocompletion for variables, macros, matrices, and file paths.
- [x] DataGrid widget with `browse`-like capabilities (e.g., interactive
  filtering).
- [x] Variable and data properties (`describe` and
  `return`/`ereturn list`) available in a side panel.
- [x] Interactive help files available within notebook.
- [x] `#delimit ;` interactive support (along with all types of
  comments).
- [ ] Mata interactive support.

### What do Stata notebooks allow that the official Stata IDE doesn’t?

- Exploratory analysis that is both:
  - interactive
  - preserved for future reference/editing
- Presenting results in a way that interweaves:
  - code
  - results (including graphs)
  - rich text:
    1.  lists
    2.  **Headings**
    3.  <img align="left" width="54" height="18.6" src="index_files/figure-commonmark/69ff5bcb-1-image-2.png">
    4.  [links](https://hugetim.github.io/nbstata/)
    5.  math: $y_{it}=\beta_0+\varepsilon_{it}$

## Install

*Because it uses [pystata](https://www.stata.com/python/pystata/) under
the hood, `nbstata` requires Stata 17 to be installed locally. (If you
have an older version of Stata, consider
[stata_kernel](https://github.com/kylebarron/stata_kernel) instead.)*

To install `nbstata`, run:

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

### Updating

To update from a previous version of `nbstata`, run:

``` sh
pip install nbstata --upgrade
```

When updating, you don’t have to run `python -m nbstata.install` again.

### Syntax highlighting

Stata syntax highlighting can be installed for Jupyter Lab:

``` sh
pip install jupyterlab_stata_highlight2
```

## Configuration

The following settings are permitted inside the configuration file:

- `stata_dir`: Stata installation directory.
- `edition`: Stata edition. Acceptable values are ‘be’, ‘se’ and ‘mp’.
  Default is ‘be’.
- `graph_format`: Acceptable values are ‘png’ (the default), ‘pdf’,
  ‘svg’ and ‘pystata’. Specify the last option if you want to use
  `pystata`’s [default
  setting](https://www.stata.com/python/pystata/config.html#pystata.config.set_graph_format).
- `echo`: controls the echo of commands, with the default being ‘None’:
  - ‘True’: the kernel will echo all commands.
  - ‘False’: the kernel will not echo single-line commands.
  - ‘None’: the kernel will not echo any command.
- `splash`: controls display of the splash message during Stata startup.
  Default is ‘False’.
- `missing`: What should be displayed in the output of the `*%head` and
  `*%tail` magics for a missing value. Default is ‘.’, following Stata.
  To defer to pandas’ format for `NA`, specify ‘pandas’.

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
alternative, you may prefix the magic name with `*%`, which will then be
treated by Stata as a single-line comment.

`nbstata` currently supports the following magics:

| Magic      | Description                   | Full Syntax                                              |
|:-----------|:------------------------------|:---------------------------------------------------------|
| \*%browse  | Interactively view dataset    | `*%browse [-h] [varlist] [if] [in] [, nolabel noformat]` |
| \*%head    | View first 5 (or N) rows      | `*%head [-h] [N] [varlist] [if] [, nolabel noformat]`    |
| \*%tail    | View last 5 (or N) rows       | `*%tail [-h] [N] [varlist] [if] [, nolabel noformat]`    |
| \*%locals  | List locals with their values | `*%locals`                                               |
| \*%delimit | Print the current delimiter   | `*%delimit`                                              |
| \*%help    | Display Stata help            | `*%help [-h] command_or_topic_name`                      |
| \*%echo    | Ensure echo from cell         | `*%echo`                                                 |
| \*%noecho  | Suppress echo from cell       | `*%noecho`                                               |
| \*%quietly | Suppress all output from cell | `*%quietly`                                              |

The `%browse` magic requires JupyterLab with the
`@finos/perspective-jupyterlab` extension [correctly
installed](https://perspective.finos.org/docs/python/#jupyterlab).

By default, the `%browse`, `%head`, and `%tail` magics convert numeric
Stata values to strings using their Stata format (or value labels). To
prevent this behavior, specify the `noformat` and/or `nolabel` options.

## Stata Implementation Details

### \#delimit behavior

A [`#delimit;`](https://www.stata.com/manuals/pdelimit.pdf) command in
one cell will persist into other cells, until `#delimit cr` is called.
For example, see [delimit
tests.ipynb](https://github.com/hugetim/nbstata/blob/master/manual_test_nbs/delimit%20tests.ipynb).

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
