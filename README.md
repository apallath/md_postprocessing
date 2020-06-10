# Analysis package for simulation data obtained using GROMACS implementation of Dynamic INDUS

[![Python](https://img.shields.io/github/languages/top/apallath/analysis_scripts)](https://www.python.org/downloads/release/python-370/)
[![Actions Status](https://img.shields.io/github/workflow/status/apallath/analysis_scripts/Analysis)](https://github.com/apallath/analysis_scripts/actions)

[![Open Issues](https://img.shields.io/github/issues-raw/apallath/analysis_scripts)](https://github.com/apallath/analysis_scripts/issues)
[![Closed Issues](https://img.shields.io/github/issues-closed-raw/apallath/analysis_scripts)](https://github.com/apallath/analysis_scripts/issues)

## Features (v0.2)
- Uses Cython for improved performance (still under development)
- New program call structure

## Installation

1. Install requirements
`pip install -r requirements.txt`

2. Build C extensions
`python setup.py build_ext --inplace`

2. Install package [in editable state]
`pip install .`

## Usage

The analysis package can be imported in any Python script using

`import analysis`

The meta_analysis package, which implements functions for profling/performance
analysis of the analysis package, can be imported using

`import meta_analysis`

To run an analysis from the command line, call
`python /path/to/analysis_scripts/run_<analysis_name>.py`
with the required arguments

## Testing

Run both unit tests and integration tests to make sure the package is installed
and working correctly. Ideally, all tests should pass.

### Integration tests:

Run integration tests in this folder by running
`pytest`
inside the folder `tests_integration/`.

### Unit tests:

Run unit tests in this folder by running
`pytest`
inside the folder `tests_unit/`.
