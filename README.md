# Stochastic Service Composition

Implementation of Digital Twins Composition in Smart Manufacturing via Markov Decision Processes.

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

To run the notebooks, activate the virtual environment. Then:

```
jupyter-notebook
```

Then via the browser go to `docs/notebooks` to open the notebooks.

## Digital Twins

The folder `digital_twins` contains the integration of the 
stochastic service composition with the Bosch IoT Things platform.

To run the examples, go to the terminal and set:
```
export PYTHONPATH=".:$PYTHONPATH"
```

Then, run:
```
python digital_twins/main.py --config digital_twins/config.json
```

## Tests

To run tests: `tox`

To run only the code tests: `tox -e py3.7`

To run only the linters: 
- `tox -e flake8`
- `tox -e mypy`
- `tox -e black-check`
- `tox -e isort-check`

Please look at the `tox.ini` file for the full list of supported commands. 

## Docs

To build the docs: `mkdocs build`

To view documentation in a browser: `mkdocs serve`
and then go to [http://localhost:8000](http://localhost:8000)

## License

`stochastic_service_composition` is released under the MIT license.

Copyright 2021 Luciana Silo
