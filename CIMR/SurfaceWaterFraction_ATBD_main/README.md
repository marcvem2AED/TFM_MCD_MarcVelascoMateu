# L2 Template

A template repo to host the ATBD and prototype software implementation for a Level-2 algorithm in the ESA-funded Level-2 Product and Algorithm Development project (CIMR L2PAD). The ATBD is prepared as a JupyterBook.

**DISCLAIMER: This repository is a template for testing and developing, it does not contain any valuable science.**

## Structure of the repo

Each L2 algorithm has its own GitHub repository, referenced from the [CIMR-L2PAD](https://github.com/CIMR-L2PAD) organization page.

In the repo we have (at least) these directories:
* `atbd/` (for the ATBD in JupyterBook format),
* `algorithm/` (for the software implementation),
* `notebooks/` (for jupyter notebooks that illustrate part of the algorithm),
* `data/` (for static data, e.g. calibration / validation data).
* `test/` (for software tests)

Convention: the main branch is called `main` (not `master`). `git config --global init.defaultBranch main`.

## Creating a new repo from the template
The `l2_template` repo is a _template repository_. It can be used to create a new repo for your L2 algorithm as a copy of the repo,
directly with the right structure and with initial file content. You can then work on your L2 book repo, this will not change the
template repository.

Follow these instructions to create a new repo from the template repo: [link](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template).

## Instructions to build the JupyterBook ATBD

### Fetch and read the book
If you just want to download the repo and read the book (not building it):
```
cd </path/to/where/you/want/the/repo> # call it /PATH/
git clone <repo>
```
In your web browser load `file:///PATH/atbd/_build/html/intro.html` in the url field.

## Instructions for building the book

### If needed, install miniconda or mamba
See https://docs.conda.io/en/latest/miniconda.html
See https://github.com/conda-forge/miniforge

### Create a conda environment and install the jupyter-book tools
```
conda create -c conda-forge --name JB python=3.11
conda activate JB
conda env list # check that JB is the current env.
```

### install packages needed for the atbd
```
conda install --file atbd/requirements.txt
```
You may add your needed packages to the `requirements.txt` file in the `atbd/` directory.

### build the book
```
cd /path/to/local/repo/with/atbd/ # the root of the repo, with atbd/ algorithm/ data/ ...
jupyter-book build atbd/
jupyter-book build --all atbd/ #(force rebuild everything)
```

### develop the book and commit to GitHub
Edit the `.md` files of the book
Build the book (see above)
```
git add <modified files>
git commit -m "commit message" 
git push
```

## Instructions for building a PDF of the book

Move to the `atbd/` subdirectory in your local directory, then:

```
make pdf
```

You need to install `pyppeteer`: `pip install pyppeteer`

## Instructions for publishing the book (with GitHub pages)

**This requires that the repository is public.**

We follow the instructions on the jupyterbook.org website: https://jupyterbook.org/en/stable/start/publish.html#

Install `ghp-import`:
```
conda install -c conda-forge ghp-import
```

Move to the `atbd/` subdirectory in your local directory.

Make sure the ATBD's HTML is freshly built
```
make
```

Remember to commit and push your edits to the `.md` and the `_build/` files (this pushes to `main` branch).

Run ghp-import
```
ghp-import -n -p -f _build/html
```

This will create a `gh-pages` branch (1st time) and push the new HTML pages to that branch (not `main`).

First time, visit "Settings / Pages" and check that it points at the `gh-pages` branch.

Your ATBD is hosted at https://cimr-l2pad.github.io/l2\_template

## Other Resources:
* [Setting up repos on GitHub](https://kbroman.org/github_tutorial/pages/init.html)
* [Put your JupyterBook on Github with online webpage (requires Public repo)](https://jupyterbook.org/en/stable/start/publish.html#)
