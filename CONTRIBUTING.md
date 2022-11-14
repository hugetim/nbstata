# How to contribute

This project is developed using [nbdev](https://nbdev.fast.ai/), a way to create delightful software with Jupyter notebooks. The Python library and docs are automatically created from the notebooks in the `/nbs` directory.

## How to get started
Before anything else, please install the git hooks that run automatic scripts during each commit and merge to strip the notebooks of superfluous metadata (and avoid merge conflicts). After cloning the repository, run this command inside it: [nbdev_install_hooks](https://nbdev.fast.ai/tutorials/modular_nbdev.html#jupyter-git-integration)

## How to submit notebook PRs
After making changes to the `/nbs` notebooks, you should run [nbdev_prepare](https://nbdev.fast.ai/tutorials/tutorial.html#prepare-your-changes) and make any necessary changes in order to pass all the tests.

(You may also make limited changes directly to the `.py` files in the `/nbstata` folder, in which case you should sync those changes back to the notebooks with [nbdev_update](https://nbdev.fast.ai/api/sync.html).)

## Do you want to contribute to the documentation?
* Docs are automatically created from the notebooks in the `/nbs` folder.
* You can preview the docs locally by running [nbdev_preview](https://nbdev.fast.ai/tutorials/tutorial.html#preview-your-docs). While in preview mode, you can make updates to notebooks and they will be reflected (after a small delay) in your browser.
