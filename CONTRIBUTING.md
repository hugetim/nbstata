# How to contribute

This project is developed using [nbdev](https://nbdev.fast.ai/blog/posts/2022-07-28-nbdev2/#whats-nbdev), a way to create delightful software with Jupyter notebooks. The Python library and docs are automatically created from the notebooks in the `/nbs` directory.

## How to get started
Note: nbdev works on macOS, Linux, and most Unix-style operating systems. It works on Windows under [WSL](https://learn.microsoft.com/en-us/windows/wsl/setup/environment), but some features will not work under cmd or Powershell.

Follow the [install nbdev](https://nbdev.fast.ai/tutorials/tutorial.html#installation) instructions, specifically:

1. [Install jupyter notebook](https://nbdev.fast.ai/tutorials/tutorial.html#install-jupyter-notebook)
2. [Install nbdev](https://nbdev.fast.ai/tutorials/tutorial.html#install-nbdev)
3. [Install quarto](https://nbdev.fast.ai/tutorials/tutorial.html#install-quarto)
4. After cloning the repository, run this command inside it: [nbdev_install_hooks](https://nbdev.fast.ai/tutorials/modular_nbdev.html#jupyter-git-integration)
5. Run [nbdev_export](https://nbdev.fast.ai/tutorials/tutorial.html#install-quarto) inside the project directory
6. Run [pip install -e '.[dev]'](https://nbdev.fast.ai/tutorials/tutorial.html#install-your-package) inside the project directory

Visit [https://hugetim.github.io/nbstata/dev_docs_index.html](https://hugetim.github.io/nbstata/dev_docs_index.html) to get oriented.

## How to submit notebook PRs
After making changes to the `/nbs` notebooks, you should run [nbdev_prepare](https://nbdev.fast.ai/tutorials/tutorial.html#prepare-your-changes) and make any necessary changes in order to pass all the tests.

(You may also make limited changes directly to the `.py` files in the `/nbstata` folder, in which case you should sync those changes back to the notebooks with [nbdev_update](https://nbdev.fast.ai/api/sync.html).)

ReviewNB gives us visual diffs for notebooks and enables PR comments specific to a cell: https://app.reviewnb.com/hugetim/nbstata/ (free account needed to login)

## Do you want to contribute to the documentation?
* Docs are automatically created from the notebooks in the `/nbs` folder.
* You can preview the docs locally by running [nbdev_preview](https://nbdev.fast.ai/tutorials/tutorial.html#preview-your-docs). While in preview mode, you can make updates to notebooks and they will be reflected (after a small delay) in your browser.

## Specifics to be aware of
* The [@patch_to](https://fastcore.fast.ai/basics.html#patch_to) decorator is occasionally used to break up class definitions into separate cells.
