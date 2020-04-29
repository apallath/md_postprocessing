# Analysis scripts for MD simulation post processing.

Install in editable state using pip:

`pip install -e .`

## Core analysis package:
`analysis/`

The analysis package can be imported in any Python script using

`import analysis`

The analysis scripts are executable with command line arguments.

`python /path/to/script/ --help`
will list out the required and optional arguments for each script.

### Usage examples

`python /path/to/analysis_scripts/analysis/indus_waters.py phiout.dat \
    -opref current -apref previous -oformat png -dpi 150 -window 1000 \
    -aprevlegend "Previous run" -acurlegend "Current run" \
    --remote`

`python /path/to/analysis_scripts/analysis/protein_order_params.py conf.gro traj.xtc \
    -reftrajf traj.xtc -reftstep 0 -opref current -apref previous -oformat png -dpi 150 \
    -align backbone -select backbone -window 50 \
    -aprevlegend "Previous run" -acurlegend "Current run" \
    --remote`

`python /path/to/analysis_scripts/analysis/contacts.py conf.gro traj.xtc \
    -opref current -apref previous -oformat png -dpi 150 \
    -aprevlegend "Previous run" -acurlegend "Current run" \
    --verbose --remote`

## Tests:
`tests/`

Run tests in this folder by running
`pytest`
inside the folder. Ideally, all tests should pass.

## Other components:
Scratch Jupyter notebooks:
`scratch/`
