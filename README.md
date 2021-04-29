# Stochastic Service Composition

Implementation of stochastic service composition.
Paper:

[Brafman, R. I., De Giacomo, G., Mecella, M., & Sardina, S. 
(2017, November). Service Composition in Stochastic Settings. 
In Conference of the Italian Association for Artificial Intelligence 
(pp. 159-171). Springer, Cham.](http://www.diag.uniroma1.it/~degiacom/papers/2017/AIIA17bdms.pdf)

## Preliminaries

- Set up the virtual environment. 
First, install [Pipenv](https://pipenv-fork.readthedocs.io/en/latest/).
Then:
```
pipenv install --dev
```

- Install the Python package in development mode:
```
pip install -e .
# alternatively:
# python setup.py develop 
```

- To use rendering functionalities, you will also need to install Graphviz. 
  At [this page](https://www.graphviz.org/download/) you will
  find the releases for all the supported platform.


## Notebooks

To run the notebooks:

```
PYTHONPATH="$(pwd)" jupyter-notebook
```

And then go to `examples/notebooks`.

## Tests

To run tests: `tox`

To run only the code tests: `tox -e py3.7`

To run only the linters: 
- `tox -e flake8`
- `tox -e mypy`
- `tox -e black-check`
- `tox -e isort-check`

Please look at the `tox.ini` file for the full list of supported commands. 
