"""
Integration tests

Execution times for test cases will be reported to `test_exec_times.txt`
For detailed profiling, run `python -m cProfile test_realdata.py`.
"""

import numpy as np
import matplotlib.pyplot as plt
import os

from analysis.indus_waters import IndusWaters
from analysis.protein_order_params import OrderParams
from analysis.contacts import Contacts
from meta_analysis.profiling import timefuncfile, skipfunc

"""
INDUS waters analysis with sample data
"""

# Waters analysis
@timefuncfile("test_exec_times.txt")
def test_waters_noprobe():
    if not os.path.exists('waters_test_data'):
        os.makedirs('waters_test_data')

    waters = IndusWaters()
    waters.parse_args(['phiout.dat', '-obsstart', '500', '-obspref',
                       'waters_test_data/obsdata', '-window', '50', '-opref', 'waters_test_data/indus', '-oformat',
                       'png', '-dpi', '150', '--remote'])
    waters.read_args()
    waters()
    return True

# Waters analysis with generation of PDB
@timefuncfile("test_exec_times.txt")
def test_waters_pdb():
    if not os.path.exists('waters_test_data'):
        os.makedirs('waters_test_data')

    waters = IndusWaters()
    waters.parse_args(['phiout.dat', '-obsstart', '500', '-obspref',
                       'waters_test_data/obsdata', '-window', '50', '-opref', 'waters_test_data/indus', '-oformat',
                       'png', '-dpi', '150', '--remote',
                       '--genpdb', '-structf', 'indus.tpr', '-trajf', 'indus_mol_skip.xtc', '-radius', '6.0', '-skip', '50'])
    waters.read_args()
    waters()
    return True

"""
Protein order parameters analysis with actual data
"""
@timefuncfile("test_exec_times.txt")
def test_order_params():
    if not os.path.exists('order_params_test_data'):
        os.makedirs('order_params_test_data')

    op = OrderParams()
    op.parse_args(['indus.tpr', 'indus_mol_skip.xtc', '-opref', 'order_params_test_data/indus', '-oformat', 'png',
                   '-dpi', '150', '-align', 'backbone', '-select', 'backbone', '-window', '50',
                   '--remote'])
    op.read_args()
    op()
    return True

"""
Contacts analysis with actual data
"""

# 3res-sh method, with no PDB generation
@timefuncfile("test_exec_times.txt")
def test_contacts_3res_sh_nopdb():
    if not os.path.exists('contacts_test_data'):
        os.makedirs('contacts_test_data')

    cts = Contacts()
    cts.parse_args(['indus.tpr', 'indus_mol_skip.xtc', '-opref', 'contacts_test_data/indus', '-oformat', 'png',
                    '-method', '3res-sh',
                    '-dpi', '150', '-distcutoff', '4.5', '-skip', '20', '-bins', '50', '--remote'])
    cts.read_args()
    cts()

# 3res-sh method, with PDB generation
@timefuncfile("test_exec_times.txt")
def test_contacts_3res_sh_pdb():
    if not os.path.exists('contacts_test_data'):
        os.makedirs('contacts_test_data')

    cts = Contacts()
    cts.parse_args(['indus.tpr', 'indus_mol_skip.xtc', '-opref', 'contacts_test_data/indus', '-oformat', 'png',
                    '-method', '3res-sh',
                    '-dpi', '150', '-distcutoff', '4.5', '-skip', '20', '-bins', '50', '--remote',
                    '--genpdb'])
    cts.read_args()
    cts()

# 3res-sh method, replotting from saved data, with PDB generation
@timefuncfile("test_exec_times.txt")
def test_contacts_3res_sh_replot_pdb():
    if not os.path.exists('contacts_test_data'):
        os.makedirs('contacts_test_data')

    cts = Contacts()
    cts.parse_args(['indus.tpr', 'indus_mol_skip.xtc', '-opref', 'contacts_test_data/indus', '-oformat', 'png',
                    '-method', '3res-sh', '--replot', '-replotpref', 'contacts_test_data/indus',
                    '-dpi', '150', '-distcutoff', '4.5', '-skip', '20', '-bins', '50', '--remote',
                    '--genpdb'])
    cts.read_args()
    cts()

    return True

# atomic-sh method, with no PDB generation
@timefuncfile("test_exec_times.txt")
def test_contacts_atomic_sh_nopdb():
    if not os.path.exists('contacts_test_data'):
        os.makedirs('contacts_test_data')

    cts = Contacts()
    cts.parse_args(['indus.tpr', 'indus_mol_skip.xtc', '-opref', 'contacts_test_data/indus', '-oformat', 'png',
                    '-method', 'atomic-sh',
                    '-dpi', '150', '-distcutoff', '7', '-skip', '20', '-bins', '50', '--remote'])
    cts.read_args()
    cts()

# atomic-sh method, with PDB generation
@timefuncfile("test_exec_times.txt")
def test_contacts_atomic_sh_pdb():
    if not os.path.exists('contacts_test_data'):
        os.makedirs('contacts_test_data')

    cts = Contacts()
    cts.parse_args(['indus.tpr', 'indus_mol_skip.xtc', '-opref', 'contacts_test_data/indus', '-oformat', 'png',
                    '-method', 'atomic-sh',
                    '-dpi', '150', '-distcutoff', '7', '-skip', '5', '-bins', '50', '--remote',
                    '--genpdb'])
    cts.read_args()
    cts()

# atomic-sh method, replotting from saved data, with PDB generation
@timefuncfile("test_exec_times.txt")
def test_contacts_atomic_sh_replot_pdb():
    if not os.path.exists('contacts_test_data'):
        os.makedirs('contacts_test_data')

    cts = Contacts()
    cts.parse_args(['indus.tpr', 'indus_mol_skip.xtc', '-opref', 'contacts_test_data/indus', '-oformat', 'png',
                    '-method', 'atomic-sh', '--replot', '-replotpref', 'contacts_test_data/indus',
                    '-dpi', '150', '-distcutoff', '7', '-skip', '20', '-bins', '50', '--remote',
                    '--genpdb'])
    cts.read_args()
    cts()

    return True

if __name__=="__main__":
    test_waters_noprobe()
    test_waters_pdb()
    test_order_params()
    test_contacts_3res_sh_nopdb()
    test_contacts_3res_sh_pdb()
    test_contacts_3res_sh_replot_pdb()
    test_contacts_atomic_sh_nopdb()
    test_contacts_atomic_sh_pdb()
    test_contacts_atomic_sh_replot_pdb()
