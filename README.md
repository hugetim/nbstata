Welcome to nbstata
================

<!-- WARNING: THIS FILE WAS AUTOGENERATED! DO NOT EDIT! -->

*[Click here for the nbstata User
Guide](https://hugetim.github.io/nbstata/user_guide.html)*

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

<img align="center" width="650" src="https://github.com/kylebarron/stata_kernel/raw/master/docs/src/img/jupyter_notebook_example.gif">

### `nbstata` features

- [x] [Easy
  setup](https://hugetim.github.io/nbstata/user_guide.html#install)
- [x] Works with Stata 17 (only).
- [x] Displays Stata output without the redundant ‘echo’ of (multi-line)
  commands
- [x] Autocompletion for variables, macros, matrices, and file paths
- [x] DataGrid widget with `browse`-like capabilities (e.g., interactive
  filtering)
- [x] Variable and data properties (`describe` and `e`/`return list`)
  available in a ‘contextual help’ side panel
- [x] Interactive/richtext help files accessible within notebook
- [x] `#delimit ;` interactive support (along with all types of
  comments)

### What can you do with Stata notebooks…

…that you can’t do with the [official Stata
interface](https://www.stata.com/features/overview/graphical-user-interface/)?

- Exploratory analysis that is both:
  - interactive
  - preserved for future reference/editing
- Present results in a way that interweaves:\[1\]
  - code
  - results (including graphs)
  - rich text:
    1.  lists
    2.  **Headings**
    3.  <img align="left" width="54" height="18.6" src="index_files/figure-commonmark/766814e4-1-image-2.png">
    4.  [links](https://hugetim.github.io/nbstata/)
    5.  math: $y_{it}=\beta_0+\varepsilon_{it}$

\[1\] Stata [dynamic
documents](https://www.stata.com/manuals/rptdynamicdocumentsintro.pdf)
can do this part, but with a very different, less interactive workflow.
(See also: [markstat](https://grodri.github.io/markstat/),
[stmd](https://www.ssc.wisc.edu/~hemken/Stataworkshops/stmd/Usage/stmdusage.html),
and
[Statamarkdown](https://ssc.wisc.edu/~hemken/Stataworkshops/Statamarkdown/stata-and-r-markdown.html))

## Contributing

`nbstata` is being developed using
[nbdev](https://nbdev.fast.ai/blog/posts/2022-07-28-nbdev2/#whats-nbdev).
The `/nbs` directory is where edits to the source code should be made.
(The python code is then exported to the `/nbdev` library folder.) The
one exception is `install.py`.

The [@patch_to](https://fastcore.fast.ai/basics.html#patch_to) decorator
is occasionally used to break up class definitions into separate cells.

For more, see
[CONTRIBUTING.md](https://github.com/hugetim/nbstata/blob/master/CONTRIBUTING.md).

## Acknowledgements

Kyle Barron authored the original `stata_kernel` and Vinci Chow carried
that work forward for Stata 17, converting the backend to use
[pystata](https://www.stata.com/python/pystata/). `nbstata` was
originally derived from his
[pystata-kernel](https://github.com/ticoneva/pystata-kernel), but much
of the docs and newer features are derived directly from `stata_kernel`.
